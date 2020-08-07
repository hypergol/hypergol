from tests.hypergol_test_case import DataClass1
from tests.hypergol_test_case import HypergolTestCase


class TestDatasetDefFile(HypergolTestCase):

    def __init__(self, methodName='runTest'):
        super(TestDatasetDefFile, self).__init__(
            location='test_dataset_def_file_location',
            project='test_dataset_def_file',
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
        self.datasetNew = self.datasetFactory.get(dataType=DataClass1, name='data_class_new')

    def tearDown(self):
        super().tearDown()
        self.delete_if_exists(dataset=self.dataset)
        self.delete_if_exists(dataset=self.datasetNew)
        self.clean_directories()

    def test_dataset_correctly_locates_def_file(self):
        self.assertEqual(self.dataset.defFile.defFilename, f'{self.location}/{self.project}/{self.branch}/data_class/data_class.def')

    def test_dataset_check_def_file_returns_true_if_correct(self):
        self.assertEqual(self.dataset.defFile.check_def_file(), True)
