import shutil
from tests.hypergol_test_case import DataClass1
from tests.hypergol_test_case import HypergolTestCase
from tests.example_tensorflow_classes import ExampleBatchProcessor
from tests.example_tensorflow_classes import ExampleOutputDataClass


class TestBaseBatchReader(HypergolTestCase):

    def __init__(self, methodName='runTest'):
        self.location = 'test_batch_reader_location'
        super(TestBaseBatchReader, self).__init__(
            location=self.location,
            project='test_batch_reader',
            branch='branch',
            chunkCount=16,
            methodName=methodName
        )

    def setUp(self):
        super().setUp()
        self.sampleLength = 3
        self.inputDataset = self.create_test_dataset(
            dataset=self.datasetFactory.get(dataType=DataClass1, name='data1'),
            content=[DataClass1(id_=k, value1=k + 1) for k in range(self.sampleLength)]
        )
        self.outputDataset = self.datasetFactory.get(dataType=ExampleOutputDataClass, name='exampleOutputDataset')
        self.batchReader = ExampleBatchProcessor(
            inputDataset=self.inputDataset,
            inputBatchSize=self.sampleLength,
            outputDataset=self.outputDataset
        )
        self.expectedBatchInputs = {
            'batchIds': list(range(0, self.sampleLength)),
            'inputs': {
                'input1': list(range(1, self.sampleLength + 1)),
                'input2': list(range(2, self.sampleLength + 2))
            },
            'targets': list(range(1, self.sampleLength + 1))
        }
        self.expectedOutputObjects = {ExampleOutputDataClass(id_=k, value1=k + 1, predictionTarget=k + 1, modelPrediction=k + 2) for k in range(self.sampleLength)}

    def tearDown(self):
        super().tearDown()
        shutil.rmtree(self.location)

    def test_read_batch(self):
        self.assertEqual(next(self.batchReader), self.expectedBatchInputs)

    def test_save_batch(self):
        self.batchReader.save_batch(modelInputs=self.expectedBatchInputs, modelOutputs=[k + 2 for k in range(self.sampleLength)])
        savedObjects = set()
        with self.outputDataset.open('r') as datasetReader:
            for value in datasetReader:
                savedObjects.add(value)
        self.assertSetEqual(savedObjects, self.expectedOutputObjects)
