from unittest import TestCase

from hypergol.base_data import BaseData
from hypergol.dataset import Dataset
from hypergol.dataset import DatasetFactory


class DataClass(BaseData):

    def __init__(self, id_: int, value: int):
        self.id_ = id_
        self.value = value

    def get_id(self):
        return (self.id_, )


class TestDatasetFactory(TestCase):

    def setUp(self):
        super().setUp()
        self.expectedDataset = Dataset(
            dataType=DataClass,
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
        dataset = datasetFactory.get(dataType=DataClass, name='data_class')
        self.assertDictContainsSubset(self.expectedDataset.__dict__, dataset.__dict__)
