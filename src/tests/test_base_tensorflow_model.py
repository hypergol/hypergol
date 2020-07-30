import numpy as np
import os
import shutil
import tensorflow as tf
from pathlib import Path
from unittest import TestCase
from hypergol.base_tensorflow_model import BaseTensorflowModel

from .test_base_tensorflow_model_block import ModelBlockExample
tf.config.experimental.set_visible_devices([], 'GPU')


class ModelExample(BaseTensorflowModel):

    def __init__(self, exampleBlock, **kwargs):
        super(ModelExample, self).__init__(**kwargs)
        self.exampleBlock = exampleBlock

    def call(self, inputs, training, **kwargs):
        return self.exampleBlock(inputs)

    def get_loss(self, outputs, targets):
        return np.sum(outputs - targets)

    def get_metrics(self, inputs, outputs, targets):
        return inputs, outputs, targets

    @tf.function(input_signature=tf.TensorSpec(shape=[1, 3], dtype=tf.float32, name="tensorInput"))
    def get_outputs(self, tensorInput):
        return self.call(inputs=tensorInput, training=False)


class TestBaseTensorflowModel(TestCase):

    def __init__(self, methodName='runTest'):
        super(TestBaseTensorflowModel, self).__init__(methodName=methodName)
        self.location = 'test_tensorflow_model'
        self.exampleEmbeddingSize = 1
        self.exampleLogits = tf.constant([2, 3, 4], dtype=tf.float32)
        self.expectedOutput = np.array([0.09003057, 0.24472848, 0.66524094], dtype=np.float32)

    def setUp(self):
        super().setUp()
        Path(self.location).mkdir()
        self.exampleBlock = ModelBlockExample(exampleEmbeddingSize=self.exampleEmbeddingSize)
        self.model = ModelExample(exampleBlock=self.exampleBlock)
        # self.blockSaveFile = f'{self.location}/{self.block.get_name()}.json'

    def tearDown(self):
        super().tearDown()
        shutil.rmtree(self.location)

    # def test_block_build(self):
    #     self.block.build(inputs_shape=0)
    #
    # def test_block_call(self):
    #     self.block.build(inputs_shape=0)
    #     outputTensor = self.block(self.exampleLogits)
    #     self.assertTrue((outputTensor.numpy() == self.expectedOutput).all())
    #
    # def test_get_config(self):
    #     self.block.build(inputs_shape=0)
    #     config = self.block.get_config()
    #     self.assertEqual(config['exampleEmbeddingSize'], self.exampleEmbeddingSize)
    #
    # def test_dictionary_round_trip(self):
    #     self.block.build(inputs_shape=0)
    #     self.block.save_to_dictionary(directory=self.location)
    #     newBlock = ModelBlockExample.load_from_dictionary(directory=self.location)
    #     self.assertEqual(self.block.get_config(), newBlock.get_config())
