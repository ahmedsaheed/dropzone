from fastapi import FastAPI, Request, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse, Response, StreamingResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from scripts.utils import extract_relative_path, should_add_to_list, should_add_to_sub
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

    user = get_user(user_token).get()
    return templates.TemplateResponse('main.html', {'request': request, 'user_token': user_token, 'error_message': error_message, 'user_info': user, 'file_list': file_list, 'directory_list': directory_list})


@app.post("/add-directory", response_class=RedirectResponse)
async def add_directory_handler(request: Request):
    user_token = token_with_validation(request)
    if not user_token:
        return RedirectResponse(url='/')

    form = await request.form()
    prefix = form['dir-path-prefix']
    dir_name = form['dir_name']
    if prefix == '/':
        prefix = ''

    if dir_name == '':
        return RedirectResponse('/')

    dir_name = str(prefix) + str(dir_name)
    user_id = user_token['email'] + "_" +  user_token['user_id']
    add_directory(dir_name, user_id)

    # if the directory is added to the root directory, redirect to the root else call get-subdirectory with the new directory as form da

    if prefix == '':
        return RedirectResponse(url='/', status_code=status.HTTP_302_FOUND)
    else:
        url_and_params = f'/get-subdirectory?dir-path={dir_name}'
        return RedirectResponse(url=url_and_params, status_code=status.HTTP_302_FOUND)

@app.post("/upload-file", response_class=RedirectResponse)
async def upload_file_handler(request: Request):
    id_token = request.cookies.get("token")
    user_token = validate_firebase_token(id_token)
    if not user_token:
        return RedirectResponse(url='/')

    form = await request.form()
    file = form['file_name']
    prefix = form['file-path-prefix']

    if prefix == '/':
        prefix = ''
    user_id = user_token['email'] + "_" +  user_token['user_id']

    if file.filename == '':
        return RedirectResponse(url='/', status_code=status.HTTP_302_FOUND)

    add_file(file, prefix, user_id)

    if prefix == '':
        return RedirectResponse(url='/', status_code=status.HTTP_302_FOUND)
    else:
        url_and_params = f'/get-subdirectory?dir-path={prefix}'
        return RedirectResponse(url=url_and_params, status_code=status.HTTP_302_FOUND)


@app.post("/download-file", response_class=RedirectResponse)
async def download_file_handler(request: Request):
    user_token = token_with_validation(request)
    if not user_token:
        return RedirectResponse(url='/')

    form = await request.form()
    prefix = f"users/{user_token['email']}_{user_token['user_id']}/"
    file_name = form['filename']
    download_path = prefix + str(file_name)
    file = download_blob(download_path)
    return StreamingResponse(iter([file]), media_type='application/octet-stream', headers={"Content-Disposition": f"attachment;filename={file_name}"})


@app.post("/delete-file", response_class=RedirectResponse)
async def delete_file_handler(request: Request):
    user_token = token_with_validation(request)
    if not user_token:
        return RedirectResponse(url='/')

    form = await request.form()
    prefix = f"users/{user_token['email']}_{user_token['user_id']}/"
    file_name = form['filename']
    file_path = prefix + str(file_name)
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
    dir_path = prefix + str(dir_name)
    delete_directory(dir_path)
    return RedirectResponse(url='/', status_code=status.HTTP_302_FOUND)


@app.route("/get-subdirectory", methods=['GET', 'POST'])
async def get_subdirectory_handler(request: Request):
    user_token = token_with_validation(request)
    if not user_token:
        return RedirectResponse(url='/')

    form = await request.form()
    if form:
        sub_directory_path = form['dirname']
    else:
        # check for query params
        query_params = request.query_params['dir-path']
        print("Got Header", query_params)
        sub_directory_path = query_params

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


@app.get("/logout", response_class=RedirectResponse)
async def logout(request: Request):
    response = RedirectResponse(url='/', status_code=status.HTTP_302_FOUND)
    response.delete_cookie("token")
    return response
