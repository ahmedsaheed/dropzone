from google.cloud import storage
import local_constants
from scripts.login import get_all_users
from scripts.utils import _extract_file_name

project_name = local_constants.PROJECT_NAME
project_storage_bucket = local_constants.PROJECT_STORAGE_BUCKET

# Determine if a file exists in the storage bucket
def file_exist(file, prefix, uid):
    storage_client = storage.Client(project=project_name)
    bucket = storage_client.bucket(project_storage_bucket)
    path = f"users/{uid}/{prefix}{file.filename}"
    blob = bucket.blob(path)
    return blob.exists()


# Adds a file to a storage bucket of a user
# Uses a prefix to determine the subdirectory to add the file to
def add_file(file, prefix, uid):
    storage_client = storage.Client(project=project_name)
    bucket = storage_client.bucket(project_storage_bucket)
    path = f"users/{uid}/{prefix}{file.filename}"
    print("file added in " + path)
    blob = storage.Blob(path, bucket)
    # https://cloud.google.com/python/docs/reference/storage/latest/generation_metageneration#using-ifgenerationmatch
    # In case we need to overwrite the file, we can use the if_generation_match parameter
    # https://stackoverflow.com/a/75547773/16943869
    blob.upload_from_file(file.file)


# Itrates through the list of files and check for matching md5_hash property
# if a match is found, return the two matching files
def check_for_duplicate_file(file_list):
    matching_files = []
    for i in range(len(file_list)):
        print(file_list[i].md5_hash, file_list[i].name)
        for j in range(i+1, len(file_list)):
            if file_list[i].md5_hash == file_list[j].md5_hash:
                matching_files.append(file_list[i])
                matching_files.append(file_list[j])
                return matching_files


# Delete a blob from the storage bucket using the blob's path
def delete_file(file_path):
    storage_client = storage.Client(project=project_name)
    bucket = storage_client.bucket(project_storage_bucket)
    blob = bucket.blob(file_path)
    if blob.exists():
        blob.delete()
    else:
        print('File does not exist')


# Copy a file from one user's storage bucket to another user's storage bucket
# Uses the source path to get the file to copy and the recipient email to get the destination path
# https://cloud.google.com/storage/docs/copying-renaming-moving-objects#copy
def copy_file(user_token, source_path, recipient_email):
    all_users = get_all_users(user_token)
    reciever = None
    for user in all_users:
       if user['email'] == recipient_email:
           reciever = user
           break

    if reciever is None:
        print('User not found')
        return
    email = reciever['email']
    id = reciever['id']
    destination_path = f"users/{email}_{id}/"

    print(f"Copying file from {source_path} to {destination_path}")
    storage_client = storage.Client(project=project_name)
    bucket = storage_client.bucket(project_storage_bucket)
    source_blob = bucket.blob(source_path)
    source_bucket = source_blob.bucket
    destination_blob = bucket.blob(destination_path)
    destination_bucket = destination_blob.bucket
    extracted_file_name = _extract_file_name(source_blob.name)
    name = str(destination_blob.name) + extracted_file_name.strip()
    print(source_blob.exists(), source_blob.name)
    if source_blob.exists():
        blob_copy = source_bucket.copy_blob(source_blob, destination_bucket, name)
        print(
              "Blob {} in bucket {} copied to blob {} in bucket {}.".format(
                  source_blob.name,
                  source_bucket.name,
                  blob_copy.name,
                  destination_bucket.name,
              )
          )
    else:
        print('File does not exist')
