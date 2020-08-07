import numpy as np
import tensorflow as tf
from unittest import TestCase
from tests.tensorflow_test_classes import ExampleNonTrainableBlock
from tests.tensorflow_test_classes import ExampleTrainableBlock
from tests.tensorflow_test_classes import TensorflowModelExample

tf.config.experimental.set_visible_devices([], 'GPU')


class TestBaseTensorflowModel(TestCase):

    def __init__(self, methodName='runTest'):
        super(TestBaseTensorflowModel, self).__init__(methodName=methodName)
        self.exampleInputs = {
            'batchIds': [1, 2, 3],
            'input1': tf.constant([[2, 3, 4]], dtype=tf.float32)
        }
        self.nonTrainableExpectedOutput = np.array([[0.09003057, 0.24472848, 0.66524094]], dtype=np.float32)
        self.exampleTargets = tf.constant([[1, 2, 3]], dtype=tf.float32)
        self.expectedLoss = -5

    def setUp(self):
        super().setUp()
        self.trainableBlock = ExampleTrainableBlock(requiredOutputSize=self.nonTrainableExpectedOutput.shape[1])
        self.nonTrainableBlock = ExampleNonTrainableBlock()
        self.trainableModel = TensorflowModelExample(exampleBlock=self.trainableBlock)
        self.nonTrainableModel = TensorflowModelExample(exampleBlock=self.nonTrainableBlock)

    def test_get_model_blocks(self):
        nonTrainableBlocks = self.nonTrainableModel.get_model_blocks()
        nonTrainableBlockConfigs = [block.get_config() for block in nonTrainableBlocks]
        self.assertEqual(nonTrainableBlockConfigs, [self.nonTrainableBlock.get_config()])
        trainableBlocks = self.trainableModel.get_model_blocks()
        trainableBlockConfigs = [block.get_config() for block in trainableBlocks]
        self.assertEqual(trainableBlockConfigs, [self.trainableBlock.get_config()])

    def test_model_get_loss(self):
        modelLoss = self.nonTrainableModel.get_loss(
            targets=self.exampleTargets,
            training=False,
            **self.exampleInputs
        )
        self.assertEqual(modelLoss.numpy(), self.expectedLoss)

    def test_model_produce_metrics(self):
        metrics = self.nonTrainableModel.produce_metrics(
            targets=self.exampleTargets,
            training=False,
            globalStep=100,
            **self.exampleInputs
        )
        self.assertTrue((metrics.numpy() == self.exampleInputs['input1'].numpy()).all())

    def test_model_get_outputs(self):
        modelOutput = self.nonTrainableModel.get_outputs(**self.exampleInputs)
        self.assertTrue((modelOutput.numpy() == self.nonTrainableExpectedOutput).all())

    def test_model_get_evaluation_outputs(self):
        modelOutput = self.nonTrainableModel.get_evaluation_outputs(**self.exampleInputs)
        self.assertTrue((modelOutput.numpy() == self.nonTrainableExpectedOutput).all())
