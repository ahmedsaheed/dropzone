import local_constants
from google.cloud import storage

def blob_list(prefix, uid):
    storage_client = storage.Client(project=local_constants.PROJECT_NAME)
    user_prefix = f"users/{uid}/"
    if prefix:
        user_prefix += prefix 
    
    return storage_client.list_blobs(local_constants.PROJECT_STORAGE_BUCKET, prefix=user_prefix)


def download_blob(download_path):
    storage_client = storage.Client(project=local_constants.PROJECT_NAME)
    bucket = storage_client.bucket(local_constants.PROJECT_STORAGE_BUCKET)
    blob = bucket.get_blob(download_path)
    return blob.download_as_bytes()
