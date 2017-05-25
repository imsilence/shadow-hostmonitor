#encoding: utf-8

import os
import hashlib
import shutil

def list_dir(fdir, fsuffix='*', except_fsuffixs=None, except_dirs=None):
    if except_fsuffixs is None: except_fsuffixs = []
    if except_dirs is None: except_dirs = []

    fdir = os.path.normpath(fdir)
    except_dirs = [os.path.normpath(except_dir) for except_dir in except_dirs]

    for path in __list_dir(fdir, fsuffix, except_fsuffixs, except_dirs):
        yield path


def __list_dir(fdir, fsuffix, except_fsuffixs, except_dirs):
    if os.path.exists(fdir):
        for fname in os.listdir(fdir):
            fpath = os.path.normpath(os.path.join(fdir, fname))
            if os.path.isdir(fpath):
                if fpath in except_dirs:
                    continue
                for cfpath in __list_dir(fpath, fsuffix, except_fsuffixs, except_dirs):
                    yield cfpath
            elif fsuffix == '*' or fname.endswith(fsuffix):
                pox = fname.rfind('.')
                if  pox == -1 or fname[pox:] not in except_fsuffixs:
                    yield fpath


def get_file_stat(path):
    if not os.path.exists(path):
        return None

    fd = os.open(path, os.O_RDONLY)
    stat_result = os.fstat(fd)
    os.close(fd)
    return stat_result


def get_md5(path):
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

def copy_file(src, dst):
    shutil.copy2(src, dst)



if __name__ == '__main__':
    from crypt import get_file_md5
    for i in list_dir('F:\\test', '*', [".doc"], ["F:\\test\\test"]):
        stat = get_file_stat(i)
        print(stat.st_mode)
        print(get_file_md5(i))
