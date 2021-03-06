import os
import shutil
from pathlib import Path
import tensorflow as tf

from hypergol.hypergol_project import HypergolProject
from hypergol.tensorflow_model_manager import TensorflowModelManager

from tests.tensorflow_test_classes import ExampleOutputDataClass
from tests.tensorflow_test_classes import ExampleTensorflowBatchProcessor
from tests.tensorflow_test_classes import ExampleTrainableBlock
from tests.tensorflow_test_classes import TensorflowModelExample
from tests.hypergol_test_case import DataClass1
from tests.hypergol_test_case import HypergolTestCase
from tests.hypergol_test_case import TestRepoManager

tf.config.experimental.set_visible_devices([], 'GPU')


class TestTensorflowModelManager(HypergolTestCase):

    def __init__(self, methodName='runTest'):
        self.location = 'test_tensorflow_model_manager_location'
        self.projectName = 'test_tensorflow_model_manager'
        self.branch = 'branch'
        super(TestTensorflowModelManager, self).__init__(
            location=self.location,
            projectName=self.projectName,
            branch=self.branch,
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
        self.batchProcessor = ExampleTensorflowBatchProcessor(
            inputDataset=self.inputDataset,
            inputBatchSize=self.batchSize,
            outputDataset=self.outputDataset
        )
        self.modelBlock = ExampleTrainableBlock(requiredOutputSize=1)
        self.model = TensorflowModelExample(exampleBlock=self.modelBlock)
        self.project = HypergolProject(
            projectDirectory='DOESNOTEXIST',
            dataDirectory=self.location,
            repoManager=TestRepoManager(raiseIfDirty=False)
        )
        self.modelManager = TensorflowModelManager(
            model=self.model,
            optimizer=tf.keras.optimizers.Adam(lr=1),
            batchProcessor=self.batchProcessor,
            project=self.project,
            restoreWeightsPath=None
        )

        self.modelManager.project.tensorboardPath = Path(self.location, self.projectName, 'tensorboard', self.branch)
        self.modelManager.project.modelDataPath = Path(self.location, self.projectName, self.branch, 'models')
        self.modelManager.start()

    def tearDown(self):
        super().tearDown()
        self.modelManager.finish()
        shutil.rmtree(self.location)

    def test_summary_writer_initialization(self):
        self.assertIsNotNone(self.modelManager.trainingSummaryWriter)
        self.assertIsNotNone(self.modelManager.evaluationSummaryWriter)

    def test_train(self):
        loss = self.modelManager.train(withTracing=True)
        self.assertIsNotNone(loss)
        self.assertNotEqual(loss.numpy(), 0)

    def test_gradients_applied_in_train(self):
        self.modelManager.train(withTracing=False)
        weights1 = self.modelManager.model.exampleBlock.exampleDenseLayer.weights[0].numpy()  # need numpy call here, otherwise pointed returned
        self.modelManager.train(withTracing=False)
        weights2 = self.modelManager.model.exampleBlock.exampleDenseLayer.weights[0].numpy()
        self.assertFalse((weights1 == weights2).all())

    def test_evaluate(self):
        loss = self.modelManager.evaluate(withTracing=True)
        self.assertIsNotNone(loss)
        self.assertNotEqual(loss.numpy(), 0)

    def test_gradients_not_applied_in_evaluation(self):
        self.modelManager.evaluate(withTracing=False)
        weights1 = self.modelManager.model.exampleBlock.exampleDenseLayer.weights[0].numpy()  # need numpy call here, otherwise pointed returned
        self.modelManager.evaluate(withTracing=False)
        weights2 = self.modelManager.model.exampleBlock.exampleDenseLayer.weights[0].numpy()
        self.assertTrue((weights1 == weights2).all())

    def test_save_model(self):
        self.modelManager.train(withTracing=True)
        modelDirectory = Path(self.modelManager.project.modelDataPath, self.modelManager.model.modelName, str(self.modelManager.globalStep))
        self.modelManager.save_model()
        self.assertTrue(os.path.exists(modelDirectory))
        self.assertTrue(os.path.exists(f'{modelDirectory}/assets'))
        self.assertTrue(os.path.exists(f'{modelDirectory}/variables'))
        self.assertTrue(os.path.exists(f'{modelDirectory}/{self.modelBlock.blockName}.json'))
        self.assertTrue(os.path.exists(f'{modelDirectory}/saved_model.pb'))
        self.assertTrue(os.path.exists(f'{modelDirectory}/{self.model.modelName}.h5'))

    def test_restore_model(self):
        self.modelManager.train(withTracing=True)
        originalBlockWeights = self.modelManager.model.exampleBlock.weights[0].numpy()
        modelDirectory = Path(self.modelManager.project.modelDataPath, self.modelManager.model.modelName, str(self.modelManager.globalStep))
        self.modelManager.save_model()
        newModel = TensorflowModelExample(exampleBlock=ExampleTrainableBlock(requiredOutputSize=1))
        # new batch processor needed to avoid DataSet collision with previous processor
        newOutputDataset = self.datasetFactory.get(dataType=ExampleOutputDataClass, name='newExampleOutputDataset')
        newBatchProcessor = ExampleTensorflowBatchProcessor(
            inputDataset=self.inputDataset,
            inputBatchSize=self.batchSize,
            outputDataset=newOutputDataset
        )
        newModelManager = TensorflowModelManager(
            model=newModel,
            optimizer=tf.keras.optimizers.Adam(lr=1),
            batchProcessor=newBatchProcessor,
            project=self.project,
            restoreWeightsPath=modelDirectory
        )
        newModelManager.start()
        newBlockWeights = newModelManager.model.exampleBlock.weights[0].numpy()
        self.assertTrue((originalBlockWeights == newBlockWeights).all())
