from unittest import TestCase

from tests.hypergol_test_case import DataClass1
from hypergol.base_data import BaseData
from hypergol.dataset import Dataset
from hypergol.dataset import DatasetFactory


class TestDatasetFactory(TestCase):

    def setUp(self):
        super().setUp()
        self.expectedDataset = Dataset(
            dataType=DataClass1,
            location='.',
            project='test_x',
            branch='branch',
            name='data_class',
            chunks=256
        )

    def test_dataset_factory_returns_correct_dataset(self):
        datasetFactory = DatasetFactory(
            location=self.expectedDataset.location,
            project=self.expectedDataset.project,
            branch=self.expectedDataset.branch,
            chunks=self.expectedDataset.chunks
        )
        dataset = datasetFactory.get(dataType=DataClass1, name='data_class')
        self.assertEqual(type(dataset), Dataset)
        self.assertDictContainsSubset(self.expectedDataset.__dict__, dataset.__dict__)
