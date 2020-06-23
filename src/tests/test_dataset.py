import os
from pathlib import PosixPath
from unittest import TestCase

from hypergol.base_data import BaseData
from hypergol.dataset import Dataset
from hypergol.dataset import DatasetWriter
from hypergol.dataset import DatasetReader
from hypergol.dataset import DatasetDoesNotExistException
from hypergol.dataset import DatasetAlreadyExistsException
from hypergol.dataset import DatasetDefFileDoesNotMatchException
from hypergol.dataset import DatasetTypeDoesNotMatchDataTypeException


class DataClass(BaseData):

    def __init__(self, id_: int, value: int):
        self.id_ = id_
        self.value = value

    def get_id(self):
        return (self.id_, )

    def __hash__(self):
        return hash(self.id_)


class OtherDataClass(BaseData):

    def __init__(self, id_: int, value: int):
        self.id_ = id_
        self.value = value

    def get_id(self):
        return (self.id_, )


class TestDataset(TestCase):

    def setUp(self):
        super().setUp()
        self.dataset = Dataset(
            dataType=DataClass,
            location='test_dataset_location',
            project='test_dataset',
            branch='branch',
            name='data_class',
            chunks=16
        )
        self.expectedObjects = {DataClass(id_=k, value=k) for k in range(100)}
        if not self.dataset.exists():
            with self.dataset.open('w') as ds:
                for v in self.expectedObjects:
                    ds.append(v)
        self.datasetNew = Dataset(
            dataType=DataClass,
            location='test_dataset_location',
            project='test_dataset',
            branch='branch',
            name='data_class_new',
            chunks=16
        )

    def tearDown(self):
        super().tearDown()
        if self.dataset.exists():
            self.dataset.delete()
        if self.datasetNew.exists():
            self.datasetNew.delete()
        try:
            os.rmdir(f'{self.dataset.location}/{self.dataset.project}/{self.dataset.branch}')
        except FileNotFoundError:
            pass
        try:
            os.rmdir(f'{self.dataset.location}/{self.dataset.project}')
        except FileNotFoundError:
            pass
        try:
            os.rmdir(f'{self.dataset.location}')
        except FileNotFoundError:
            pass

    def test_dataset_directory_returns_correctly(self):
        self.assertEqual(self.dataset.directory, PosixPath('test_dataset_location/test_dataset/branch/data_class'))

    def test_dataset_correctly_locates_def_file(self):
        self.assertEqual(self.dataset.defFilename, 'test_dataset_location/test_dataset/branch/data_class/data_class.def')

    def test_dataset_exists_returns_true_if_exists(self):
        self.assertEqual(self.dataset.exists(), True)

    def test_dataset_exists_returns_false_if_does_not_exists(self):
        self.assertEqual(self.datasetNew.exists(), False)

    def test_open_returns_datawriter_and_opened_chunks_if_w_mode(self):
        datasetWriter = self.datasetNew.open('w')
        expectedFilenames = {f'{k:0x}': f'{self.datasetNew.directory}/data_class_new_{k:0x}.json.gz' for k in range(16)}
        filenames = {chunkId: chunk.file.name for chunkId, chunk in datasetWriter.chunks.items()}
        self.assertEqual(type(datasetWriter), DatasetWriter)
        self.assertEqual(datasetWriter.dataset, self.datasetNew)
        self.assertEqual(expectedFilenames, filenames)

    def test_open_returns_datareader_and_unopened_chunks_if_r_mode(self):
        datasetReader = self.dataset.open('r')
        expectedChunkIds = {f'{k:0x}' for k in range(16)}
        self.assertEqual(type(datasetReader), DatasetReader)
        self.assertEqual(datasetReader.dataset, self.dataset)
        for chunk in datasetReader.chunks:
            self.assertIsNone(chunk.file)
        self.assertSetEqual({chunk.chunkId for chunk in datasetReader.chunks}, expectedChunkIds)

    def test_init_in_read_mode_fails_if_dataset_does_not_exist(self):
        with self.assertRaises(DatasetDoesNotExistException):
            self.datasetNew.init(mode='r')

    def test_init_in_read_mode_fails_if_existing_dataset_def_does_not_match(self):
        differentDataset = Dataset(
            dataType=DataClass,
            location='test_dataset_location',
            project='test_dataset',
            branch='branch',
            name='data_class',
            chunks=256
        )
        with self.assertRaises(DatasetDefFileDoesNotMatchException):
            differentDataset.init(mode='r')

    def test_init_in_write_mode_fails_if_dataset_already_exist(self):
        with self.assertRaises(DatasetAlreadyExistsException):
            self.dataset.init(mode='w')

    def test_get_chunks_returns_the_right_chunks(self):
        chunks = self.dataset.get_chunks(mode='r')
        for chunk in chunks:
            self.assertEqual(chunk.dataset, self.dataset)
            self.assertIsNone(chunk.file)
        self.assertSetEqual({chunk.chunkId for chunk in chunks}, {f'{k:0x}' for k in range(16)})

    def test_dataset_reader_reads_correctly(self):
        objects = set(self.dataset.open('r'))
        self.assertSetEqual(objects, self.expectedObjects)

    def test_dataset_reader_reads_correctly_with_context_manager(self):
        objects = set()
        with self.dataset.open('r') as datasetReader:
            for value in datasetReader:
                objects.add(value)
        self.assertSetEqual(objects, self.expectedObjects)

    def test_dataset_writer_writes_correctly_with_context_manager(self):
        with self.datasetNew.open('w') as datasetWriter:
            for value in self.expectedObjects:
                datasetWriter.append(value)
        objects = set(self.dataset.open('r'))
        self.assertSetEqual(objects, self.expectedObjects)

    def test_delete_fails_if_dataset_not_exist(self):
        with self.assertRaises(DatasetDoesNotExistException):
            self.datasetNew.delete()

    def test_delete_deletes_files_and_directory(self):
        self.dataset.delete()
        self.assertEqual(os.path.exists(self.dataset.directory), False)

    def test_data_chunk_append_raises_error_if_type_does_not_match(self):
        with self.assertRaises(DatasetTypeDoesNotMatchDataTypeException):
            with self.datasetNew.open('w') as datasetWriter:
                datasetWriter.append(OtherDataClass(id_=0, value=0))
