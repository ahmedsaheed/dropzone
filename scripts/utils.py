def extract_relative_path(path):
    relative_path = path.split('/', 2)[2]
    if relative_path == '':
        return '/'
    return relative_path 
