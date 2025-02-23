import os

def is_valid_file(path):
    return os.path.exists(path) and os.path.isfile(path)
