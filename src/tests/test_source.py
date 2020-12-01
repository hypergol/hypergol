import os

from hypergol.base_task import Job
from hypergol.base_task import SourceIteratorNotIterableException
from hypergol.task import Task
from hypergol.dataset import Dataset
from hypergol.base_data import BaseData

from tests.hypergol_test_case import HypergolTestCase
from tests.hypergol_test_case import DataClass1


class OutputDataClass(BaseData):

    def __init__(self, id_: int, id2: int, value: int):
        self.id_ = id_
        self.id2 = id2
        self.value = value

    def get_id(self):
        return (self.id_, self.id2, )

    def __hash__(self):
        return hash((self.id_, self.id2, self.value))


class SourceExample(Task):

    def __init__(self, sampleLength, *args, **kwargs):
        super(SourceExample, self).__init__(*args, **kwargs)
        self.sampleLength = sampleLength

    def get_jobs(self):
        return [Job(id_=0, total=2), Job(id_=1, total=2)]

    def source_iterator(self):
        for k in range(self.sampleLength):
            yield (k, )

    def run(self, k):
        self.output.append(OutputDataClass(id_=k, id2=k, value=k + 1))


class BadIteratorSourceExample(Task):

    def __init__(self, sampleLength, *args, **kwargs):
        super(BadIteratorSourceExample, self).__init__(*args, **kwargs)
        self.sampleLength = sampleLength

    def get_jobs(self):
        return [Job(id_=0, total=2), Job(id_=1, total=2)]

    def source_iterator(self):
        for k in range(self.sampleLength):
            # This should be `yield k`
            return (k, )

    def run(self, k):
        self.output.append(OutputDataClass(id_=k, id2=k, value=k + 1))


class TestSource(HypergolTestCase):

    def __init__(self, methodName='runTest'):
        super(TestSource, self).__init__(
            location='test_source_location',
            projectName='test_source',
            branch='branch',
            chunkCount=16,
            methodName=methodName
        )

    def setUp(self):
        super().setUp()
        self.sampleLength = 100
        self.expectedData = {OutputDataClass(id_=k, id2=k, value=k + 1) for k in range(self.sampleLength)}
        self.outputDataset = self.datasetFactory.get(dataType=OutputDataClass, name='output_data')

    def tearDown(self):
        super().tearDown()
        for jobId in [0, 1]:
            temporaryDataSet = Dataset(
                dataType=OutputDataClass,
                location=self.outputDataset.location,
                project=self.outputDataset.project,
                branch=f'{self.outputDataset.name}_temp',
                name=f'{self.outputDataset.name}_{jobId:03}',
                chunkCount=self.outputDataset.chunkCount,
                repoData=self.outputDataset.repoData
            )
            self.delete_if_exists(dataset=temporaryDataSet)
        self.delete_if_exists(dataset=self.outputDataset)
        tempBranchDirectory = f'{self.outputDataset.location}/{self.outputDataset.project}/{self.outputDataset.name}_temp'
        if os.path.exists(tempBranchDirectory):
            os.rmdir(tempBranchDirectory)
        self.clean_directories()

    def test_source_execute_creates_dataset(self):
        sourceExample = SourceExample(
            outputDataset=self.outputDataset,
            sampleLength=self.sampleLength
        )
        jobReports = []
        for job in sourceExample.get_jobs():
            jobReports.append(sourceExample.execute(job))
        sourceExample.finalise(jobReports, 0)
        data = set(self.outputDataset.open('r'))
        self.assertSetEqual(data, self.expectedData)

    def test_execute_raises_error_if_bad_iterator(self):
        badIteratorSourceExample = BadIteratorSourceExample(
            outputDataset=self.outputDataset,
            sampleLength=self.sampleLength
        )
        with self.assertRaises(SourceIteratorNotIterableException):
            for job in badIteratorSourceExample.get_jobs():
                badIteratorSourceExample.execute(job)
