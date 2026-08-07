import os
import secrets
from pathlib import Path

from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

from app.database import (
    get_all_requests,
    get_request_by_id,
    init_database,
    save_request,
    update_request_status,
)

BASE_DIR = Path(__file__).resolve().parent.parent
ALLOWED_STATUSES = ("new", "in_progress", "completed", "rejected")

ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD")
SESSION_SECRET = os.environ.get("SESSION_SECRET")

if not ADMIN_PASSWORD:
    raise RuntimeError("ADMIN_PASSWORD environment variable is required")

if not SESSION_SECRET:
    raise RuntimeError("SESSION_SECRET environment variable is required")

app = FastAPI()

app.add_middleware(
    SessionMiddleware,
    secret_key=SESSION_SECRET,
    session_cookie="admin_session",
    max_age=60 * 60,
    same_site="lax",
    https_only=False,
)

app.mount(
    "/static",
    StaticFiles(directory=str(BASE_DIR / "static")),
    name="static",
)

templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

init_database()


def validate_request_form(
    customer_name: str,
    customer_phone: str,
    customer_email: str,
    message: str,
):
    cleaned_data = {
        "customer_name": customer_name.strip(),
        "customer_phone": customer_phone.strip(),
        "customer_email": customer_email.strip(),
        "message": message.strip(),
    }

    errors = {}

    required_fields = {
        "customer_name": "Customer name is required.",
        "customer_phone": "Customer phone is required.",
        "message": "Message is required.",
    }

    for field, error_message in required_fields.items():
        if not cleaned_data[field]:
            errors[field] = error_message

    return cleaned_data, errors


def get_admin_redirect_if_unauthorized(request: Request):
    if request.session.get("is_admin") is not True:
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
        name="request_form.html",
        context={
            "form_data": {},
            "errors": {},
        },
    )


@app.post("/requests")
def create_request(
    request: Request,
    customer_name: str = Form(...),
    customer_phone: str = Form(...),
    customer_email: str = Form(""),
    message: str = Form(...),
):
    cleaned_data, errors = validate_request_form(
        customer_name,
        customer_phone,
        customer_email,
        message,
    )

    if errors:
        return templates.TemplateResponse(
            request=request,
            name="request_form.html",
            context={
                "form_data": cleaned_data,
                "errors": errors,
            },
            status_code=400,
        )

    request_id = save_request(
        customer_name=cleaned_data["customer_name"],
        customer_phone=cleaned_data["customer_phone"],
        customer_email=cleaned_data["customer_email"],
        message=cleaned_data["message"],
    )

    return templates.TemplateResponse(
        request=request,
        name="request_success.html",
        context={
            "customer_name": cleaned_data["customer_name"],
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
    if not secrets.compare_digest(
        password.encode("utf-8"), ADMIN_PASSWORD.encode("utf-8")
    ):
        return templates.TemplateResponse(
            request=request,
            name="admin_login.html",
            context={"error": "Invalid admin password"},
            status_code=401,
        )

    request.session["is_admin"] = True

    return RedirectResponse(
        url="/admin/requests",
        status_code=303,
    )


@app.post("/admin/logout")
def admin_logout(request: Request):
    request.session.clear()

    return RedirectResponse(
        url="/admin/login",
        status_code=303,
    )


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
