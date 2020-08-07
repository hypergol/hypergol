import shutil
import tensorflow as tf
from pathlib import Path

from hypergol.tensorflow_model_manager import TensorflowModelManager
from hypergol.tensorflow_tagger import TensorflowTagger
from tests.tensorflow_test_classes import ExampleOutputDataClass
from tests.tensorflow_test_classes import ExampleTensorflowBatchProcessor
from tests.tensorflow_test_classes import ExampleTrainableBlock
from tests.tensorflow_test_classes import TensorflowModelExample
from tests.hypergol_test_case import DataClass1
from tests.hypergol_test_case import HypergolTestCase

tf.config.experimental.set_visible_devices([], 'GPU')


class TestTensorflowTagger(HypergolTestCase):

    def __init__(self, methodName='runTest'):
        self.location = 'test_tensorflow_tagger_location'
        self.project = 'test_tensorflow_tagger'
        self.branch = 'branch'
        super(TestTensorflowTagger, self).__init__(
            location=self.location,
            project=self.project,
            branch=self.branch,
            chunkCount=16,
            methodName=methodName
        )
        self.exampleInputs = {
            'ids': [1, 2, 3],
            'input1': tf.constant([[2, 3, 4]], dtype=tf.float32)
        }
        self.batchSize = 3

    def setUp(self):
        super().setUp()
        self.inputDataset = self.create_test_dataset(
            dataset=self.datasetFactory.get(dataType=DataClass1, name='data1'),
            content=[DataClass1(id_=k, value1=k + 1) for k in range(self.batchSize)]
        )
        self.outputDataset = self.datasetFactory.get(dataType=ExampleOutputDataClass, name='exampleOutputDataset')
        self.batchProcessor = ExampleTensorflowBatchProcessor(
            inputDataset=self.inputDataset,
            inputBatchSize=self.batchSize,
            outputDataset=self.outputDataset
        )
        self.modelBlock = ExampleTrainableBlock(requiredOutputSize=1)
        self.model = TensorflowModelExample(exampleBlock=self.modelBlock)
        self.modelManager = TensorflowModelManager(
            model=self.model,
            optimizer=tf.keras.optimizers.Adam(lr=1),
            batchProcessor=self.batchProcessor,
            location=self.location,
            project=self.project,
            branch=self.branch,
            name='testTfTagger',
            restoreWeightsPath=None
        )

    def tearDown(self):
        super().tearDown()
        self.modelManager.finish()
        shutil.rmtree(self.location)

    def test_tagger(self):
        self.modelManager.start()
        self.modelManager.train(withTracing=True)
        modelDirectory = Path(self.location, self.project, self.branch, 'models', self.modelManager.name, str(self.modelManager.globalStep))
        self.modelManager.save_model()
        tagger = TensorflowTagger(modelDirectory=modelDirectory, useGPU=False)
        prediction = tagger.get_prediction(**self.exampleInputs)
        self.assertIsNotNone(prediction)
        self.assertEqual(len(prediction.shape), 2)
        self.assertNotEqual(prediction.numpy()[0], 0)
