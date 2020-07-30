import numpy as np
import shutil
import tensorflow as tf
from pathlib import Path
from unittest import TestCase
from hypergol.base_tensorflow_model import BaseTensorflowModel

from .test_base_tensorflow_model_block import ModelBlockExample
tf.config.experimental.set_visible_devices([], 'GPU')


class ExampleTrainableBlock:

    class ModelBlockExample(BaseTensorflowModelBlock):

    def __init__(self, exampleEmbeddingSize, **kwargs):
        super(ModelBlockExample, self).__init__(**kwargs)
        self.exampleEmbeddingSize = exampleEmbeddingSize
        self.softmaxLayer = None

    def build(self, inputs_shape):
        self.softmaxLayer = tf.keras.layers.Softmax(axis=-1)

    def call(self, inputs, **kwargs):
        return self.softmaxLayer(inputs)


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


    def test_model_call(self, inputs, training, **kwargs):
        raise NotImplementedError(f'{self.__class__} model must implement `call` method')

    def test_model_train(self, inputs, targets, optimizer):
        with tf.GradientTape() as tape:
            outputs = self.call(inputs=inputs, training=True)
            loss = self.get_loss(outputs=outputs, targets=targets)
        grads = tape.gradient(loss, self.trainable_variables)
        optimizer.apply_gradients(zip(grads, self.trainable_variables))
        return loss

    def test_model_evaluate(self, inputs, targets):
        outputs = self.call(inputs=inputs, training=False)
        loss = self.get_loss(outputs=outputs, targets=targets)
        metrics = self.get_metrics(inputs=inputs, outputs=outputs, targets=targets)
        return outputs, loss, metrics

    def test_model_get_loss(self, outputs, targets):
        raise NotImplementedError('Must implement `get_loss` function')

    def test_model_get_metrics(self, inputs, outputs, targets):
        raise NotImplementedError('Must implement `get_metrics` function')

    def test_model_get_outputs(self, **kwargs):
        raise NotImplementedError('Must implement `get_outputs` function')

    def test_model_get_signatures(self):
        return {'signature_default': self.get_outputs}
