from pathlib import Path

from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

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

init_database()


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


@app.get("/admin/requests")
def admin_requests(request: Request):
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
    request_id: int,
    status: str = Form(...),
):
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