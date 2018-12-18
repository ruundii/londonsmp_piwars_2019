import hashlib
def file_as_bytes(file):
    with file:
        return file.read()

def getFileHash(path):
    return hashlib.md5(file_as_bytes(open(path, 'rb'))).hexdigest()