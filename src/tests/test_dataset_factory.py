from unittest import TestCase

from tests.hypergol_test_case import DataClass1
from hypergol.dataset import Dataset
from hypergol.dataset_chkfile import DataSetChkFile
from hypergol.dataset import DataSetDefFile
from hypergol.dataset import RepoData
from hypergol.dataset import DatasetFactory


class TestDatasetFactory(TestCase):

    def setUp(self):
        super().setUp()
        self.repoData = RepoData(
            branchName='testBranch',
            commitHash='f000bc7ad532063d9f9a36fe00e3ee2f83a3c565',
            commitMessage='test commit message',
            comitterName='Test Comitter',
            comitterEmail='test.comitter@gmail.com'
        )
        self.expectedDataset = Dataset(
            dataType=DataClass1,
            location='.',
            project='test_x',
            branch='branch',
            name='data_class',
            chunkCount=256,
            repoData=self.repoData
        )

    def test_dataset_factory_returns_correct_dataset(self):
        datasetFactory = DatasetFactory(
            location=self.expectedDataset.location,
            project=self.expectedDataset.project,
            branch=self.expectedDataset.branch,
            chunkCount=self.expectedDataset.chunkCount,
            repoData=self.repoData)
        dataset = datasetFactory.get(dataType=DataClass1, name='data_class')
        self.assertEqual(type(dataset), Dataset)
        expectedParameters = {k: v for k, v in self.expectedDataset.__dict__.items() if k not in ['chkFile', 'defFile']}
        actualParameters = {k: v for k, v in dataset.__dict__.items() if k not in ['chkFile', 'defFile']}
        self.assertDictContainsSubset(expectedParameters, actualParameters)
        self.assertEqual(type(dataset.chkFile), DataSetChkFile)
        self.assertEqual(dataset.chkFile.dataset, dataset)
        self.assertEqual(type(dataset.defFile), DataSetDefFile)
        self.assertEqual(dataset.defFile.dataset, dataset)
