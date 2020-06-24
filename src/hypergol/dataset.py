import os
import glob
import gzip
import json
import hashlib
from datetime import datetime
from pathlib import Path

from hypergol.utils import Repr

VALID_CHUNKS = {16: 1, 256: 2, 4096: 3}


class DatasetTypeDoesNotMatchDataTypeException(Exception):
    pass


class DatasetDoesNotExistException(Exception):
    pass


class DatasetAlreadyExistsException(Exception):
    pass


class DatasetDefFileDoesNotMatchException(Exception):
    pass


def _get_hash(lst):
    m = hashlib.sha1()
    for v in lst:
        m.update(str(v).encode('utf-8'))
    return m.hexdigest()


class DataChunk(Repr):

    def __init__(self, dataset, chunkId, mode):
        self.dataset = dataset
        self.chunkId = chunkId
        self.mode = mode
        self.file = None

    def open(self):
        fileName = f'{self.dataset.directory}/{self.dataset.name}_{self.chunkId}.json.gz'
        self.file = gzip.open(fileName, f'{self.mode}t')
        return self

    def close(self):
        self.file.close()
        self.file = None

    def append(self, value):
        if not isinstance(value, self.dataset.dataType):
            raise DatasetTypeDoesNotMatchDataTypeException(f"Trying to append an object of type {value.__class__.__name__} into a dataset of type {self.dataset.dataType.__name__}")
        self.file.write(f'{json.dumps(value.to_data())}\n')

    def __iter__(self):
        for line in self.file:
            yield self.dataset.dataType.from_data(json.loads(line.rstrip()))


class Dataset(Repr):

    def __init__(self, dataType, location, project, branch, name, chunks=16):
        self.dataType = dataType
        self.location = location
        self.project = project
        self.branch = branch
        self.name = name
        self.chunks = chunks
        self.chunkIdLength = VALID_CHUNKS[self.chunks]

    @property
    def directory(self):
        return Path(self.location, self.project, self.branch, self.name)

    @property
    def defFilename(self):
        return f'{self.directory}/{self.name}.def'

    def _make_def_file(self):
        self.directory.mkdir(parents=True, exist_ok=True)
        with open(self.defFilename, 'wt') as defFile:
            defData = self.__dict__.copy()
            defData['dataType'] = defData['dataType'].__name__
            defData['creationTime'] = datetime.now().isoformat()
            defFile.write(json.dumps(defData, indent=4))

    def _check_def_file(self):
        with open(self.defFilename, 'rt') as defFile:
            oldDefData = json.loads(defFile.read())
            oldDefData.pop('creationTime', None)
            newDefData = self.__dict__.copy()
            newDefData['dataType'] = newDefData['dataType'].__name__
            if oldDefData != newDefData:
                raise DatasetDefFileDoesNotMatchException(f'The defintion of the dataset class does not match the def file {set(newDefData.items()) ^ set(oldDefData.items())}')

    def init(self, mode):
        if mode == 'w':
            if self.exists():
                raise DatasetAlreadyExistsException(f"Dataset {self.defFilename} already exist, delete the dataset first with Dataset.delete()")
            self._make_def_file()
        elif mode == 'r':
            if not self.exists():
                raise DatasetDoesNotExistException(f'Dataset {self.name} does not exist')
            self._check_def_file()
        else:
            raise ValueError(f'Invalid mode: {mode} in {self.name}')

    def open(self, mode):
        if mode == 'w':
            return DatasetWriter(dataset=self)
        if mode == 'r':
            return DatasetReader(dataset=self)
        raise ValueError(f'Invalid mode: {mode} in {self.name}')

    def get_chunks(self, mode):
        def _get_chunk_ids():
            return [f'{k:0{self.chunkIdLength}x}' for k in range(self.chunks)]

        self.init(mode=mode)
        return [DataChunk(dataset=self, chunkId=chunkId, mode=mode) for chunkId in _get_chunk_ids()]

    def get_object_chunk_id(self, objectId):
        return _get_hash(objectId)[:self.chunkIdLength]

    def delete(self):
        if not self.exists():
            raise DatasetDoesNotExistException(f'Dataset {self.name} does not exist')
        for filename in glob.glob(f'{self.directory}/*'):
            os.remove(filename)
        os.rmdir(self.directory)

    def exists(self):
        return os.path.exists(self.defFilename)


class DatasetReader(Repr):

    def __init__(self, dataset):
        self.dataset = dataset
        self.chunks = self.dataset.get_chunks(mode='r')

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass

    def __iter__(self):
        for chunk in self.chunks:
            try:
                chunk.open()
                for elem in chunk:
                    yield elem
            finally:
                chunk.close()


class DatasetWriter(Repr):

    def __init__(self, dataset):
        self.dataset = dataset
        self.chunks = {chunk.chunkId: chunk.open() for chunk in self.dataset.get_chunks(mode='w')}

    def append(self, elem):
        chunkHash = self.dataset.get_object_chunk_id(elem.get_hash_id())
        self.chunks[chunkHash].append(elem)

    def close(self):
        for chunk in self.chunks.values():
            chunk.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


class DatasetFactory(Repr):

    def __init__(self, location, project, branch, chunks):
        self.location = location
        self.project = project
        self.branch = branch
        self.chunks = chunks

    def get(self, dataType, name, chunks=None):
        return Dataset(
            dataType=dataType,
            location=self.location,
            project=self.project,
            branch=self.branch,
            name=name,
            chunks=chunks or self.chunks
        )
