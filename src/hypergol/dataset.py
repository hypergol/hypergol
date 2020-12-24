import os
import glob
from pathlib import Path

from hypergol.datachunk import DataChunk
from hypergol.repr import Repr
from hypergol.utils import get_hash
from hypergol.repo_data import RepoData
from hypergol.dataset_chk_file import DataSetChkFile
from hypergol.dataset_def_file import DataSetDefFile

VALID_CHUNKS = {16: 1, 256: 2, 4096: 3}


class DatasetDoesNotExistException(Exception):
    pass


class DatasetAlreadyExistsException(Exception):
    pass


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

        self.repoData = repoData or RepoData.get_dummy()
        self.chkFile = DataSetChkFile(dataset=self)
        self.defFile = DataSetDefFile(dataset=self)

    def add_dependency(self, dataset):
        """Adds the ``.def`` file of a dataset to the ``.def`` file of this dataset so data lineage can be retraced

        Parameters
        ----------
        dataset : Dataset
            dataset that contributes to the generation of this dataset
        """
        self.defFile.add_dependency(dataset)

    @property
    def directory(self):
        """Full path of the directory this dataset will be in"""
        return Path(self.location, self.project, self.branch, self.name)

    def init(self, mode):
        """Checks the existence of the dataset

        Parameters
        ----------
        mode : str = ('w', 'r')
            The mode the dataset is about to be opened


        Based on the mode if

        - mode=='w' : fails if the dataset already exists otherwise creates the ``.def`` file
        - mode=='r' : fails if the dataset doesn't exist otherwise compares the data in the ``.def.`` file to the definition in the class.
        - otherwise : fails due to unknown mode
        """
        if mode == 'w':
            if self.exists():
                raise DatasetAlreadyExistsException(f"Dataset {self.directory} already exist, delete the dataset first with Dataset.delete()")
            self.defFile.make_def_file()
        elif mode == 'r':
            if not self.exists():
                raise DatasetDoesNotExistException(f'Dataset {self.directory} does not exist')
            self.defFile.check_def_file()
        else:
            raise ValueError(f'Invalid mode: {mode} in {self.directory}')

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
        return get_hash(objectHashId)[:VALID_CHUNKS[self.chunkCount]]

    def delete(self):
        """Deletes the files and the directory of the dataset"""
        if not self.exists():
            raise DatasetDoesNotExistException(f'Dataset {self.name} does not exist')
        for filename in glob.glob(f'{self.directory}/*'):
            os.remove(filename)
        os.rmdir(self.directory)

    def exists(self):
        """True if the dataset's ``.def`` file exists"""
        return os.path.exists(self.defFile.defFilename)


class DatasetReader(Repr):
    """Class to read from a dataset

    Implements context manager and iterator. It doesn't open any file until any reading actually happens and then opens each chunk one by one.
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
            Dataset to be written into, at this point it is already established that it doesn't yet exist.
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
