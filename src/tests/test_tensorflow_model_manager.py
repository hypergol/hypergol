import os
import shutil
import tensorflow as tf
from pathlib import Path

from hypergol.tensorflow_model_manager import TensorflowModelManager
from tests.tensorflow_test_classes import ExampleOutputDataClass
from tests.tensorflow_test_classes import ExampleTensorflowBatchProcessor
from tests.tensorflow_test_classes import ExampleTrainableBlock
from tests.tensorflow_test_classes import TensorflowModelExample
from tests.hypergol_test_case import DataClass1
from tests.hypergol_test_case import HypergolTestCase

tf.config.experimental.set_visible_devices([], 'GPU')


class TestTensorflowModelManager(HypergolTestCase):

    def __init__(self, methodName='runTest'):
        self.location = 'test_tensorflow_model_manager_location'
        super(TestTensorflowModelManager, self).__init__(
            location=self.location,
            project='test_tensorflow_model_manager',
            branch='branch',
            chunkCount=16,
            methodName=methodName
        )
        self.batchSize = 3

    def setUp(self):
        super().setUp()
        self.inputDataset = self.create_test_dataset(
            dataset=self.datasetFactory.get(dataType=DataClass1, name='data1'),
            content=[DataClass1(id_=k, value1=k + 1) for k in range(self.batchSize)]
        )
        self.outputDataset = self.datasetFactory.get(dataType=ExampleOutputDataClass, name='exampleOutputDataset')
        self.batchReader = ExampleTensorflowBatchProcessor(
            inputDataset=self.inputDataset,
            inputBatchSize=self.batchSize,
            outputDataset=self.outputDataset
        )
        self.modelBlock = ExampleTrainableBlock(requiredOutputSize=1)
        self.model = TensorflowModelExample(exampleBlock=self.modelBlock)
        self.modelManager = TensorflowModelManager(
            model=self.model,
            optimizer=tf.keras.optimizers.Adam(lr=1),
            batchProcessor=self.batchReader,
            saveDirectory=Path(self.location, 'save_dir'),
            tensorboardPath=Path(self.location, 'tensorboard'),
            restoreWeightsPath=None
        )

    def tearDown(self):
        super().tearDown()
        shutil.rmtree(self.location)

    def test_initialize_with_no_restore(self):
        self.modelManager.initialize()
        self.assertNotEqual(self.modelManager.trainingSummaryWriter, None)
        self.assertNotEqual(self.modelManager.evaluationSummaryWriter, None)

    def test_train(self):
        self.modelManager.initialize()
        loss = self.modelManager.train(withLogging=True, withMetadata=True)
        self.assertIsNotNone(loss)
        self.assertNotEqual(loss.numpy(), 0)

    def test_evaluate(self):
        self.modelManager.initialize()
        outputs, loss, metrics = self.modelManager.evaluate(withLogging=True, withMetadata=True)
        self.assertIsNotNone(loss)
        self.assertNotEqual(loss.numpy(), 0)

    def test_save_model(self):
        self.modelManager.initialize()
        self.modelManager.train(withLogging=True, withMetadata=True)
        saveModelDirectory = self.modelManager.modelSaveDirectory
        self.modelManager.save_model()
        self.assertTrue(os.path.exists(saveModelDirectory))
        self.assertTrue(os.path.exists(f'{saveModelDirectory}/assets'))
        self.assertTrue(os.path.exists(f'{saveModelDirectory}/variables'))
        self.assertTrue(os.path.exists(f'{saveModelDirectory}/{self.modelBlock.get_name()}.json'))
        self.assertTrue(os.path.exists(f'{saveModelDirectory}/saved_model.pb'))
        self.assertTrue(os.path.exists(f'{saveModelDirectory}/{self.model.get_name()}.h5'))

    def test_restore_model(self):
        self.modelManager.initialize()
        self.modelManager.train(withLogging=True, withMetadata=True)
        originalBlockWeights = self.modelManager.model.exampleBlock.weights[0].numpy()
        savedModelDirectory = self.modelManager.modelSaveDirectory
        self.modelManager.save_model()
        self.newModel = TensorflowModelExample(exampleBlock=ExampleTrainableBlock(requiredOutputSize=1))
        self.newModelManager = self.modelManager = TensorflowModelManager(
            model=self.model,
            optimizer=tf.keras.optimizers.Adam(lr=1),
            batchProcessor=self.batchReader,
            saveDirectory=Path(self.location, 'new', 'save_dir'),
            tensorboardPath=Path(self.location, 'new', 'tensorboard'),
            restoreWeightsPath=savedModelDirectory
        )
        self.newModelManager.restore_model_weights()
        newBlockWeights = self.newModelManager.model.exampleBlock.weights[0].numpy()
        self.assertTrue((originalBlockWeights == newBlockWeights).all())
