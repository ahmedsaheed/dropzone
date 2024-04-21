from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from scripts.utils import extract_relative_path
import starlette.status as status
from scripts.blobs import blob_list, download_blob, get_sub_blob_list
from scripts.directory import add_directory, delete_directory, create_home_directory
from scripts.file import add_file, delete_file
from scripts.login import get_user, validate_firebase_token

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


def token_with_validation(request: Request):
    id_token = request.cookies.get("token")
    user_token = validate_firebase_token(id_token)
    return user_token

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    error_message = "No error here"
    user_token = None
    user = None
    user_token = token_with_validation(request)

    if not user_token:
        return templates.TemplateResponse('login.html', {'request': request, 'user_token': None, 'error_message': None, 'user_info': None})

    user_id = user_token['email'] + "_" +  user_token['user_id']
    print(user_token)
    file_list = []
    directory_list = []
    blobs = blob_list(None, user_id)
    for blob in blobs:
        if blob.name[-1] == ('/'):

            if should_add_to_list(extract_relative_path(blob.name)):
                blob.name = extract_relative_path(blob.name)
                blob.content_type = 'Folder'
                directory_list.append(blob)
        else:
            if should_add_to_list(extract_relative_path(blob.name)):
                blob.name = extract_relative_path(blob.name)
                blob.content_type = 'File'
                file_list.append(blob)

    create_home_directory(user_id, file_list, directory_list)

    print("storage", file_list, directory_list)
    user = get_user(user_token).get()
    return templates.TemplateResponse('main.html', {'request': request, 'user_token': user_token, 'error_message': error_message, 'user_info': user, 'file_list': file_list, 'directory_list': directory_list})


def should_add_to_list(blob_name):
    """
     check if the name contains more than one forward slash
     if it does, it is a subdirectory and should not be added to the list
    """
    print(blob_name.count('/'), blob_name)
    if blob_name.count('/') >= 2:
        return False
    return True

def should_add_to_sub(blob_name, sub_directory_path):
    if sub_directory_path == blob_name:
        return True
    # remove the subdirectory path from the blob name
    if sub_directory_path != blob_name:
        blob_name = blob_name.replace(sub_directory_path, '')
    print("name", blob_name)
    is_directory = False
    if blob_name[-1] == '/':
        is_directory = True

    if is_directory:
        if blob_name.count('/') == 1:
            return True
        else:
            return False

    if blob_name.count('/') == 0:
        return True
    return False

@app.post("/add-directory", response_class=RedirectResponse)
async def add_directory_handler(request: Request):

    user_token = token_with_validation(request)

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

    user_token = token_with_validation(request)

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

    user_token = token_with_validation(request)

    if not user_token:
        return RedirectResponse(url='/')

    form = await request.form()
    prefix = f"users/{user_token['email']}_{user_token['user_id']}/"
    file_name = form['filename']
    file_path = prefix + file_name
    delete_file(file_path)
    return RedirectResponse(url='/', status_code=status.HTTP_302_FOUND)

@app.post("/delete-directory", response_class=RedirectResponse)
async def delete_directory_handler(request: Request):
    user_token = token_with_validation(request)
    if not user_token:
        return RedirectResponse(url='/')

    form = await request.form()
    prefix = f"users/{user_token['email']}_{user_token['user_id']}/"
    dir_name = form['dirname']
    dir_path = prefix + dir_name
    delete_directory(dir_path)
    return RedirectResponse(url='/', status_code=status.HTTP_302_FOUND)

@app.post("/get-subdirectory", response_class=RedirectResponse)
async def get_subdirectory_handler(request: Request):
    user_token = token_with_validation(request)
    if not user_token:
        return RedirectResponse(url='/')
    form = await request.form()
    sub_directory_path = form['dirname']
    uid = user_token['email'] + "_" +  user_token['user_id']

    sub_blobs = get_sub_blob_list(uid, sub_directory_path)
    sub_file_list = []
    sub_directory_list = []

    if sub_directory_path == '/':
        return RedirectResponse(url='/', status_code=status.HTTP_302_FOUND)


    file_list = []
    directory_list = []
    main_blobs = blob_list(None, uid)

    for main_blob in main_blobs:
        if main_blob.name[-1] == ('/'):
            main_blob.name = extract_relative_path(main_blob.name)
            main_blob.content_type = 'Folder'
            directory_list.append(main_blob)
        else:
            main_blob.name = extract_relative_path(main_blob.name)
            main_blob.content_type = 'File'
            file_list.append(main_blob)

    for sub_blob in sub_blobs:
        if sub_blob.name[-1] == ('/'):

            if should_add_to_sub(extract_relative_path(sub_blob.name), sub_directory_path):
                sub_blob.name = extract_relative_path(sub_blob.name)
                sub_blob.content_type = 'Folder'
                sub_directory_list.append(sub_blob)
        else:
            if should_add_to_sub(extract_relative_path(sub_blob.name), sub_directory_path):
                sub_blob.name = extract_relative_path(sub_blob.name)
                sub_blob.content_type = 'File'
                sub_file_list.append(sub_blob)

    return templates.TemplateResponse('main.html', {'request': request, 'user_token': user_token, 'error_message': None, 'sub_file_list': sub_file_list, 'sub_directory_list': sub_directory_list, 'directory_list': directory_list, 'file_list': file_list })

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
