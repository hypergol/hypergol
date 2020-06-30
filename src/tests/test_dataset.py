import os
import json
from pathlib import PosixPath

from tests.hypergol_test_case import HypergolTestCase
from tests.hypergol_test_case import DataClass1
from tests.hypergol_test_case import DataClass2
from hypergol.dataset import DatasetWriter
from hypergol.dataset import DatasetReader
from hypergol.dataset import DatasetDoesNotExistException
from hypergol.dataset import DatasetAlreadyExistsException
from hypergol.dataset import DatasetDefFileDoesNotMatchException
from hypergol.dataset import DatasetTypeDoesNotMatchDataTypeException
from hypergol.dataset import DatasetChecksumMismatchException


class TestDataset(HypergolTestCase):

    def __init__(self, methodName='runTest'):
        super(TestDataset, self).__init__(
            location='test_dataset_location',
            project='test_dataset',
            branch='branch',
            chunks=16,
            methodName=methodName
        )

    def setUp(self):
        super().setUp()
        self.expectedObjects = {DataClass1(id_=k, value1=k) for k in range(100)}
        self.dataset = self.create_test_dataset(
            dataset=self.datasetFactory.get(dataType=DataClass1, name='data_class'),
            content=self.expectedObjects
        )
        self.datasetNew = self.datasetFactory.get(dataType=DataClass1, name='data_class_new')

    def tearDown(self):
        super().tearDown()
        self.delete_if_exists(dataset=self.dataset)
        self.delete_if_exists(dataset=self.datasetNew)
        self.clean_directories()

    def test_dataset_directory_returns_correctly(self):
        self.assertEqual(self.dataset.directory, PosixPath(f'{self.location}/{self.project}/{self.branch}/data_class'))

    def test_dataset_correctly_locates_def_file(self):
        self.assertEqual(self.dataset.defFilename, f'{self.location}/{self.project}/{self.branch}/data_class/data_class.def')

    def test_dataset_correctly_locates_chk_file(self):
        self.assertEqual(self.dataset.chkFilename, f'{self.location}/{self.project}/{self.branch}/data_class/data_class.chk')

    def test_dataset_exists_returns_true_if_exists(self):
        self.assertEqual(self.dataset.exists(), True)

    def test_dataset_exists_returns_false_if_does_not_exists(self):
        self.assertEqual(self.datasetNew.exists(), False)

    def test_dataset_check_def_file_returns_true_if_correct(self):
        self.assertEqual(self.dataset.check_def_file(), True)

    def test_dataset_check_chk_file_returns_true_if_correct(self):
        self.assertEqual(self.dataset.check_chk_file(), True)

    def test_dataset_check_chk_file_raises_error_if_checksum_mismatch(self):
        chkFileData = json.loads(open(self.dataset.chkFilename, 'rt').read())
        chkFileData[f'{self.dataset.name}_0.json.gz'] = chkFileData[f'{self.dataset.name}_1.json.gz']
        open(self.dataset.chkFilename, 'wt').write(json.dumps(chkFileData, sort_keys=True, indent=4))
        with self.assertRaises(DatasetChecksumMismatchException):
            self.dataset.check_chk_file()

    def test_open_returns_datawriter_and_opened_chunks_if_w_mode(self):
        datasetWriter = self.datasetNew.open('w')
        expectedFilenames = {f'{k:0x}': f'{self.datasetNew.directory}/data_class_new_{k:0x}.json.gz' for k in range(16)}
        filenames = {dataChunkId: dataChunk.file.name for dataChunkId, dataChunk in datasetWriter.dataChunks.items()}
        self.assertEqual(type(datasetWriter), DatasetWriter)
        self.assertEqual(datasetWriter.dataset, self.datasetNew)
        self.assertEqual(expectedFilenames, filenames)

    def test_open_returns_datareader_and_unopened_chunks_if_r_mode(self):
        datasetReader = self.dataset.open('r')
        expectedDataChunkIds = {f'{k:0x}' for k in range(16)}
        self.assertEqual(type(datasetReader), DatasetReader)
        self.assertEqual(datasetReader.dataset, self.dataset)
        for dataChunk in datasetReader.dataChunks:
            self.assertIsNone(dataChunk.file)
        self.assertSetEqual({dataChunk.chunkId for dataChunk in datasetReader.dataChunks}, expectedDataChunkIds)

    def test_init_in_read_mode_fails_if_dataset_does_not_exist(self):
        with self.assertRaises(DatasetDoesNotExistException):
            self.datasetNew.init(mode='r')

    def test_init_in_read_mode_fails_if_existing_dataset_def_does_not_match(self):
        differentDataset = self.datasetFactory.get(dataType=DataClass1, name='data_class', chunks=256)
        with self.assertRaises(DatasetDefFileDoesNotMatchException):
            differentDataset.init(mode='r')

    def test_init_in_write_mode_fails_if_dataset_already_exist(self):
        with self.assertRaises(DatasetAlreadyExistsException):
            self.dataset.init(mode='w')

    def test_get_chunks_returns_the_right_chunks(self):
        dataChunks = self.dataset.get_data_chunks(mode='r')
        for dataChunk in dataChunks:
            self.assertEqual(dataChunk.dataset, self.dataset)
            self.assertIsNone(dataChunk.file)
        self.assertSetEqual({dataChunk.chunkId for dataChunk in dataChunks}, {f'{k:0x}' for k in range(16)})

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
                datasetWriter.append(DataClass2(id_=0, value2=0))
