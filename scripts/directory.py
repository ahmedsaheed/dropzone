import local_constants
from google.cloud import storage

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
    dir_is_empty = should_delete_dir(directory_path)
    if blob.exists():
            blob.delete()
    else:
       print('Directory does not exist')


def should_delete_dir(directory_path):
    storage_client = storage.Client(project=project_name)
    bucket = storage_client.bucket(project_storage_bucket)
    blobs = bucket.list_blobs(prefix=directory_path)
    list_of_blob = list(blobs)
    return len(list_of_blob) <= 1


def create_home_directory_if_necessary(user_id, file_blob, directory_blob):
    if len(file_blob) == 0 and len(directory_blob) == 0:
        add_directory('', user_id)


def check_for_duplicate_file(file_list):
    # itrate through the list of files and check for matching md5_hash property
    # if a match is found, return the two matching files
    #
    matching_files = []
    for i in range(len(file_list)):
        print(file_list[i].md5_hash, file_list[i].name)
        for j in range(i+1, len(file_list)):
            if file_list[i].md5_hash == file_list[j].md5_hash:
                matching_files.append((file_list[i], file_list[j]))
                return matching_files
