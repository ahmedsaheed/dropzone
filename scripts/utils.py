def extract_relative_path(path):
    relative_path = path.split('/', 2)[2]
    if relative_path == '':
        return '/'
    return relative_path

def should_add_to_list(blob_name):
    """
     check if the name contains more than one forward slash
     if it does, it is a subdirectory and should not be added to the list
    """
    # if is not a directory and has more than one forward slash, it is a subdirectory and should not be added to the list

    if not str(blob_name).endswith('/'):
        if blob_name.count('/') >  0:
            return False

    if blob_name.count('/') >= 2:
        return False
    return True

def should_add_to_sub(blob_name, sub_directory_path):
    if sub_directory_path == blob_name:
        return True
    # remove the subdirectory path from the blob name
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
