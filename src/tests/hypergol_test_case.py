import os
from unittest import TestCase

from hypergol.base_data import BaseData
from hypergol.dataset import RepoData
from hypergol.dataset_factory import DatasetFactory


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


class DataClass3(BaseData):

    def __init__(self, id_: int, value3: int):
        self.id_ = id_
        self.value3 = value3

    def get_id(self):
        return (self.id_, )

    def __hash__(self):
        return hash((self.id_, self.value3))


class HypergolTestCase(TestCase):

    def __init__(self, location, projectName, branch, chunkCount, methodName):
        super(HypergolTestCase, self).__init__(methodName=methodName)
        self.location = location
        self.projectName = projectName
        self.branch = branch
        self.chunkCount = chunkCount
        self.repoData = RepoData(
            branchName='testBranch',
            commitHash='f000bc7ad532063d9f9a36fe00e3ee2f83a3c565',
            commitMessage='test commit message',
            comitterName='Test Comitter',
            comitterEmail='test.comitter@gmail.com'
        )

    def setUp(self):
        super().setUp()
        self.datasetFactory = DatasetFactory(
            location=self.location,
            project=self.projectName,
            branch=self.branch,
            chunkCount=self.chunkCount,
            repoData=self.repoData
        )

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
