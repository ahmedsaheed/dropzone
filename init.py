
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import google.oauth2.id_token
from google.auth.transport import requests


app = FastAPI()

firebase_request_adapter = requests.Request()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    id_token = request.cookies.get("token")
    error_message = "No error here"
    user_token = None

    if id_token:
        try:
            user_token = google.oauth2.id_token.verify_firebase_token(
                id_token, firebase_request_adapter
            )
        except ValueError as err:
            print(str(err))
    return templates.TemplateResponse('main.html', {'request': request, 'user_token': user_token, 'error_message': error_message})
