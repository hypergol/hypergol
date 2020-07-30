import numpy as np
import shutil
import tensorflow as tf
from pathlib import Path
from unittest import TestCase
from hypergol.base_tensorflow_model_block import BaseTensorflowModelBlock
from hypergol.base_tensorflow_model import BaseTensorflowModel

tf.config.experimental.set_visible_devices([], 'GPU')


class ExampleTrainableBlock(BaseTensorflowModelBlock):

    def __init__(self, exampleEmbeddingSize, **kwargs):
        super(ExampleTrainableBlock, self).__init__(**kwargs)
        self.exampleEmbeddingSize = exampleEmbeddingSize
        self.exampleDenseLayer = None
        self.softmaxLayer = None

    def build(self, inputs_shape):
        self.exampleDenseLayer = tf.keras.layers.Dense(units=self)
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

    @tf.function(input_signature=[tf.TensorSpec(shape=[1, 3], dtype=tf.float32, name="tensorInput")])
    def get_outputs(self, tensorInput):
        return self.call(inputs=tensorInput, training=False)


class TestBaseTensorflowModel(TestCase):

    def __init__(self, methodName='runTest'):
        super(TestBaseTensorflowModel, self).__init__(methodName=methodName)
        self.location = 'test_tensorflow_model'
        self.exampleEmbeddingSize = 1
        self.exampleInput = tf.constant([[2, 3, 4]], dtype=tf.float32)
        self.expectedOutput = np.array([[0.09003057, 0.24472848, 0.66524094]], dtype=np.float32)
        self.exampleTargets = tf.constant([[1, 2, 3]], dtype=tf.float32)

    def setUp(self):
        super().setUp()
        Path(self.location).mkdir()
        self.exampleBlock = ExampleTrainableBlock(exampleEmbeddingSize=self.exampleEmbeddingSize)
        self.model = ModelExample(exampleBlock=self.exampleBlock)

    def tearDown(self):
        super().tearDown()
        shutil.rmtree(self.location)

    def test_model_call(self):
        modelOutput = self.model(self.exampleInput)
        self.assertEqual(modelOutput.numpy(), self.expectedOutput)

    def test_model_train(self):
        self.model(self.expectedInput)  # first call initializes layers and weights
        firstWeights = self.model.exampleBlock.exampleDenseLayer.weights
        self.model.train(inputs=self.exampleInput, targets=self.exampleTargets, optimizer=tf.keras.optimizers.Adam(lr=0.07))
        secondWeights = self.model.exampleBlock.exampleDenseLayer.weights
        self.assertNotEqual(firstWeights, secondWeights)

    def test_model_get_loss(self):
        modelLoss = self.model.get_loss(outputs=self.expectedOutput, targets=self.exampleTargets)
        self.assertEqual(modelLoss, -5)

    def test_model_get_metrics(self):
        metrics = self.model.get_metrics(inputs=self.exampleInput, outputs=self.expectedOutput, targets=self.exampleTargets)
        self.assertSequenceEqual(metrics, (self.exampleInput, self.expectedOutput, self.exampleTargets))

    def test_model_evaluate(self, inputs, targets):
        outputs = self.model(self.exampleInput)
        modelLoss = self.model.get_loss(outputs=self.expectedOutput, targets=self.exampleTargets)
        metrics = self.model.get_metrics(inputs=self.exampleInput, outputs=self.expectedOutput, targets=self.exampleTargets)
        evaluateOutput = self.model.evaluate(inputs=self.exampleInput, targets=self.exampleTargets)
        self.assertSequenceEqual(evaluateOutput, (outputs, modelLoss, metrics))

    def test_model_get_outputs(self, **kwargs):
        modelOutput = self.model.get_outputs(tensorInput=self.exampleInput)
        self.assertEqual(modelOutput.numpy(), self.expectedOutput)

    def test_model_get_signatures(self):
        modelSignatures = self.model.get_signatures()
        signatureOutput = modelSignatures['signature_default'](inputTensor=self.exampleInput)
        self.assertEqual(signatureOutput, self.expectedOutput)
