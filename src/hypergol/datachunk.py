import gzip
import json
import hashlib

from hypergol.repr import Repr


class DatasetTypeDoesNotMatchDataTypeException(Exception):
    pass


class DataChunkChecksum(Repr):

    def __init__(self, chunk, value):
        self.chunk = chunk
        self.value = value


class DataChunk(Repr):
    """This class represents the file that the data is actually stored in

    When opened for writing it implements the :func:`append()` method and when reading the :func:`__iter__` iterator. Upon close, it returns the checksum (SHA1 hash) of the content that was written into it.

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
        """Adds a data model object to the file, raises an error if the type doesn't match the dataset's type or the hash of the object doesn't match the chunkId

        Parameters
        ----------
        value : object
            Data model object matching the type of the Dataset this chunk belongs to
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
