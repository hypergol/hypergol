import numpy as np
import os
import tensorflow as tf
from pathlib import Path
from unittest import TestCase
from hypergol.base_tensorflow_model_block import BaseTensorflowModelBlock
tf.config.experimental.set_visible_devices([], 'GPU')


class ModelBlockExample(BaseTensorflowModelBlock):

    def __init__(self, exampleEmbeddingSize, **kwargs):
        super(ModelBlockExample, self).__init__(**kwargs)
        self.exampleEmbeddingSize = exampleEmbeddingSize
        self.softmaxLayer = None

    def build(self, inputs_shape):
        self.softmaxLayer = tf.keras.layers.Softmax(axis=-1)

    def call(self, inputs, **kwargs):
        return self.softmaxLayer(inputs)


class TestBaseTensorflowModelBlock(TestCase):

    def __init__(self, methodName='runTest'):
        super(TestBaseTensorflowModelBlock, self).__init__(methodName=methodName)
        self.location = 'test_tensorflow_model_block'
        self.exampleEmbeddingSize = 1

    def setUp(self):
        super().setUp()
        Path(self.location).mkdir()
        self.block = ModelBlockExample(exampleEmbeddingSize=self.exampleEmbeddingSize)
        self.blockSaveFile = f'{self.location}/{self.block.get_name()}.json'
        self.logits = tf.constant([2, 3, 4], dtype=tf.float32)
        self.expectedOutput = np.array([0.09003057, 0.24472848, 0.66524094], dtype=np.float32)

    def tearDown(self):
        super().tearDown()
        try:
            os.remove(self.blockSaveFile)
        except FileNotFoundError:
            pass
        os.rmdir(self.location)

    def test_block_build(self):
        self.block.build(inputs_shape=0)

    def test_block_call(self):
        self.block.build(inputs_shape=0)
        outputTensor = self.block(self.logits)
        self.assertTrue((outputTensor.numpy() == self.expectedOutput).all())

    def test_get_config(self):
        self.block.build(inputs_shape=0)
        config = self.block.get_config()
        self.assertEqual(config['exampleEmbeddingSize'], self.exampleEmbeddingSize)

    def test_dictionary_round_trip(self):
        self.block.build(inputs_shape=0)
        self.block.save_to_dictionary(directory=self.location)
        newBlock = ModelBlockExample.load_from_dictionary(directory=self.location)
        self.assertEqual(self.block.get_config(), newBlock.get_config())
