import os
from unittest import TestCase

from hypergol.base_data import BaseData
from hypergol.dataset import DatasetFactory


# TODO(Laszlo): move all the dataset make/clean code here


class DataClass1(BaseData):

    def __init__(self, id_: int, value1: int):
        self.id_ = id_
        self.value1 = value1

    def get_id(self):
        return (self.id_, )

    def __hash__(self):
        return hash((self.id_, self.value1))


class DataClass2(BaseData):

    def __init__(self, id_: int, value2: int):
        self.id_ = id_
        self.value2 = value2

    def get_id(self):
        return (self.id_, )

    def __hash__(self):
        return hash((self.id_, self.value2))


class HypergolTestCase(TestCase):

    def __init__(self, location, project, branch, chunks, methodName):
        super(HypergolTestCase, self).__init__(methodName)
        self.location = location
        self.project = project
        self.branch = branch
        self.chunks = chunks

    def setUp(self):
        super().setUp()
        self.datasetFactory = DatasetFactory(
            location=self.location,
            project=self.project,
            branch=self.branch,
            chunks=self.chunks
        )

    def tearDown(self):
        super().tearDown()

    @staticmethod
    def create_test_dataset(dataset, content):
        if not dataset.exists():
            with dataset.open('w') as datasetWriter:
                for v in content:
                    datasetWriter.append(v)
        return dataset

    @staticmethod
    def delete_if_exists(dataset):
        if dataset.exists():
            dataset.delete()

    def clean_directories(self):
        try:
            os.rmdir(f'{self.datasetFactory.location}/{self.datasetFactory.project}/{self.datasetFactory.branch}')
        except FileNotFoundError:
            pass
        try:
            os.rmdir(f'{self.datasetFactory.location}/{self.datasetFactory.project}')
        except FileNotFoundError:
            pass
        try:
            os.rmdir(f'{self.datasetFactory.location}')
        except FileNotFoundError:
            pass
