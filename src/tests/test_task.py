import os
import pickle

from tests.hypergol_test_case import HypergolTestCase
from tests.hypergol_test_case import DataClass1
from tests.hypergol_test_case import DataClass2
from hypergol.base_data import BaseData
from hypergol.task import Task


class OutputDataClass(BaseData):

    def __init__(self, id_: int, data1: DataClass1, data2: DataClass2, value: int):
        self.id_ = id_
        self.data1 = data1
        self.data2 = data2
        self.value = value

    def to_data(self):
        data = self.__dict__.copy()
        data['data1'] = data['data1'].to_data()
        data['data2'] = data['data2'].to_data()
        return data

    @classmethod
    def from_data(cls, data):
        data['data1'] = DataClass1.from_data(data['data1'])
        data['data2'] = DataClass2.from_data(data['data2'])
        return cls(**data)

    def __hash__(self):
        return hash((self.id_, hash(self.data1), hash(self.data2), self.value))


class TaskExample(Task):

    def __init__(self, increment, *args, **kwargs):
        super(TaskExample, self).__init__(*args, **kwargs)
        self.increment = increment

    def init(self):
        self.increment = self.increment + 1

    def run(self, data1, data2):
        if data1.id_ != data2.id_:
            raise ValueError('ids are not matching')
        return OutputDataClass(
            id_=data1.id_,
            data1=data1,
            data2=data2,
            value=self.increment
        )


class TestTask(HypergolTestCase):

    def __init__(self, methodName='runTest'):
        super(TestTask, self).__init__(
            location='test_task_location',
            project='test_task',
            branch='branch',
            chunks=16,
            methodName=methodName
        )

    def setUp(self):
        super().setUp()
        self.sampleLength = 100
        self.increment = 1
        self.dataset1 = self.create_test_dataset(
            dataset=self.datasetFactory.get(dataType=DataClass1, name='data1'),
            content=[DataClass1(id_=k, value1=k) for k in range(self.sampleLength)]
        )
        self.dataset2 = self.create_test_dataset(
            dataset=self.datasetFactory.get(dataType=DataClass2, name='data2'),
            content=[DataClass2(id_=k, value2=k) for k in range(self.sampleLength)]
        )
        self.reversedDataset = self.create_test_dataset(
            dataset=self.datasetFactory.get(dataType=DataClass2, name='rev_data2'),
            content=[DataClass2(id_=k, value2=k) for k in reversed(range(self.sampleLength))]
        )
        self.outputDataset = self.datasetFactory.get(dataType=OutputDataClass, name='output_data')
        self.expectedOutputDataset = {
            OutputDataClass(
                id_=k,
                data1=DataClass1(id_=k, value1=k),
                data2=DataClass2(id_=k, value2=k),
                value=self.increment + 1
            ) for k in range(100)}

    def tearDown(self):
        super().tearDown()
        self.delete_if_exists(self.dataset1)
        self.delete_if_exists(self.dataset2)
        self.delete_if_exists(self.reversedDataset)
        self.delete_if_exists(self.outputDataset)
        self.clean_directories()

    def test_task(self):
        task = TaskExample(
            inputDatasets=[self.dataset1, self.dataset2],
            outputDataset=self.outputDataset,
            increment=1
        )
        for job in task.get_jobs():
            taskCopy = pickle.loads(pickle.dumps(task))
            taskCopy.execute(job)
        self.assertEqual(set(self.outputDataset.open('r')), self.expectedOutputDataset)

    def test_execute_throws_error_if_ids_do_not_match(self):
        task = TaskExample(
            inputDatasets=[self.dataset1, self.reversedDataset],
            outputDataset=self.outputDataset,
            increment=1
        )
        # TODO(Laszlo): this tests run not execute, change when sync/debug added to Taskgs
        with self.assertRaises(ValueError):
            for job in task.get_jobs():
                taskCopy = pickle.loads(pickle.dumps(task))
                taskCopy.execute(job)
