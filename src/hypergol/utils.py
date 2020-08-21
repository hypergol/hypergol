import os
import hashlib
import inspect
from typing import List

from pydantic import create_model           # pylint: disable=no-name-in-module

from hypergol.base_data import BaseData


def create_pydantic_type(type_):
    parameters = {}
    for parameter, parameterData in inspect.signature(type_.__init__).parameters.items():
        if parameter != 'self':
            parameterType = parameterData.annotation
            if getattr(parameterType, '_name', None) == 'List':
                if issubclass(parameterType.__args__[0], BaseData):
                    parameterType = List[create_pydantic_type(parameterType.__args__[0])]
            elif issubclass(parameterType, BaseData):
                parameterType = create_pydantic_type(parameterType)
            parameters[parameter] = (parameterType, ...)
    return create_model(type_.__name__, **parameters)


def get_hash(data):
    if not isinstance(data, (str, int, tuple)):
        raise ValueError(f'Wrong type in get_hash() {data.__class__.__name__}')
    if isinstance(data, (str, int)):
        data = [data]
    hasher = hashlib.sha1(''.encode('utf-8'))
    for value in data:
        if not isinstance(value, (str, int)):
            raise ValueError(f'get_hash was called with type {value.__class__.__name__}')
        hasher.update(str(value).encode('utf-8'))
    return hasher.hexdigest()


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
