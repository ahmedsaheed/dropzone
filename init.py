from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import google.oauth2.id_token
from google.auth.transport import requests
from google.cloud import firestore, storage
import starlette.status as status
import local_constants

app = FastAPI()
firestore_db = firestore.Client()
firebase_request_adapter = requests.Request()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

def add_directory(directory_name):
    storage_client = storage.Client(project=local_constants.PROJECT_NAME)
    bucket = storage_client.bucket(local_constants.PROJECT_STORAGE_BUCKET)
    blob = bucket.blob(directory_name)
    blob.upload_from_string('', content_type='application/x-www-form-urlencoded;charset=UTF-8')


def add_file(file):
    storage_client = storage.Client(project=local_constants.PROJECT_NAME)
    bucket = storage_client.bucket(local_constants.PROJECT_STORAGE_BUCKET)
    print(file)
    blob = storage.Blob(file.filename, bucket)
    blob.upload_from_file(file.file)


def blob_list(prefix):
    storage_client = storage.Client(project=local_constants.PROJECT_NAME)
    return storage_client.list_blobs(local_constants.PROJECT_STORAGE_BUCKET, prefix=prefix)


def download_blob(file_name):
    storage_client = storage.Client(project=local_constants.PROJECT_NAME)
    bucket = storage_client.bucket(local_constants.PROJECT_STORAGE_BUCKET)
    blob = bucket.get_blob(file_name)
    return blob.download_as_bytes()

def get_user(user_token):
    user = firestore_db.collection('users').document(user_token['user_id'])
    if not user.get().exists:
        user_data = {
            'name': "John Doe"
        }
        firestore_db.collection('users').document(user_token['user_id']).set(user_data)
    return user

def validate_firebase_token(id_token):
    if not id_token:
        return None

    user_token = None
    try:
        user_token = google.oauth2.id_token.verify_firebase_token(
            id_token, firebase_request_adapter
        )
    except ValueError as err:
        print(str(err))

    return user_token

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    id_token = request.cookies.get("token")
    error_message = "No error here"
    user_token = None
    user = None

    user_token = validate_firebase_token(id_token)
    if not user_token:
        return templates.TemplateResponse('main.html', {'request': request, 'user_token': None, 'error_message': None, 'user_info': None})

    file_list = []
    directory_list = []
    
    blobs = blob_list(None)
    for blob in blobs:
        if blob.name[-1] == ('/'):
            directory_list.append(blob)
        else:
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
    
    if dir_name == '' or dir_name[-1] != '/':
        return RedirectResponse('/')

    add_directory(dir_name)
    return RedirectResponse(url='/', status_code=status.HTTP_302_FOUND)


@app.post("/download-file", response_class=RedirectResponse)
async def download_file_handler(request: Request):
    id_token = request.cookies.get("token")
    user_token = validate_firebase_token(id_token)
    if not user_token:
        return RedirectResponse(url='/')

    form = await request.form()
    file_name = form['filename']
    file = download_blob(file_name)
    return Response(file)


@app.post("/upload-file", response_class=RedirectResponse)
async def upload_file_handler(request: Request):
    id_token = request.cookies.get("token")
    user_token = validate_firebase_token(id_token)
    if not user_token:
        return RedirectResponse(url='/')

    form = await request.form()

    file = form['file_name']

    # if file.filename == '':
    #     return RedirectResponse(url='/', status_code=status.HTTP_302_FOUND)

    file = form['file_name']
    add_file(file)
    return RedirectResponse(url='/', status_code=status.HTTP_302_FOUND)

