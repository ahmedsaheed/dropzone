from typing_extensions import Any
from google.auth.jwt import Mapping
import starlette.status as status
from fastapi import FastAPI, Request, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse, Response, StreamingResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from scripts.utils import extract_relative_path, should_add_to_list, should_add_to_sub
from scripts.blobs import blob_list, download_blob, get_sub_blob_list, get_photos
from scripts.directory import add_directory, delete_directory, create_home_directory_if_necessary, dir_exists, should_delete_dir
from scripts.file import add_file, copy_file, delete_file, file_exist, check_for_duplicate_file
from scripts.login import get_user, get_all_users, validate_firebase_token

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")
error_array = [] # Global data structure for messages to be displayed to the user - not necessarily an error


"""
Root route for the application.
This route is responsible for rendering the main page of the application.
If logged in, the user's information is retrieved and displayed on the page. (if new user, a default root is created for them)
Otherwise, the user is redirected to the login page.
"""
@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    user_token = None
    user = None
    user_token = token_with_validation(request)
    error_message = check_for_error()

    if not user_token:
        return templates.TemplateResponse('login.html', {'request': request, 'user_token': None, 'error_message': None, 'user_info': None})

    user_id = get_user_id(user_token)
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

    create_home_directory_if_necessary(user_id, file_list, directory_list)
    duplicate_files = check_for_duplicate_file(file_list)
    if not duplicate_files == None:
        files = duplicate_files[0].name + " and " + duplicate_files[1].name
        error_array.append("Duplicate files found in your storage: " + files)
        error_message = error_array.pop()

    user = get_user(user_token).get()
    all_users = get_all_users(user_token)
    return templates.TemplateResponse('main.html', {'request': request, 'user_token': user_token, 'error_message': error_message, 'user_info': user, 'all_users': all_users, 'file_list': file_list, 'directory_list': directory_list})



"""
Route for navigating to a subdirectory.
This route is responsible for rendering the subdirectory page of the application.
Has same functionality as the root route, but for a specific subdirectory.
"""
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
        try:
            query_params = request.query_params['dir-path']
            print("Got Header", query_params)
            sub_directory_path = query_params
        except:  # Get back up if lost
            sub_directory_path = '/'

    uid = get_user_id(user_token)
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

    duplicate_files = check_for_duplicate_file(sub_file_list)
    if not duplicate_files == None:
        files = duplicate_files[0].name + " and " + duplicate_files[1].name
        error_array.append("Duplicate files found in this directory: " + files)

    error_message = check_for_error()
    all_users = get_all_users(user_token)
    return templates.TemplateResponse('main.html', {'request': request, 'user_token': user_token, 'all_users': all_users, 'error_message': error_message, 'sub_file_list': sub_file_list, 'sub_directory_list': sub_directory_list, 'directory_list': [], 'file_list': [] })



"""
Route for handling add-directory requests.
This route is responsible for adding a new directory to the user's storage.
"""
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
    user_id = get_user_id(user_token)

    if dir_exists(dir_name, user_id):
        error_array.append("Folder already exists! skipping creation.")
        if prefix == '':
            return RedirectResponse(url='/', status_code=status.HTTP_302_FOUND)
        else:
            url_and_params = f'/get-subdirectory?dir-path={dir_name}'
            return RedirectResponse(url=url_and_params, status_code=status.HTTP_302_FOUND)

    add_directory(dir_name, user_id)
    if prefix == '':
        return RedirectResponse(url='/', status_code=status.HTTP_302_FOUND)
    else:
        url_and_params = f'/get-subdirectory?dir-path={dir_name}'
        return RedirectResponse(url=url_and_params, status_code=status.HTTP_302_FOUND)


"""
Route for handling upload-file requests.
This route is responsible for uploading a file to the user's storage.
On the client side, there's a flag that allows the user to overwrite a file if it already exists.
"""
@app.post("/upload-file", response_class=RedirectResponse)
async def upload_file_handler(request: Request):
    id_token = request.cookies.get("token")
    user_token = validate_firebase_token(id_token)
    if not user_token:
        return RedirectResponse(url='/')

    form = await request.form()
    file = form['file_name']

    try:
        prefix = form['file-path-prefix']
    except:
        prefix = ''

    try:
        # This is a flag that allows overwrite only if the file already exists
        should_overwrite = str(form['overwrite-file-control'])
    except:
        should_overwrite = None

    if prefix == '/':
        prefix = ''
    user_id = get_user_id(user_token)
    if file.filename == '':
        return RedirectResponse(url='/', status_code=status.HTTP_302_FOUND)

    # Does it exist and should we overwrite?
    if file_exist(file, prefix, user_id) and should_overwrite == "true":
        path = f"users/{user_token['email']}_{user_token['user_id']}/" + str(file.filename)
        delete_file(path)
        add_file(file, prefix, user_id)
        error_array.append(f"{file.filename} added successfully")
        if prefix == '':
            return RedirectResponse(url='/', status_code=status.HTTP_302_FOUND)
        return RedirectResponse(url=f'/get-subdirectory?dir-path={prefix}', status_code=status.HTTP_302_FOUND)

    add_file(file, prefix, user_id)
    error_array.append(f"{file.filename} added successfully")
    if prefix == '':
        return RedirectResponse(url='/', status_code=status.HTTP_302_FOUND)
    else:
        url_and_params = f'/get-subdirectory?dir-path={prefix}'
        return RedirectResponse(url=url_and_params, status_code=status.HTTP_302_FOUND)






"""
Route for handling download-file requests.
This route is responsible for downloading a file from the user's storage
It uses the StreamingResponse class to stream the into the user local machine.
"""
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



"""
Route for handling delete-file requests.
This route is responsible for deleting a file from the user's storage.
Deletes the file and redirects to where the user was before.
"""
@app.post("/delete-file", response_class=RedirectResponse)
async def delete_file_handler(request: Request):
    user_token = token_with_validation(request)
    if not user_token:
        return RedirectResponse(url='/')

    form = await request.form()
    prefix = f"users/{user_token['email']}_{user_token['user_id']}/"
    file_name = form['filename']
    try:
        sub_dir_path = form['delete-path-prefix']
        print(sub_dir_path)
    except:
        sub_dir_path = None
    file_path = prefix + str(file_name)
    delete_file(file_path)
    if sub_dir_path:
        return RedirectResponse(url=f'/get-subdirectory?dir-path={sub_dir_path}', status_code=status.HTTP_302_FOUND)
    return RedirectResponse(url='/', status_code=status.HTTP_302_FOUND)






"""
Route for handling delete-directory requests.
This route is responsible for deleting a non empty directory from the user's storage.
Deletes the non empty directory and redirects to where the user was before.
"""
@app.post("/delete-directory", response_class=RedirectResponse)
async def delete_directory_handler(request: Request):
    user_token = token_with_validation(request)
    if not user_token:
        return RedirectResponse(url='/')

    form = await request.form()
    prefix = f"users/{user_token['email']}_{user_token['user_id']}/"
    dir_name = form['dirname']
    try:
        sub_dir_path = form['delete-folder-prefix-name']
        print(sub_dir_path)
    except:
        sub_dir_path = None

    dir_path = prefix + str(dir_name)
    if not should_delete_dir(dir_path):
        error_array.append("Can't delete non-empty folder.")
        if sub_dir_path:
            return RedirectResponse(url=f'/get-subdirectory?dir-path={sub_dir_path}', status_code=status.HTTP_302_FOUND)
        return RedirectResponse(url='/', status_code=status.HTTP_302_FOUND)
    delete_directory(dir_path)
    error_array.append("Directory deleted successfully")
    if sub_dir_path:
        return RedirectResponse(url=f'/get-subdirectory?dir-path={sub_dir_path}', status_code=status.HTTP_302_FOUND)
    return RedirectResponse(url='/', status_code=status.HTTP_302_FOUND)





"""
Route for handling share-file requests.
This route is responsible for sharing a file with another user.
It copies the file to the recipient's base directory.
"""
@app.post('/share-file', response_class=RedirectResponse)
async def share_file_handler(request: Request):
    user_token = token_with_validation(request)
    if not user_token:
        return RedirectResponse(url='/')

    source_path_base = f"users/{user_token['email']}_{user_token['user_id']}/"
    form = await request.form()
    relative_path = str(form['source_path'])
    recipient_email = form['recipient_email']

    if relative_path.startswith('/'):
        relative_path = relative_path[1:]

    source_path = source_path_base + relative_path
    copy_file(user_token, source_path, recipient_email)
    error_array.append(f"File shared with {recipient_email}")
    return RedirectResponse(url='/', status_code=status.HTTP_302_FOUND)


"""
Route for handling get-photos requests.
This route is responsible for fetching all the photos from the user's storage.
It fetches the photos and returns them the client for rendering.
"""
@app.post("/get-photos", response_class=RedirectResponse)
async def get_photos_handler(request: Request):
    user_token = token_with_validation(request)
    if not user_token:
        return RedirectResponse(url='/')

    uid = get_user_id(user_token)
    photos_data = get_photos(uid)
    error_message = check_for_error()
    return templates.TemplateResponse('main.html', {'request': request, 'user_token': user_token, 'photos': photos_data, 'error_message': error_message, 'directory_list': [], 'file_list': [] })


# Retrieves and validates the user's token from the request
def token_with_validation(request: Request) -> Mapping[str, Any] | None:
    id_token = request.cookies.get("token")
    user_token = validate_firebase_token(id_token)
    return user_token


# Manage the messages to be displayed to the user
def check_for_error() -> str:
    if len(error_array) > 0:
        return error_array.pop()
    return "No error here"


# Get the user uid from the user token
def get_user_id(user_token) -> str:
    return user_token['email'] + "_" +  user_token['user_id']
