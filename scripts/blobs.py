import local_constants
from google.cloud import storage

# Get the base directory for the user using the user id
def blob_list(prefix, uid):
    storage_client = storage.Client(project=local_constants.PROJECT_NAME)
    user_prefix = f"users/{uid}/"
    if prefix:
        user_prefix += prefix

    return storage_client.list_blobs(local_constants.PROJECT_STORAGE_BUCKET, prefix=user_prefix)

# Get the subdirectories for the user using the user id and the subdirectory path
def get_sub_blob_list(uid, sub_dir_path):
    storage_client = storage.Client(project=local_constants.PROJECT_NAME)
    user_prefix = f"users/{uid}/"
    if sub_dir_path:
        user_prefix += sub_dir_path
    print(user_prefix)
    return storage_client.list_blobs(local_constants.PROJECT_STORAGE_BUCKET, prefix=user_prefix)

# Download a blob as byte from the storage bucket using the blob path
def download_blob(download_path):
    storage_client = storage.Client(project=local_constants.PROJECT_NAME)
    bucket = storage_client.bucket(local_constants.PROJECT_STORAGE_BUCKET)
    blob = bucket.get_blob(download_path)
    return blob.download_as_bytes()

# Gets all the photos from the user bucket using the user id
def get_photos(uid):
    base = blob_list(None, uid)
    blobs_uri =  [blob.name for blob in base if blob.name.endswith('.jpg') or blob.name.endswith('.jpeg') or blob.name.endswith('.png')]
    storage_client = storage.Client(project=local_constants.PROJECT_NAME)
    bucket = storage_client.bucket(local_constants.PROJECT_STORAGE_BUCKET)
    # here, we make the blob public to access it from UI
    blob_public_url = []
    for blob_name in blobs_uri:
        blob = bucket.blob(blob_name)
        blob.make_public()
        blob_public_url.append({
            'name': blob_name,
            'url': blob.public_url
        })

    return blob_public_url
