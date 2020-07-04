import os

MAX_MEMBER_REPR_LENGTH = 1000


def delete_if_exists(filePath):
    if os.path.exists(filePath):
        if os.path.isdir(filePath):
            os.rmdir(filePath)
        else:
            os.remove(filePath)


class HypergolFileAlreadyExistsException(Exception):
    pass


class Mode:
    DRY_RUN = 'DRY_RUN'
    FORCE = 'FORCE'
    NORMAL = 'NORMAL'
    ALL = [DRY_RUN, FORCE, NORMAL]


def mode_message(mode):
    if mode == Mode.NORMAL:
        return ''
    return f' - Mode: {mode}'


def _mode_handler(path, verb, objectName, mode, handledFunction):
    print(f'{verb} {objectName.lower()} {path}.{mode_message(mode)}')
    if mode == Mode.NORMAL:
        if os.path.exists(path):
            raise HypergolFileAlreadyExistsException(f'{objectName} {path} already exist.{mode_message(mode)}')
        handledFunction()
    elif mode == Mode.DRY_RUN:
        if os.path.exists(path):
            print(f"{objectName} {path} already exist.{mode_message(mode)}")
    elif mode == Mode.FORCE:
        if os.path.exists(path):
            print(f"{objectName} {path} already exist.{mode_message(mode)}")
        try:
            handledFunction()
        except FileExistsError:
            pass
    else:
        raise ValueError(f'Unknown mode: {mode}')


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


class Repr:
    """Convencience class to automatically add standard ``__repr__()`` and ``__str__()`` functions to class.

    Uses ``__dict__`` property.
    """

    def __repr__(self):
        members = ', '.join(f'{k}={str(v)[:MAX_MEMBER_REPR_LENGTH]}' for k, v in self.__dict__.items())
        return f"{self.__class__.__name__}({members})"

    def __str__(self):
        return self.__repr__()
