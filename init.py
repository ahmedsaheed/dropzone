from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from scripts.utils import extract_relative_path
import starlette.status as status
from scripts.blobs import blob_list, download_blob
from scripts.directory import add_directory
from scripts.file import add_file, delete_file
from scripts.login import get_user, validate_firebase_token

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    id_token = request.cookies.get("token")
    error_message = "No error here"
    user_token = None
    user = None

    user_token = validate_firebase_token(id_token)
    if not user_token:
        return templates.TemplateResponse('login.html', {'request': request, 'user_token': None, 'error_message': None, 'user_info': None})

    user_id = user_token['email'] + "_" +  user_token['user_id']
    print(user_token)
    file_list = []
    directory_list = []
    
    blobs = blob_list(None, user_id)
    for blob in blobs:
        if blob.name[-1] == ('/'):
            blob.name = extract_relative_path(blob.name)
            blob.content_type = 'Folder'
            directory_list.append(blob)
        else:
            blob.name = extract_relative_path(blob.name)
            blob.content_type = 'File'
            file_list.append(blob)

    user = get_user(user_token).get()
    return templates.TemplateResponse('main.html', {'request': request, 'user_token': user_token, 'error_message': error_message, 'user_info': user, 'file_list': file_list, 'directory_list': directory_list})


@app.post("/add-directory", response_class=RedirectResponse)
async def add_directory_handler(request: Request):
    id_token = request.cookies.get("token")
    user_token = validate_firebase_token(id_token)
    if not user_token:
        return RedirectResponse(url='/')

    form = await request.form()
    dir_name = form['dir_name']
    
    if dir_name == '':
        return RedirectResponse('/')
    user_id = user_token['email'] + "_" +  user_token['user_id']
    add_directory(dir_name, user_id)
    return RedirectResponse(url='/', status_code=status.HTTP_302_FOUND)


@app.post("/download-file", response_class=RedirectResponse)
async def download_file_handler(request: Request):
    id_token = request.cookies.get("token")
    user_token = validate_firebase_token(id_token)
    if not user_token:
        return RedirectResponse(url='/')

    form = await request.form()
    prefix = f"users/{user_token['email']}_{user_token['user_id']}/"
    file_name = form['filename']
    download_path = prefix + file_name
    file = download_blob(download_path)

    return Response(file)


@app.post("/delete-file", response_class=RedirectResponse)
async def delete_file_handler(request: Request):
    id_token = request.cookies.get("token")
    user_token = validate_firebase_token(id_token)
    if not user_token:
        return RedirectResponse(url='/')

    form = await request.form()
    prefix = f"users/{user_token['email']}_{user_token['user_id']}/"
    file_name = form['filename']
    file_path = prefix + file_name
    delete_file(file_path)
    return RedirectResponse(url='/', status_code=status.HTTP_302_FOUND)

@app.post("/upload-file", response_class=RedirectResponse)
async def upload_file_handler(request: Request):
    id_token = request.cookies.get("token")
    user_token = validate_firebase_token(id_token)
    if not user_token:
        return RedirectResponse(url='/')

    form = await request.form()
    file = form['file_name']
    user_id = user_token['email'] + "_" +  user_token['user_id']

    if file.filename == '':
        return RedirectResponse(url='/', status_code=status.HTTP_302_FOUND)

    file = form['file_name']
    add_file(file, user_id)
    return RedirectResponse(url='/', status_code=status.HTTP_302_FOUND)


@app.get("/logout", response_class=RedirectResponse)
async def logout(request: Request):
    response = RedirectResponse(url='/', status_code=status.HTTP_302_FOUND)
    response.delete_cookie("token")
    return response
