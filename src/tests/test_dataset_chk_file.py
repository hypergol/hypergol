import json
from tests.hypergol_test_case import DataClass1
from tests.hypergol_test_case import HypergolTestCase
from hypergol.dataset_chk_file import DatasetChecksumMismatchException


class TestDatasetChkFile(HypergolTestCase):

    def __init__(self, methodName='runTest'):
        super(TestDatasetChkFile, self).__init__(
            location='test_dataset_chk_file_location',
            projectName='test_dataset_chk_file',
            branch='branch',
            chunkCount=16,
            methodName=methodName
        )

    def setUp(self):
        super().setUp()
        self.expectedObjects = {DataClass1(id_=k, value1=k) for k in range(100)}
        self.dataset = self.create_test_dataset(
            dataset=self.datasetFactory.get(dataType=DataClass1, name='data_class'),
            content=self.expectedObjects
        )

    def tearDown(self):
        super().tearDown()
        self.delete_if_exists(dataset=self.dataset)
        self.clean_directories()

    def test_dataset_correctly_locates_chk_file(self):
        self.assertEqual(self.dataset.chkFile.chkFilename, f'{self.location}/{self.projectName}/{self.branch}/data_class/data_class.chk')

    def test_dataset_check_chk_file_returns_true_if_correct(self):
        self.assertEqual(self.dataset.chkFile.check_chk_file(), True)

    def test_dataset_check_chk_file_raises_error_if_checksum_mismatch(self):
        chkFileData = json.loads(open(self.dataset.chkFile.chkFilename, 'rt').read())
        chkFileData[f'{self.dataset.name}_0.jsonl.gz'] = chkFileData[f'{self.dataset.name}_1.jsonl.gz']
        open(self.dataset.chkFile.chkFilename, 'wt').write(json.dumps(chkFileData, sort_keys=True, indent=4))
        with self.assertRaises(DatasetChecksumMismatchException):
            self.dataset.chkFile.check_chk_file()
