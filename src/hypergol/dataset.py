import os
import glob
import gzip
import json
import hashlib

from datetime import datetime
from pathlib import Path

from hypergol.utils import Repr
from hypergol.base_data import BaseData

VALID_CHUNKS = {16: 1, 256: 2, 4096: 3}
CHECKSUM_BUFFER_SIZE = 128*1024


class DatasetTypeDoesNotMatchDataTypeException(Exception):
    pass


class DatasetDoesNotExistException(Exception):
    pass


class DatasetAlreadyExistsException(Exception):
    pass


class DatasetDefFileDoesNotMatchException(Exception):
    pass


class DatasetChecksumMismatchException(Exception):
    pass


def _get_hash(data):
    if isinstance(data, (str, int)):
        data = [data]
    hasher = hashlib.sha1(''.encode('utf-8'))
    for value in data:
        if not isinstance(value, (str, int)):
            raise ValueError(f'_get_hash was called with type {value.__class__.__name__}')
        hasher.update(str(value).encode('utf-8'))
    return hasher.hexdigest()


class RepoData(BaseData):

    def __init__(self, branchName, commitHash, commitMessage, comitterName, comitterEmail):
        self.branchName = branchName
        self.commitHash = commitHash
        self.commitMessage = commitMessage
        self.comitterName = comitterName
        self.comitterEmail = comitterEmail


class DataChunkChecksum(Repr):

    def __init__(self, chunk, value):
        self.chunk = chunk
        self.value = value


class DataChunk(Repr):

    def __init__(self, dataset, chunkId, mode):
        self.dataset = dataset
        self.chunkId = chunkId
        self.mode = mode
        self.file = None
        self.hasher = None
        self.checksum = None

    @property
    def fileName(self):
        return f'{self.dataset.name}_{self.chunkId}.json.gz'

    def open(self):
        fileName = f'{self.dataset.directory}/{self.fileName}'
        self.file = gzip.open(fileName, f'{self.mode}t')
        self.hasher = hashlib.sha1((self.checksum or '').encode('utf-8'))
        return self

    def close(self):
        self.file.close()
        self.file = None
        self.checksum = self.hasher.hexdigest()
        self.hasher = None
        return DataChunkChecksum(chunk=self, value=self.checksum)

    def append(self, value):
        if not isinstance(value, self.dataset.dataType):
            raise DatasetTypeDoesNotMatchDataTypeException(f"Trying to append an object of type {value.__class__.__name__} into a dataset of type {self.dataset.dataType.__name__}")
        if self.dataset.get_object_chunk_id(value.get_hash_id()) != self.chunkId:
            raise ValueError(f'Incorrect hashId {self.dataset.get_object_chunk_id(value)} was inserted into {self.dataset.name} chunk {self.chunkId}.')
        self.write(f'{json.dumps(value.to_data(), sort_keys=True)}\n')

    def write(self, data):
        self.hasher.update(data.encode('utf-8'))
        self.file.write(data)

    def __iter__(self):
        for line in self.file:
            yield self.dataset.dataType.from_data(json.loads(line.rstrip()))


class Dataset(Repr):

    def __init__(self, dataType, location, project, branch, name, repoData, chunkCount=16):
        self.dataType = dataType
        self.location = location
        self.project = project
        self.branch = branch
        self.name = name
        self.chunkCount = chunkCount
        self.dependencies = []
        self.repoData = repoData

    def add_dependency(self, dataset):
        self.dependencies.append(dataset)

    @property
    def directory(self):
        return Path(self.location, self.project, self.branch, self.name)

    @property
    def defFilename(self):
        return f'{self.directory}/{self.name}.def'

    @property
    def chkFilename(self):
        return f'{self.directory}/{self.name}.chk'

    def get_chk_file_data(self):
        return json.loads(open(self.chkFilename, 'rt').read())

    def get_checksum(self):
        return _get_hash(data=self.get_chk_file_data())

    def make_chk_file(self, checksums):
        chkData = {checksum.chunk.fileName: checksum.value for checksum in checksums}
        chkData[f'{self.name}.def'] = _get_hash(open(self.defFilename, 'rt').read())
        chkDataString = json.dumps(chkData, sort_keys=True, indent=4)
        with open(self.chkFilename, 'wt') as chkFile:
            chkFile.write(chkDataString)

    def check_chk_file(self):
        chkFileData = self.get_chk_file_data()
        mv = memoryview(bytearray(CHECKSUM_BUFFER_SIZE))
        for fileName, chkFileChecksum in chkFileData.items():
            if fileName.endswith('.def'):
                data = open(self.defFilename, 'rt').read()
                actualChecksum = _get_hash(data)
            else:
                hasher = hashlib.sha1(''.encode('utf-8'))
                with gzip.open(f'{self.directory}/{fileName}', 'rb') as f:
                    for n in iter(lambda: f.readinto(mv), 0):   # pylint: disable=cell-var-from-loop
                        hasher.update(mv[:n])
                actualChecksum = hasher.hexdigest()
            if chkFileChecksum != actualChecksum:
                raise DatasetChecksumMismatchException(f'Checksum error {self.name} for {fileName}: chkFile: {chkFileChecksum}, actual: {actualChecksum}')
        return True

    def get_def_file_data(self):
        return json.loads(open(self.defFilename, 'rt').read())

    def make_def_file(self):
        dependencyData = []
        for dataset in self.dependencies:
            data = dataset.get_def_file_data()
            data['chkFileChecksum'] = dataset.get_checksum()
            dependencyData.append(data)
        defData = {
            'dataType': self.dataType.__name__,
            'project': self.project,
            'branch': self.branch,
            'name': self.name,
            'chunkCount': self.chunkCount,
            'creationTime': datetime.now().isoformat(),
            'dependencies': dependencyData,
            'repo': self.repoData.to_data()
        }
        self.directory.mkdir(parents=True, exist_ok=True)
        with open(self.defFilename, 'wt') as defFile:
            defFile.write(json.dumps(defData, sort_keys=True, indent=4))

    def check_def_file(self):
        defFileData = self.get_def_file_data()
        isDefValuesMatch = (
            defFileData['dataType'] == self.dataType.__name__ and
            defFileData['project'] == self.project and
            defFileData['branch'] == self.branch and
            defFileData['name'] == self.name and
            defFileData['chunkCount'] == self.chunkCount
        )
        if not isDefValuesMatch:
            raise DatasetDefFileDoesNotMatchException('The defintion of the dataset class does not match the def file')
        return True

    def init(self, mode):
        if mode == 'w':
            if self.exists():
                raise DatasetAlreadyExistsException(f"Dataset {self.defFilename} already exist, delete the dataset first with Dataset.delete()")
            self.make_def_file()
        elif mode == 'r':
            if not self.exists():
                raise DatasetDoesNotExistException(f'Dataset {self.name} does not exist')
            self.check_def_file()
        else:
            raise ValueError(f'Invalid mode: {mode} in {self.name}')

    def open(self, mode):
        if mode == 'w':
            return DatasetWriter(dataset=self)
        if mode == 'r':
            return DatasetReader(dataset=self)
        raise ValueError(f'Invalid mode: {mode} in {self.name}')

    def get_data_chunks(self, mode):
        def _get_chunk_ids():
            return [f'{k:0{VALID_CHUNKS[self.chunkCount]}x}' for k in range(self.chunkCount)]

        self.init(mode=mode)
        return [DataChunk(dataset=self, chunkId=chunkId, mode=mode) for chunkId in _get_chunk_ids()]

    def get_object_chunk_id(self, objectId):
        return _get_hash(objectId)[:VALID_CHUNKS[self.chunkCount]]

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
        self.dataChunks = self.dataset.get_data_chunks(mode='r')

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass

    def __iter__(self):
        for chunk in self.dataChunks:
            try:
                chunk.open()
                for elem in chunk:
                    yield elem
            finally:
                chunk.close()


class DatasetWriter(Repr):

    def __init__(self, dataset):
        self.dataset = dataset
        self.dataChunks = {dataChunk.chunkId: dataChunk.open() for dataChunk in self.dataset.get_data_chunks(mode='w')}

    def append(self, elem):
        chunkHash = self.dataset.get_object_chunk_id(elem.get_hash_id())
        self.dataChunks[chunkHash].append(elem)

    def close(self):
        checksums = []
        for chunk in self.dataChunks.values():
            checksum = chunk.close()
            checksums.append(checksum)
        self.dataset.make_chk_file(checksums=checksums)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


class DatasetFactory(Repr):

    def __init__(self, location, project, branch, chunkCount, repoData):
        self.location = location
        self.project = project
        self.branch = branch
        self.chunkCount = chunkCount
        self.repoData = repoData

    def get(self, dataType, name, chunkCount=None):
        return Dataset(
            dataType=dataType,
            location=self.location,
            project=self.project,
            branch=self.branch,
            name=name,
            chunkCount=chunkCount or self.chunkCount,
            repoData=self.repoData
        )
