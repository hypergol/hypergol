from hypergol.base_batch_reader import BaseBatchReader
from tests.hypergol_test_case import DataClass1
from tests.hypergol_test_case import HypergolTestCase


class BatchReaderExample(BaseBatchReader):

    def __init__(self, dataset, batchSize):
        super(BatchReaderExample, self).__init__(dataset=dataset, batchSize=batchSize)

    def process_batch(self, batch):
        # needs to produce unordered sets for testing, because it's hard to know the order in which data will be read from Dataset
        output = {
            'batchIds': {v.id_ for v in batch},
            'inputs': {
                'input1': {v.id_ for v in batch},
                'input2': {v.value1 for v in batch}
            },
            'targets': {v.value1 for v in batch}
        }
        return output


class TestBaseBatchReader(HypergolTestCase):

    def __init__(self, methodName='runTest'):
        super(TestBaseBatchReader, self).__init__(
            location='test_task_location',
            project='test_task',
            branch='branch',
            chunkCount=16,
            methodName=methodName
        )

    def setUp(self):
        super().setUp()
        self.sampleLength = 3
        self.dataset1 = self.create_test_dataset(
            dataset=self.datasetFactory.get(dataType=DataClass1, name='data1'),
            content=[DataClass1(id_=k, value1=k + 1) for k in range(self.sampleLength)]
        )
        self.expectedOutput = {
            'batchIds': set(range(0, self.sampleLength)),
            'inputs': {
                'input1': set(range(0, self.sampleLength)),
                'input2': set(range(1, self.sampleLength + 1))
            },
            'targets': set(range(1, self.sampleLength + 1))
        }

    def tearDown(self):
        super().tearDown()
        self.delete_if_exists(dataset=self.dataset1)
        self.clean_directories()

    def test_batch_reader(self):
        batchReader = BatchReaderExample(
            dataset=self.dataset1,
            batchSize=self.sampleLength
        )
        self.assertEqual(next(batchReader), self.expectedOutput)
