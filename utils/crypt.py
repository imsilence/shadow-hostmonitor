#encoding: utf-8
import os
import hashlib

def get_file_md5(path):
    if not os.path.exists(path):
        return None

    md5 = hashlib.md5()
    fhandler = open(path, 'rb')
    while True:
        cxt = fhandler.read(1024 * 5)
        if b'' == cxt:
            break

        md5.update(cxt)

    fhandler.close()
    return md5.hexdigest()

def get_str_md5(cxt):
    md5 = hashlib.md5()
    md5.update(cxt.encode('utf-8'))
    return md5.hexdigest()


if __name__ == '__main__':
    print(get_str_md5('abc'))
