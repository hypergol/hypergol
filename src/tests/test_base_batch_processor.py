import shutil
from tests.hypergol_test_case import DataClass1
from tests.hypergol_test_case import HypergolTestCase
from tests.tensorflow_test_classes import ExampleBatchProcessor
from tests.tensorflow_test_classes import ExampleOutputDataClass


class TestBaseBatchProcessor(HypergolTestCase):

    def __init__(self, methodName='runTest'):
        self.location = 'test_batch_processor_location'
        super(TestBaseBatchProcessor, self).__init__(
            location=self.location,
            projectName='test_batch_processor',
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
        self.expectedBatchInputs = {
            'ids': list(range(0, self.sampleLength)),
            'input1': list(range(1, self.sampleLength + 1)),
            'input2': list(range(2, self.sampleLength + 2))
        }
        self.expectedBatchTargets = list(range(1, self.sampleLength + 1))
        self.expectedOutputObjects = {ExampleOutputDataClass(id_=k, value1=k + 1, predictionTarget=k + 1, modelPrediction=k + 2) for k in range(self.sampleLength)}
        self.batchProcessor = None

    def tearDown(self):
        super().tearDown()
        if self.batchProcessor is not None:
            self.batchProcessor.finish()
        shutil.rmtree(self.location)

    def test_read_batch(self):
        self.batchProcessor = ExampleBatchProcessor(
            inputDataset=self.inputDataset,
            inputBatchSize=self.sampleLength,
            outputDataset=self.datasetFactory.get(dataType=ExampleOutputDataClass, name='exampleOutputDataset')
        )
        self.batchProcessor.start()
        inputs, targets = next(self.batchProcessor)
        self.assertEqual(inputs, self.expectedBatchInputs)
        self.assertEqual(targets, self.expectedBatchTargets)

    def test_save_batch(self):
        self.batchProcessor = ExampleBatchProcessor(
            inputDataset=self.inputDataset,
            inputBatchSize=self.sampleLength,
            outputDataset=self.datasetFactory.get(dataType=ExampleOutputDataClass, name='exampleOutputDataset')
        )
        self.batchProcessor.start()
        self.batchProcessor.save_batch(
            inputs=self.expectedBatchInputs,
            targets=self.expectedBatchTargets,
            outputs=[k + 2 for k in range(self.sampleLength)]
        )
        self.batchProcessor.finish()
        savedObjects = set()
        with self.batchProcessor.outputDataset.open('r') as datasetReader:
            for value in datasetReader:
                savedObjects.add(value)
        self.assertSetEqual(savedObjects, self.expectedOutputObjects)
