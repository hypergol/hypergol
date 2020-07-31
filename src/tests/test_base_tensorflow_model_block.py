import numpy as np
import shutil
import tensorflow as tf
from pathlib import Path
from unittest import TestCase
from tests.example_tensorflow_classes import ExampleNonTrainableBlock
from tests.example_tensorflow_classes import ExampleTrainableBlock

tf.config.experimental.set_visible_devices([], 'GPU')


class TestBaseTensorflowModelBlock(TestCase):

    def __init__(self, methodName='runTest'):
        super(TestBaseTensorflowModelBlock, self).__init__(methodName=methodName)
        self.location = 'test_tensorflow_model_block'
        self.exampleEmbeddingSize = 1
        self.exampleLogits = tf.constant([[2, 3, 4]], dtype=tf.float32)
        self.expectedOutput = np.array([[0.09003057, 0.24472848, 0.66524094]], dtype=np.float32)

    def setUp(self):
        super().setUp()
        Path(self.location).mkdir()
        self.blockWithConstructionParam = ExampleTrainableBlock(requiredOutputSize=self.exampleEmbeddingSize)
        self.nonTrainableBlock = ExampleNonTrainableBlock()
        self.blockSaveFile = f'{self.location}/{self.blockWithConstructionParam.get_name()}.json'

    def tearDown(self):
        super().tearDown()
        shutil.rmtree(self.location)

    def test_block_build(self):
        self.blockWithConstructionParam.build(inputs_shape=0)
        self.assertNotEqual(self.blockWithConstructionParam.exampleDenseLayer, None)

    def test_block_call(self):
        self.nonTrainableBlock.build(inputs_shape=0)
        outputTensor = self.nonTrainableBlock(self.exampleLogits)
        self.assertTrue((outputTensor.numpy() == self.expectedOutput).all())

    def test_get_config(self):
        self.blockWithConstructionParam.build(inputs_shape=0)
        config = self.blockWithConstructionParam.get_config()
        self.assertEqual(config['requiredOutputSize'], self.exampleEmbeddingSize)
