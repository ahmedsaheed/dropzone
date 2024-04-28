# Extracts the relative path from the full path
def extract_relative_path(path):
    relative_path = path.split('/', 2)[2]
    if relative_path == '':
        return '/'
    return relative_path

"""
    Determines if a blob should be added to the base list of blobs
    based on the number of slashes in the blob name
    example:
        /users/1/ -> True
        /users/1/1/ -> False
        /users/1/1.txt -> True
        /users/1/1/1.txt -> False
"""
def should_add_to_list(blob_name):
    if not str(blob_name).endswith('/'):
        if blob_name.count('/') >  0:
            return False

    if blob_name.count('/') >= 2:
        return False
    return True


# Equivalent to should_add_to_list but for subdirectories
def should_add_to_sub(blob_name, sub_directory_path):
    if sub_directory_path == blob_name:
        return True
    if sub_directory_path != blob_name:
        blob_name = blob_name.replace(sub_directory_path, '')
    is_directory = False
    if blob_name[-1] == '/':
        is_directory = True

    if is_directory:
        if blob_name.count('/') == 1:
            return True
        else:
            return False

    if blob_name.count('/') == 0:
        return True
    return False


# Extracts the file name from the full path
# example: /users/1/1.txt -> 1.txt, /users/1/2/3.txt -> 3.txt
def _extract_file_name(file_path):
    return file_path.strip().split('/')[-1]
