from google.cloud import firestore, storage
import local_constants

def add_file(file):
    storage_client = storage.Client(project=local_constants.PROJECT_NAME)
    bucket = storage_client.bucket(local_constants.PROJECT_STORAGE_BUCKET)
    print(file)
    blob = storage.Blob(file.filename, bucket)
    blob.upload_from_file(file.file)
