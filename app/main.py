import os
import secrets
from pathlib import Path

from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.database import (
    get_all_requests,
    get_request_by_id,
    init_database, 
    save_request,
    update_request_status,
)

app = FastAPI()
BASE_DIR = Path(__file__).resolve().parent.parent
app.mount(
    "/static", 
    StaticFiles(directory=str(BASE_DIR / "static")), 
    name="static",
)

templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
ALLOWED_STATUSES = ("new", "in_progress", "completed", "rejected")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD")
ADMIN_SESSION_TOKEN = secrets.token_urlsafe(32)

if ADMIN_PASSWORD is None:
    raise RuntimeError("ADMIN_PASSWORD environment variable is required")

init_database()


def get_admin_redirect_if_unauthorized(request: Request):
    admin_session = request.cookies.get("admin_session")

    if admin_session != ADMIN_SESSION_TOKEN:
        return RedirectResponse(
            url="/admin/login",
            status_code=303,
        )
    
    return None


@app.get("/")
def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
    )


@app.get("/requests/new")
def new_request_form(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="request_form.html"
    )


@app.post("/requests")
def create_request(
    request: Request,
    customer_name: str = Form(...),
    customer_phone: str = Form(...),
    customer_email: str = Form(""),
    message: str = Form(...),
):
    request_id = save_request(
        customer_name=customer_name,
        customer_phone=customer_phone,
        customer_email=customer_email,
        message=message,
    )

    return templates.TemplateResponse(
        request=request,
        name="request_success.html",
        context={
            "customer_name": customer_name,
            "request_id": request_id,
        },
    )


@app.get("/admin/login")
def admin_login_form(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="admin_login.html",
        context={"error": None},
    )


@app.post("/admin/login")
def admin_login(
    request: Request,
    password: str = Form(...),
):
    if not secrets.compare_digest(password, ADMIN_PASSWORD):
        return templates.TemplateResponse(
            request=request,
            name="admin_login.html",
            context={"error": "Invalid admin password"},
            status_code=401,
        )
    
    response = RedirectResponse(
        url="/admin/requests",
        status_code=303,
    )
    response.set_cookie(
        key="admin_session",
        value=ADMIN_SESSION_TOKEN,
        httponly=True,
        samesite="lax",
    )

    return response


@app.post("/admin/logout")
def admin_logout():
    response = RedirectResponse(
        url="/admin/login",
        status_code=303,
    )
    response.delete_cookie("admin_session")

    return response


@app.get("/admin/requests")
def admin_requests(request: Request):
    auth_redirect = get_admin_redirect_if_unauthorized(request)

    if auth_redirect is not None:
        return auth_redirect

    requests = get_all_requests()

    return templates.TemplateResponse(
        request=request,
        name="admin_requests.html",
        context={
            "requests": requests,
            "allowed_statuses": ALLOWED_STATUSES,
        },
    )


@app.get("/admin/requests/{request_id}")
def admin_request_detail(request: Request, request_id: int):
    auth_redirect = get_admin_redirect_if_unauthorized(request)

    if auth_redirect is not None:
        return auth_redirect

    customer_request = get_request_by_id(request_id)

    if customer_request is None:
        raise HTTPException(status_code=404, detail="Request not found")
    
    return templates.TemplateResponse(
        request=request,
        name="admin_request_detail.html",
        context={"customer_request": customer_request},
    )


@app.post("/admin/requests/{request_id}/status")
def change_request_status(
    request: Request,
    request_id: int,
    status: str = Form(...),
):
    auth_redirect = get_admin_redirect_if_unauthorized(request)

    if auth_redirect is not None:
        return auth_redirect

    if status not in ALLOWED_STATUSES:
        raise HTTPException(status_code=400, detail="Invalid status")
    
    updated_rows = update_request_status(
        request_id=request_id,
        status=status,
    )

    if updated_rows == 0:
        raise HTTPException(status_code=404, detail="Request not found")
    
    return RedirectResponse(
        url="/admin/requests",
        status_code=303,
    )