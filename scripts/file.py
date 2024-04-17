from google.cloud import storage
import local_constants

project_name = local_constants.PROJECT_NAME
project_storage_bucket = local_constants.PROJECT_STORAGE_BUCKET

def add_file(file, uid):
    storage_client = storage.Client(project=project_name)
    bucket = storage_client.bucket(project_storage_bucket)
    path = f"users/{uid}/{file.filename}"

    blob = storage.Blob(path, bucket)
    blob.upload_from_file(file.file)

def delete_file(file_path):
    storage_client = storage.Client(project=project_name)
    bucket = storage_client.bucket(project_storage_bucket)


    blob = bucket.blob(file_path)
    if blob.exists():
        blob.delete()
    else:
        print('File does not exist')