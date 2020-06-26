import re
import os
import stat
import shutil

MAX_MEMBER_REPR_LENGTH = 1000


class HypergolFileAlreadyExistsException(Exception):
    pass


class Mode:
    DRY_RUN = 'DRY_RUN'
    FORCE = 'FORCE'
    NORMAL = 'NORMAL'
    ALL = [DRY_RUN, FORCE, NORMAL]


def get_mode(mode, dryrun, force):
    if force:
        mode = Mode.FORCE
    if dryrun:
        mode = Mode.DRY_RUN
    if mode not in Mode.ALL:
        raise ValueError(f'mode must be one of {Mode.ALL}')
    return mode


def _test_existence(path, objectName, mode):
    if not os.path.exists(path):
        if mode == Mode.DRY_RUN:
            print(f'{objectName} {path} does not exist - {mode}')
        else:
            raise ValueError(f'{objectName} {path} does not exist - {mode}')


def _mode_handler(path, verb, objectName, mode, handledFunction):
    print(f'{verb} {objectName.lower()} {path} - {mode}')
    if mode == Mode.NORMAL:
        if os.path.exists(path):
            raise HypergolFileAlreadyExistsException(f'{objectName} {path} already exist')
        handledFunction()
    elif mode == Mode.DRY_RUN:
        if os.path.exists(path):
            print(f"{objectName} {path} already exist - {mode}")
    elif mode == Mode.FORCE:
        if os.path.exists(path):
            print(f"{objectName} {path} already exist - {mode}")
        else:
            handledFunction()
    else:
        raise ValueError(f'Unknown mode: {mode}')
    print(f'{verb} {objectName.lower()} {path} - DONE - {mode}')


def make_file_executable(filePath, mode):
    print(f'Making file {filePath} executable - {mode}')
    _test_existence(filePath, 'File', mode)
    if mode != Mode.DRY_RUN:
        fileStat = os.stat(filePath)
        if os.getuid() == fileStat.st_uid:
            os.chmod(filePath, fileStat.st_mode | stat.S_IXUSR)


def create_text_file(filePath, content, mode):
    def _create_text_file():
        with open(filePath, 'wt') as f:
            f.write(content)
    _mode_handler(
        path=filePath,
        verb='Creating',
        objectName='File',
        mode=mode,
        handledFunction=_create_text_file
    )


def create_directory(path, mode):
    def _create_directory():
        os.mkdir(path)
    _mode_handler(
        path=path,
        verb='Creating',
        objectName='Directory',
        mode=mode,
        handledFunction=_create_directory
    )


def copy_file(src, dst, mode):
    def _copy_file():
        shutil.copy(src, dst)
    _test_existence(src, 'File', mode)
    _mode_handler(
        path=dst,
        verb='Copying',
        objectName='File',
        mode=mode,
        handledFunction=_copy_file
    )


class Repr:

    def __repr__(self):
        members = ', '.join(f'{k}={str(v)[:MAX_MEMBER_REPR_LENGTH]}' for k, v in self.__dict__.items())
        return f"{self.__class__.__name__}({members})"

    def __str__(self):
        return self.__repr__()


def to_snake(name):
    name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', name).lower()

def to_camel(name):
    return ''.join([v.title() for v in name.split('_')])
