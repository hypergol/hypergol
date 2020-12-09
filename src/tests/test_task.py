import os
import pickle

from hypergol.task import Task
from hypergol.base_data import BaseData
from hypergol.dataset import Dataset
from hypergol.dataset import DatasetAlreadyExistsException

from tests.hypergol_test_case import DataClass1
from tests.hypergol_test_case import DataClass2
from tests.hypergol_test_case import DataClass3
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


class OutputDataClass2(BaseData):

    def __init__(self, id_: int, data1: DataClass1, data2: DataClass2, data3: DataClass3, value: int):
        self.id_ = id_
        self.data1 = data1
        self.data2 = data2
        self.data3 = data3
        self.value = value

    def get_id(self):
        return (self.id_, )

    def to_data(self):
        data = self.__dict__.copy()
        data['data1'] = data['data1'].to_data()
        data['data2'] = data['data2'].to_data()
        data['data3'] = data['data3'].to_data()
        return data

    @classmethod
    def from_data(cls, data):
        data['data1'] = DataClass1.from_data(data['data1'])
        data['data2'] = DataClass2.from_data(data['data2'])
        data['data3'] = DataClass3.from_data(data['data3'])
        return cls(**data)

    def __hash__(self):
        return hash((self.id_, hash(self.data1), hash(self.data2), self.value))


class TaskExample2(Task):

    def __init__(self, increment, *args, **kwargs):
        super(TaskExample2, self).__init__(*args, **kwargs)
        self.increment = increment

    def init(self):
        self.increment = self.increment + 1

    def run(self, data1, data2, lstData3):
        if data1.id_ != data2.id_:
            raise ValueError('ids are not matching')
        data3 = next(data for data in lstData3 if data.id_ == data1.id_)
        self.output.append(OutputDataClass2(
            id_=data1.id_,
            data1=data1,
            data2=data2,
            data3=data3,
            value=self.increment
        ))


class TaskExample3(Task):

    def __init__(self, increment, *args, **kwargs):
        super(TaskExample3, self).__init__(*args, **kwargs)
        self.increment = increment

    def init(self):
        self.increment = self.increment + 1

    def run(self, data1, data2, lstData3):
        if data1.id_ != data2.id_:
            raise ValueError('ids are not matching')
        data3 = next(data for data in lstData3 if data.id_ == data1.id_)
        self.output.append(OutputDataClass2(
            id_=data1.id_,
            data1=data1,
            data2=data2,
            data3=data3,
            value=self.increment
        ))


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
        self.increment = 1
        self.dataset1 = self.create_test_dataset(
            dataset=self.datasetFactory.get(dataType=DataClass1, name='data1'),
            content=[DataClass1(id_=k, value1=k) for k in range(self.sampleLength)]
        )
        self.dataset2 = self.create_test_dataset(
            dataset=self.datasetFactory.get(dataType=DataClass2, name='data2'),
            content=[DataClass2(id_=k, value2=k) for k in range(self.sampleLength)]
        )
        self.dataset3 = self.create_test_dataset(
            dataset=self.datasetFactory.get(dataType=DataClass3, name='data3'),
            content=[DataClass3(id_=k, value3=k) for k in range(self.sampleLength)]
        )
        self.expectedOutputDataset = set()
        for id_ in range(self.sampleLength):
            for k in range(self.repeat):
                self.expectedOutputDataset.add(OutputDataClass(id_=id_, id2=k, value=id_))
        self.outputDataset = self.datasetFactory.get(dataType=OutputDataClass, name='output_data')
        self.expectedOutputDataset2 = {
            OutputDataClass2(
                id_=k,
                data1=DataClass1(id_=k, value1=k),
                data2=DataClass2(id_=k, value2=k),
                data3=DataClass3(id_=k, value3=k),
                value=self.increment + 1
            ) for k in range(100)}
        self.outputDataset2 = self.datasetFactory.get(dataType=OutputDataClass2, name='output_data2')
        self.reversedDataset = self.create_test_dataset(
            dataset=self.datasetFactory.get(dataType=DataClass2, name='rev_data2'),
            content=[DataClass2(id_=k, value2=k) for k in reversed(range(self.sampleLength))]
        )

    def tearDown(self):
        super().tearDown()
        self.delete_if_exists(dataset=self.dataset1)
        self.delete_if_exists(dataset=self.dataset2)
        self.delete_if_exists(dataset=self.dataset3)
        self.delete_if_exists(dataset=self.outputDataset)
        self.delete_if_exists(dataset=self.outputDataset2)
        self.delete_if_exists(dataset=self.reversedDataset)
        for jobId in range(self.dataset1.chunkCount):
            self.delete_if_exists(dataset=Dataset(
                dataType=OutputDataClass,
                location=self.outputDataset.location,
                project='temp',
                branch=f'{self.outputDataset.name}_temp',
                name=f'{self.outputDataset.name}_{jobId:03}',
                chunkCount=self.outputDataset.chunkCount,
                repoData=self.outputDataset.repoData
            ))
        tempBranchDirectory = f'{self.outputDataset.location}/temp/{self.outputDataset.name}_temp'
        if os.path.exists(tempBranchDirectory):
            os.rmdir(tempBranchDirectory)
        self.clean_directories()

    def test_task(self):
        jobReports = []
        task = TaskExample(
            inputDatasets=[self.dataset1],
            outputDataset=self.outputDataset,
            loadedInputDatasets=[],
            repeat=3,
            debug=True
        )
        for job in task.get_jobs():
            taskCopy = pickle.loads(pickle.dumps(task))
            jobReport = taskCopy.execute(job)
            jobReports.append(jobReport)
        task.finalise(jobReports=jobReports, threads=3)
        self.assertEqual(set(self.outputDataset.open('r')), self.expectedOutputDataset)

    def test_execute_throws_error_if_ids_do_not_match(self):
        jobReports = []
        task = TaskExample2(
            inputDatasets=[self.dataset1, self.reversedDataset],
            outputDataset=self.outputDataset,
            loadedInputDatasets=[self.dataset3],
            increment=1,
            debug=True
        )
        with self.assertRaises(ValueError):
            for job in task.get_jobs():
                taskCopy = pickle.loads(pickle.dumps(task))
                jobReport = taskCopy.execute(job)
                jobReports.append(jobReport)
        taskCopy.finalise(jobReports=jobReports, threads=3)

    def test_task_with_loaded_dataset(self):
        jobReports = []
        task = TaskExample3(
            inputDatasets=[self.dataset1, self.dataset2],
            outputDataset=self.outputDataset2,
            loadedInputDatasets=[self.dataset3],
            increment=1,
            debug=True
        )
        for job in task.get_jobs():
            taskCopy = pickle.loads(pickle.dumps(task))
            jobReport = taskCopy.execute(job)
            jobReports.append(jobReport)
        task.finalise(jobReports=jobReports, threads=3)
        self.assertEqual(set(self.outputDataset2.open('r')), self.expectedOutputDataset2)

    def test_check_if_output_exists_raises_if_dataset_already_exists(self):
        task = TaskExample(
            inputDatasets=[self.dataset1],
            outputDataset=self.dataset2,
            loadedInputDatasets=[],
            repeat=3,
            debug=True
        )
        with self.assertRaises(DatasetAlreadyExistsException):
            task.check_if_output_exists()

    def test_check_if_output_exists_raises_if_temporary_directory_already_exists(self):
        task = TaskExample(
            inputDatasets=[self.dataset1],
            outputDataset=self.outputDataset,
            loadedInputDatasets=[],
            repeat=3,
            debug=True
        )
        os.mkdir(task.temporaryDatasetFactory.projectDirectory)
        os.mkdir(task.temporaryDatasetFactory.branchDirectory)
        with self.assertRaises(DatasetAlreadyExistsException):
            task.check_if_output_exists()
