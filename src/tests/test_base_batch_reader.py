import shutil
from hypergol.base_batch_processor import BaseBatchProcessor
from hypergol.base_data import BaseData
from tests.hypergol_test_case import DataClass1
from tests.hypergol_test_case import HypergolTestCase


class ExampleOutputDataClass(BaseData):

    def __init__(self, id_: int, value1: int, predictionTarget: int, modelPrediction: int):
        self.id_ = id_
        self.value1 = value1
        self.predictionTarget = predictionTarget
        self.modelPrediction = modelPrediction

    def get_id(self):
        return (self.id_, )

    def __hash__(self):
        return hash((self.id_, self.value1, self.modelPrediction))


class BatchProcessorExample(BaseBatchProcessor):

    def __init__(self, inputDataset, inputBatchSize, outputDataset):
        super(BatchProcessorExample, self).__init__(inputDataset=inputDataset, inputBatchSize=inputBatchSize, outputDataset=outputDataset)

    def process_input_batch(self, batch):
        # sorting needs to happen for testing, because impossible to know ordering of items in batch
        output = {
            'batchIds': sorted([v.id_ for v in batch]),
            'inputs': {
                'input1': sorted([v.value1 for v in batch]),
                'input2': sorted([v.value1 + 1 for v in batch])
            },
            'targets': sorted([v.value1 for v in batch])
        }
        return output

    def process_output_batch(self, modelInputs, modelOutputs):
        outputData = []
        for index, batchId in enumerate(modelInputs['batchIds']):
            outputData.append(ExampleOutputDataClass(
                id_=batchId,
                value1=modelInputs['inputs']['input1'][index],
                predictionTarget=modelInputs['targets'][index],
                modelPrediction=modelOutputs[index]
            ))
        return outputData


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
        self.batchReader = BatchProcessorExample(
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
