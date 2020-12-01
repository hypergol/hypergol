import os
import pickle

from hypergol.task import Task
from hypergol.base_data import BaseData
from hypergol.dataset import Dataset

from tests.hypergol_test_case import DataClass1
from tests.hypergol_test_case import HypergolTestCase


class OutputDataClass(BaseData):

    def __init__(self, id_: int, id2: int, value: int):
        self.id_ = id_
        self.id2 = id2
        self.value = value

    def get_id(self):
        return (self.id_, self.id2, )

    def __hash__(self):
        return hash((self.id_, self.id2, self.value))


class TaskExample(Task):

    def __init__(self, repeat, *args, **kwargs):
        super(TaskExample, self).__init__(*args, **kwargs)
        self.repeat = repeat

    def run(self, inputData):
        for k in range(self.repeat):
            self.output.append(OutputDataClass(id_=inputData.id_, id2=k, value=inputData.value1))


class TestTask(HypergolTestCase):

    def __init__(self, methodName='runTest'):
        super(TestTask, self).__init__(
            location='test_task_location',
            projectName='test_task',
            branch='branch',
            chunkCount=16,
            methodName=methodName
        )

    def setUp(self):
        super().setUp()
        self.sampleLength = 100
        self.repeat = 3
        self.dataset1 = self.create_test_dataset(
            dataset=self.datasetFactory.get(dataType=DataClass1, name='data1'),
            content=[DataClass1(id_=k, value1=k) for k in range(self.sampleLength)]
        )
        self.expectedOutputDataset = set()
        for id_ in range(self.sampleLength):
            for k in range(self.repeat):
                self.expectedOutputDataset.add(OutputDataClass(id_=id_, id2=k, value=id_))
        self.outputDataset = self.datasetFactory.get(dataType=OutputDataClass, name='output_data')

    def tearDown(self):
        super().tearDown()
        self.delete_if_exists(dataset=self.dataset1)
        self.delete_if_exists(dataset=self.outputDataset)
        for jobId in range(self.dataset1.chunkCount):
            self.delete_if_exists(dataset=Dataset(
                dataType=OutputDataClass,
                location=self.outputDataset.location,
                project=self.outputDataset.project,
                branch=f'{self.outputDataset.name}_temp',
                name=f'{self.outputDataset.name}_{jobId:03}',
                chunkCount=self.outputDataset.chunkCount,
                repoData=self.outputDataset.repoData
            ))
        tempBranchDirectory = f'{self.outputDataset.location}/{self.outputDataset.project}/{self.outputDataset.name}_temp'
        if os.path.exists(tempBranchDirectory):
            os.rmdir(tempBranchDirectory)
        self.clean_directories()

    def test_task(self):
        jobReports = []
        task = TaskExample(
            inputDatasets=[self.dataset1],
            outputDataset=self.outputDataset,
            loadedInputDatasets=[],
            repeat=3
        )
        for job in task.get_jobs():
            taskCopy = pickle.loads(pickle.dumps(task))
            jobReport = taskCopy.execute(job)
            jobReports.append(jobReport)
        task.finalise(jobReports=jobReports, threads=3)
        self.assertEqual(set(self.outputDataset.open('r')), self.expectedOutputDataset)
