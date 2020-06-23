import os
import pickle
from unittest import TestCase

from hypergol.base_data import BaseData
from hypergol.dataset import DatasetFactory
from hypergol.task import Task


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


class TestDataset(TestCase):

    def setUp(self):
        self.sampleLength = 100
        self.increment = 1
        self.datasetFactory = DatasetFactory(location='test_task_location', project='test_task', branch='branch', chunks=16)
        self.dataset1 = self.datasetFactory.get(dataType=DataClass1, name='data1')
        self.dataset2 = self.datasetFactory.get(dataType=DataClass2, name='data2')
        self.reversedDataset = self.datasetFactory.get(dataType=DataClass2, name='rev_data2')
        self.outputDataset = self.datasetFactory.get(dataType=OutputDataClass, name='output_data')

        if not self.dataset1.exists():
            with self.dataset1.open('w') as ds1:
                for k in range(self.sampleLength):
                    ds1.append(DataClass1(id_=k, value1=k))
        if not self.dataset2.exists():
            with self.dataset2.open('w') as ds2:
                for k in range(self.sampleLength):
                    ds2.append(DataClass2(id_=k, value2=k))
        if not self.reversedDataset.exists():
            with self.reversedDataset.open('w') as dsrev:
                for k in reversed(range(self.sampleLength)):
                    dsrev.append(DataClass2(id_=k, value2=k))
        self.expectedOutputDataset = {
            OutputDataClass(
                id_=k,
                data1=DataClass1(id_=k, value1=k),
                data2=DataClass2(id_=k, value2=k),
                value=self.increment + 1
            ) for k in range(100)}

    def tearDown(self):
        if self.dataset1.exists():
            self.dataset1.delete()
        if self.dataset2.exists():
            self.dataset2.delete()
        if self.reversedDataset.exists():
            self.reversedDataset.delete()
        if self.outputDataset.exists():
            self.outputDataset.delete()
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
