import os

from tests.hypergol_test_case import HypergolTestCase
from tests.hypergol_test_case import DataClass1
from hypergol.base_data import BaseData
from hypergol.source import Source
from hypergol.source import SourceIteratorNotIterableException


class SourceExample(Source):

    def __init__(self, sampleLength, *args, **kwargs):
        super(SourceExample, self).__init__(*args, **kwargs)
        self.sampleLength = sampleLength

    def source_iterator(self):
        for k in range(self.sampleLength):
            yield k

    def run(self, k):
        return DataClass1(id_=k, value1=k)


class BadIteratorSourceExample(Source):

    def __init__(self, sampleLength, *args, **kwargs):
        super(BadIteratorSourceExample, self).__init__(*args, **kwargs)
        self.sampleLength = sampleLength

    def source_iterator(self):
        for k in range(self.sampleLength):
            # This should be `yield k`
            return k

    def run(self, k):
        return DataClass1(id_=k, value1=k)


class TestSource(HypergolTestCase):

    def __init__(self, methodName='runTest'):
        super(TestSource, self).__init__(
            location='test_source_location',
            project='test_source',
            branch='branch',
            chunkCount=16,
            methodName=methodName
        )

    def setUp(self):
        super().setUp()
        self.sampleLength = 100
        self.expectedData = {DataClass1(id_=k, value1=k) for k in range(self.sampleLength)}
        self.dataset = self.datasetFactory.get(dataType=DataClass1, name='data_class')

    def tearDown(self):
        super().tearDown()
        self.delete_if_exists(dataset=self.dataset)
        self.clean_directories()

    def test_source_execute_creates_dataset(self):
        sourceExample = SourceExample(
            outputDataset=self.dataset,
            sampleLength=self.sampleLength
        )
        sourceExample.execute()
        data = set(self.dataset.open('r'))
        self.assertSetEqual(data, self.expectedData)

    def test_execute_raises_error_if_bad_iterator(self):
        badIteratorSourceExample = BadIteratorSourceExample(
            outputDataset=self.dataset,
            sampleLength=self.sampleLength
        )
        with self.assertRaises(SourceIteratorNotIterableException):
            badIteratorSourceExample.execute()
