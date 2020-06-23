import os
from unittest import TestCase

from hypergol.base_data import BaseData
from hypergol.dataset import Dataset
from hypergol.source import Source
from hypergol.source import SourceIteratorNotIterableException


class DataClass(BaseData):

    def __init__(self, id_: int, value: int):
        self.id_ = id_
        self.value = value

    def get_id(self):
        return (self.id_, )

    def __hash__(self):
        return self.id_


class SourceExample(Source):

    def __init__(self, sampleLength, *args, **kwargs):
        super(SourceExample, self).__init__(*args, **kwargs)
        self.sampleLength = sampleLength

    def source_iterator(self):
        for k in range(self.sampleLength):
            yield k

    def run(self, k):
        return DataClass(id_=k, value=k)


class BadIteratorSourceExample(Source):

    def __init__(self, sampleLength, *args, **kwargs):
        super(BadIteratorSourceExample, self).__init__(*args, **kwargs)
        self.sampleLength = sampleLength

    def source_iterator(self):
        for k in range(self.sampleLength):
            # This should be `yield k`
            return k

    def run(self, k):
        return DataClass(id_=k, value=k)


class TestSource(TestCase):

    def setUp(self):
        super().setUp()
        self.sampleLength = 100
        self.dataset = Dataset(
            dataType=DataClass,
            location='test_source_location',
            project='test_source',
            branch='branch',
            name='data_class',
            chunks=16
        )
        self.expectedData = {DataClass(id_=k, value=k) for k in range(self.sampleLength)}

    def tearDown(self):
        super().tearDown()
        if self.dataset.exists():
            self.dataset.delete()
        try:
            os.rmdir(f'{self.dataset.location}/{self.dataset.project}/{self.dataset.branch}')
        except FileNotFoundError:
            pass
        try:
            os.rmdir(f'{self.dataset.location}/{self.dataset.project}')
        except FileNotFoundError:
            pass
        try:
            os.rmdir(f'{self.dataset.location}')
        except FileNotFoundError:
            pass

    def test_source_execute_creates_dataset(self):
        sourceExample = SourceExample(
            outputDataset=self.dataset,
            sampleLength=self.sampleLength
        )
        sourceExample.execute()
        data = set(self.dataset.open('r'))
        self.assertSetEqual(data, self.expectedData)

    def test_source_execute_creates_dataset(self):
        badIteratorSourceExample = BadIteratorSourceExample(
            outputDataset=self.dataset,
            sampleLength=self.sampleLength
        )
        with self.assertRaises(SourceIteratorNotIterableException):
            badIteratorSourceExample.execute()
