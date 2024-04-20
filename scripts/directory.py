from google.cloud import storage
import local_constants

project_name = local_constants.PROJECT_NAME
project_storage_bucket = local_constants.PROJECT_STORAGE_BUCKET

def add_directory(directory_name, user_id):
    storage_client = storage.Client(project=project_name)
    bucket = storage_client.bucket(project_storage_bucket)
    new_path = f"users/{user_id}/{directory_name}"
    print(new_path) 

    if not new_path.endswith('/'):
        new_path += '/'

    blob = bucket.blob(new_path)
    blob.upload_from_string('', content_type='application/x-www-form-urlencoded;charset=UTF-8')


def delete_directory(directory_path):
    storage_client = storage.Client(project=project_name)
    bucket = storage_client.bucket(project_storage_bucket)
    blob = bucket.blob(directory_path)
    if blob.exists():
        blob.delete()
    else:
        print('Directory does not exist')

def create_home_directory(user_id, file_blob, directory_blob):
    if len(file_blob) == 0 and len(directory_blob) == 0:
        storage_client = storage.Client(project=project_name)
        bucket = storage_client.bucket(project_storage_bucket)
        new_path = f"users/{user_id}/"
        blob = bucket.blob(new_path)
        blob.upload_from_string('', content_type='application/x-www-form-urlencoded;charset=UTF-8')        
