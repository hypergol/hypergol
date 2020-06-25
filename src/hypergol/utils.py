import re
import os
import stat
import shutil

MAX_MEMBER_REPR_LENGTH = 1000


class Mode:
    DRY_RUN = 'dry_run'
    FORCE = 'force'
    NORMAL = 'normal'
    ALL = [DRY_RUN, FORCE, NORMAL]

# TODO(Laszlo): all file operations should go through these function
# TODO(Laszlo): all paths should use pathlib


def create_text_file(filePath, content, mode):
    if os.path.exists(filePath):
        if mode == Mode.DRY_RUN:
            print("ValueError(f'{filePath} already exists, use --force flag to overwrite it')")
        else:
            raise ValueError(f'{filePath} already exists, use --force flag to overwrite it')
    if mode == Mode.DRY_RUN:
        print(content)
    else:
        with open(filePath, 'wt') as dataModelFile:
            dataModelFile.write(content)


def create_directory(path, mode):
    if os.path.exists(path):
        if mode == Mode.DRY_RUN:
            print(f"ValueError('Directory {path} already exist")
        else:
            raise ValueError(f'Directory {path} already exist')
    if mode == Mode.DRY_RUN:
        print(f'creating {path} directory')
    else:
        os.mkdir(path)


def copy_file(src, dst, mode):
    try:
        if mode == Mode.DRY_RUN:
            print(f'copying {src} to {dst}')
        else:
            shutil.copy(src, dst)
    except shutil.Error as err:
        if mode == Mode.DRY_RUN:
            print(err)
        else:
            raise err


class Repr:

    def __repr__(self):
        members = ', '.join(f'{k}={str(v)[:MAX_MEMBER_REPR_LENGTH]}' for k, v in self.__dict__.items())
        return f"{self.__class__.__name__}({members})"

    def __str__(self):
        return self.__repr__()


def to_snake(name):
    name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', name).lower()


def make_file_executable(filePath):
    fileStat = os.stat(filePath)
    if os.getuid() == fileStat.st_uid:
        os.chmod(filePath, fileStat.st_mode | stat.S_IXUSR)
