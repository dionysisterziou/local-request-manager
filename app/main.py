from fastapi import FastAPI, Form, Request
from fastapi.templating import Jinja2Templates

app = FastAPI()
templates = Jinja2Templates(directory="templates")


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
    return templates.TemplateResponse(
        request=request,
        name="request_success.html",
        context={"customer_name": customer_name},
    )