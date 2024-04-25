from google.cloud import storage
import local_constants

project_name = local_constants.PROJECT_NAME
project_storage_bucket = local_constants.PROJECT_STORAGE_BUCKET

def does_file_exist(file, prefix, uid):
    storage_client = storage.Client(project=project_name)
    bucket = storage_client.bucket(project_storage_bucket)
    path = f"users/{uid}/{prefix}{file.filename}"
    blob = bucket.blob(path)
    return blob.exists()

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


def delete_file(file_path):
    storage_client = storage.Client(project=project_name)
    bucket = storage_client.bucket(project_storage_bucket)
    blob = bucket.blob(file_path)
    if blob.exists():
        blob.delete()
    else:
        print('File does not exist')
