from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def home():
    return {"message": "Local Request Manager is running"}