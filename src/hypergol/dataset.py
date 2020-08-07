import os
import glob
import gzip
import json
import hashlib

from datetime import datetime
from pathlib import Path

from hypergol.utils import Repr
from hypergol.utils import _get_hash
from hypergol.base_data import BaseData
from hypergol.dataset_chkfile import DataSetChkFile

VALID_CHUNKS = {16: 1, 256: 2, 4096: 3}


class DatasetTypeDoesNotMatchDataTypeException(Exception):
    pass


class DatasetDoesNotExistException(Exception):
    pass


class DatasetAlreadyExistsException(Exception):
    pass


class DatasetDefFileDoesNotMatchException(Exception):
    pass


class RepoData(BaseData):
    """Stores the information about the repository in the dataset"""

    def __init__(self, branchName, commitHash, commitMessage, comitterName, comitterEmail):
        """
        Parameters
        ----------
        branchName : str
        commitHash : str
        commitMessage : str
        comitterName : str
        comitterEmail : str
        """
        self.branchName = branchName
        self.commitHash = commitHash
        self.commitMessage = commitMessage
        self.comitterName = comitterName
        self.comitterEmail = comitterEmail

    @classmethod
    def get_dummy(cls):
        """Creates an empty RepoData if the Dataset was created outside a git repository"""
        print('Dummy repodata was used, data lineage disabled')
        return RepoData(
            branchName='dummy',
            commitHash='0000000000000000000000000000000000000000',
            commitMessage='dummy',
            comitterName='Dummy Dummy',
            comitterEmail='dummy@dummy.com'
        )


class DataChunkChecksum(Repr):

    def __init__(self, chunk, value):
        self.chunk = chunk
        self.value = value


class DataChunk(Repr):
    """This class represents the file that the data is actually stored in.

    When opened for writing it implements the :func:`append()` method and when reading the :func:`__iter__` iterator. Upon close it returns the checksum (SHA1 hash) of the the content that was written into it.

    """

    def __init__(self, dataset, chunkId, mode):
        """
        Parameters
        ----------
        dataset : Dataset
            The dataset this class chunk belongs to
        chunkId : str
            The hexadecimal identified of this chunk
        mode : str = ('w' or 'r')
            The mode this chunk was created to be opened in, determined by :func:`Dataset.get_data_chunks()`
        """
        self.dataset = dataset
        self.chunkId = chunkId
        self.mode = mode
        self.file = None
        self.hasher = None
        self.checksum = None

    @property
    def fileName(self):
        """Name of the file the data will be stored"""
        return f'{self.dataset.name}_{self.chunkId}.jsonl.gz'

    def open(self):
        """Opens the chunk according to the mode specified at creation"""
        fileName = f'{self.dataset.directory}/{self.fileName}'
        self.file = gzip.open(fileName, f'{self.mode}t')
        self.hasher = hashlib.sha1((self.checksum or '').encode('utf-8'))
        return self

    def close(self):
        """Closes the file handler and gets the checksum and returns it as ``DataChunkChecksum`` object"""
        self.file.close()
        self.file = None
        self.checksum = self.hasher.hexdigest()
        self.hasher = None
        return DataChunkChecksum(chunk=self, value=self.checksum)

    def append(self, value):
        """Adds a datamodel object to the file, raises error if the type doesn't match the dataset's type or the hash of the object doesn't match the chunkId

        Parameters
        ----------
        value : object
            Datamodel object matching the type of the Dataset this chunk belongs to
        """
        if not isinstance(value, self.dataset.dataType):
            raise DatasetTypeDoesNotMatchDataTypeException(f"Trying to append an object of type {value.__class__.__name__} into a dataset of type {self.dataset.dataType.__name__}")
        if self.dataset.get_object_chunk_id(value.get_hash_id()) != self.chunkId:
            raise ValueError(f'Incorrect hashId {self.dataset.get_object_chunk_id(value)} was inserted into {self.dataset.name} chunk {self.chunkId}.')
        self.write(data=f'{json.dumps(value.to_data(), sort_keys=True)}\n')

    def write(self, data):
        """Writes into the file and updates the hash, used in multithreaded rechunking in :class:`Task`"""
        self.hasher.update(data.encode('utf-8'))
        self.file.write(data)

    def __iter__(self):
        """Iterator to read all the data from the file"""
        for line in self.file:
            yield self.dataset.dataType.from_data(json.loads(line.rstrip()))


class Dataset(Repr):
    """
    Dataset class to store BaseData objects that is readable/writable in a parallel manner.

    Files will be stored in: ``location/project/branch/name/name_???.jsonl.gz``

    """

    def __init__(self, dataType, location, project, branch, name, repoData=None, chunkCount=16):
        """
        Parameters
        ----------
        dataType : BaseData
            Type of this dataset, only ``dataType`` objects can be stored in this dataset
        location : str
            path the project is in
        project : str
            project name
        branch : str
            branch name
        name : str
            name of this dataset
        repoData : RepoData = None
            stores the commit information at the creation of the dataset
        chunkCount : int = {16 ( default), 256, 4096}
            How many files the data will be stored in, sets the granularity of multithreaded processing
        """
        self.dataType = dataType
        self.location = location
        self.project = project
        self.branch = branch
        self.name = name
        self.chunkCount = chunkCount
        self.dependencies = []
        self.repoData = repoData or RepoData.get_dummy()
        self.chkFile = DataSetChkFile(dataset=self)

    def add_dependency(self, dataset):
        """Adds the ``.def`` file of a dataset to the ``.def`` file of this dataset so data lineage can be retraced

        Parameters
        ----------
        dataset : Dataset
            dataset that contributes to the generation of this dataset
        """
        self.dependencies.append(dataset)

    @property
    def directory(self):
        """Full path of the directory this dataset will be in"""
        return Path(self.location, self.project, self.branch, self.name)

    @property
    def defFilename(self):
        """Full path of the definition file for this dataset"""
        return f'{self.directory}/{self.name}.def'

    def get_def_file_data(self):
        """Loads the data from the ``.def`` file"""
        return json.loads(open(self.defFilename, 'rt').read())

    def make_def_file(self):
        """Creates the ``.def`` file, adds the dependencies ``.def`` data with that dataset's own checksum (which is the SHA1 of the contend of that dataset's ``.chk`` file)
        """
        dependencyData = []
        for dataset in self.dependencies:
            data = dataset.get_def_file_data()
            data['chkFileChecksum'] = dataset.chkFile.get_checksum()
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
        """Checks if a dataset already exists the definition of the object matches to that on disk"""
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
        """Checks the existence of the dataset

        Parameters
        ----------
        mode : str = ('w', 'r')
            The mode the dataset is about to be opened


        Based on the mode if

        - mode=='w' : fails if the dataset already exists otherwise creates the ``.def`` file
        - mode=='r' : fails if the dataset doesn't exist otherwise compares the data in the ``.def.`` file to the definiton in the class.
        - otherwise : fails due to unknown mode
        """
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
        """Opens the dataset for reading or writing

        Parameters
        ----------
        mode : str = ('w', 'r')
            The mode the dataset is about to be opened


        Returns a :class:`DatasetWriter` or :class:`DatasetReader` object that handles the reading or writing of the files through the dataset's chunks.
        """
        if mode == 'w':
            return DatasetWriter(dataset=self)
        if mode == 'r':
            return DatasetReader(dataset=self)
        raise ValueError(f'Invalid mode: {mode} in {self.name}')

    def get_chunk_ids(self):
        """Returns the list of :term:`chunk id`-s """
        return [f'{k:0{VALID_CHUNKS[self.chunkCount]}x}' for k in range(self.chunkCount)]

    def get_data_chunks(self, mode):
        """Initialises the dataset and creates all the :class:`Datachunk` classes"""
        self.init(mode=mode)
        return [
            DataChunk(dataset=self, chunkId=chunkId, mode=mode)
            for chunkId in self.get_chunk_ids()
        ]

    def get_object_chunk_id(self, objectHashId):
        """Finds out which chunk the object belongs based on the :term:`hash id` """
        return _get_hash(objectHashId)[:VALID_CHUNKS[self.chunkCount]]

    def delete(self):
        """Deletes the files and the directory of the dataset"""
        if not self.exists():
            raise DatasetDoesNotExistException(f'Dataset {self.name} does not exist')
        for filename in glob.glob(f'{self.directory}/*'):
            os.remove(filename)
        os.rmdir(self.directory)

    def exists(self):
        """True if the dataset's ``.def`` file exists"""
        return os.path.exists(self.defFilename)


class DatasetReader(Repr):
    """Class to read from a dataset

    Implements context manager and iterator, doesn't open any file until reading actually happen and then opens each chunk one by one.
    """

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
    """Class to write into a dataset"""

    def __init__(self, dataset):
        """Opens all chunks at once and puts them in a dictionary for easy lookup

        Implements context manager for proper file open/close.

        Parameters
        ----------
        dataset : Dataset
            dataset to be written into, at this point it is already established that it doesn't yet exists
        """
        self.dataset = dataset
        self.dataChunks = {dataChunk.chunkId: dataChunk.open() for dataChunk in self.dataset.get_data_chunks(mode='w')}

    def append(self, elem):
        """Writes a single object into the right chunks"""
        chunkHash = self.dataset.get_object_chunk_id(elem.get_hash_id())
        self.dataChunks[chunkHash].append(elem)

    def close(self):
        """Closes the files and writes the ``.chk`` file"""
        checksums = []
        for chunk in self.dataChunks.values():
            checksum = chunk.close()
            checksums.append(checksum)
        self.dataset.chkFile.make_chk_file(checksums=checksums)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


class DatasetFactory(Repr):
    """Convenience class to create lots of datasets at once. Used in pipelines where multiple datasets are created into the same location, project, branch
    """

    def __init__(self, location, project, branch, chunkCount, repoData=None):
        """
        Parameters
        ----------
        location : str
            path the project is in
        project : str
            project name
        branch : str
            branch name
        repoData : RepoData
            stores the commit information at the creation of the dataset
        chunkCount : int = {16 , 256, 4096}
            How many files the data will be stored in, sets the granularity of multithreaded processing
        """
        self.location = location
        self.project = project
        self.branch = branch
        self.chunkCount = chunkCount
        self.repoData = repoData or RepoData.get_dummy()

    def get(self, dataType, name, chunkCount=None):
        """Creates a dataset with the parameters given and the factory's own parameters

        Parameters
        ----------
        dataType : BaseData
            Type of the dataset
        name : str
            Name of the dataset (recommended to be in snakecase)
        chunkCount : int=None
            Number of chunks, if None, the factory's own value will be used
        """
        return Dataset(
            dataType=dataType,
            location=self.location,
            project=self.project,
            branch=self.branch,
            name=name,
            chunkCount=chunkCount or self.chunkCount,
            repoData=self.repoData
        )
