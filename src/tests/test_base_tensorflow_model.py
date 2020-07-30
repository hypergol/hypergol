import numpy as np
import tensorflow as tf
from unittest import TestCase
from hypergol.base_tensorflow_model_block import BaseTensorflowModelBlock
from hypergol.base_tensorflow_model import BaseTensorflowModel

tf.config.experimental.set_visible_devices([], 'GPU')


class ExampleNonTrainableBlock(BaseTensorflowModelBlock):

    def __init__(self, **kwargs):
        super(ExampleNonTrainableBlock, self).__init__(**kwargs)
        self.softmaxLayer = None

    def build(self, inputs_shape):
        self.softmaxLayer = tf.keras.layers.Softmax(axis=-1)

    def call(self, inputs, **kwargs):
        return self.softmaxLayer(inputs)


class ExampleTrainableBlock(BaseTensorflowModelBlock):

    def __init__(self, requiredOutputSize, **kwargs):
        super(ExampleTrainableBlock, self).__init__(**kwargs)
        self.requiredOutputSize = requiredOutputSize
        self.exampleDenseLayer = None

    def build(self, inputs_shape):
        self.exampleDenseLayer = tf.keras.layers.Dense(units=self.requiredOutputSize)

    def call(self, inputs, **kwargs):
        return self.exampleDenseLayer(inputs)


class ModelExample(BaseTensorflowModel):

    def __init__(self, exampleBlock, **kwargs):
        super(ModelExample, self).__init__(**kwargs)
        self.exampleBlock = exampleBlock

    def call(self, inputs, **kwargs):
        return self.exampleBlock(inputs)

    def get_loss(self, outputs, targets):
        return tf.reduce_sum(outputs - targets)

    def get_metrics(self, inputs, outputs, targets):
        return inputs

    @tf.function(input_signature=[tf.TensorSpec(shape=[1, 3], dtype=tf.float32, name="tensorInput")])
    def get_outputs(self, tensorInput):
        return self.call(inputs=tensorInput, training=False)


class TestBaseTensorflowModel(TestCase):

    def __init__(self, methodName='runTest'):
        super(TestBaseTensorflowModel, self).__init__(methodName=methodName)
        self.exampleEmbeddingSize = 10
        self.exampleInput = tf.constant([[2, 3, 4]], dtype=tf.float32)
        self.nonTrainableExpectedOutput = np.array([[0.09003057, 0.24472848, 0.66524094]], dtype=np.float32)
        self.exampleTargets = tf.constant([[1, 2, 3]], dtype=tf.float32)
        self.expectedLoss = -5

    def setUp(self):
        super().setUp()
        self.trainableBlock = ExampleTrainableBlock(requiredOutputSize=self.nonTrainableExpectedOutput.shape[1])
        self.nonTrainableBlock = ExampleNonTrainableBlock()
        self.trainableModel = ModelExample(exampleBlock=self.trainableBlock)
        self.nonTrainableModel = ModelExample(exampleBlock=self.nonTrainableBlock)

    def tearDown(self):
        super().tearDown()

    def test_non_trainable_model_call(self):
        modelOutput = self.nonTrainableModel(inputs=self.exampleInput)
        self.assertTrue((modelOutput.numpy() == self.nonTrainableExpectedOutput).all())

    def test_trainable_model_call(self):
        modelOutput1 = self.trainableModel(inputs=self.exampleInput)
        weights1 = self.trainableModel.exampleBlock.exampleDenseLayer.weights[0].numpy()  # need numpy calls here, otherwise reference to tensor is stored and updated
        modelOutput2 = self.trainableModel(inputs=self.exampleInput)
        weights2 = self.trainableModel.exampleBlock.exampleDenseLayer.weights[0].numpy()
        self.assertTrue((modelOutput1.numpy() == modelOutput2.numpy()).all())
        self.assertNotEqual(weights1, np.array([]))
        self.assertNotEqual(weights2, np.array([]))
        self.assertTrue((weights1 == weights2).all())

    def test_model_get_loss(self):
        modelLoss = self.nonTrainableModel.get_loss(outputs=self.nonTrainableExpectedOutput, targets=self.exampleTargets)
        self.assertEqual(modelLoss.numpy(), self.expectedLoss)

    def test_model_train(self):
        self.trainableModel(inputs=self.exampleInput)  # first call initializes layers and weights
        weights1 = self.trainableModel.exampleBlock.exampleDenseLayer.weights[0].numpy()
        self.trainableModel.train(inputs=self.exampleInput, targets=self.exampleTargets, optimizer=tf.keras.optimizers.Adam(lr=1))
        weights2 = self.trainableModel.exampleBlock.exampleDenseLayer.weights[0].numpy()
        self.assertNotEqual(weights1, np.array([]))
        self.assertNotEqual(weights2, np.array([]))
        self.assertFalse((weights1 == weights2).all())

    def test_model_get_metrics(self):
        metrics = self.nonTrainableModel.get_metrics(inputs=self.exampleInput, outputs=self.nonTrainableExpectedOutput, targets=self.exampleTargets)
        self.assertTrue((metrics.numpy() == self.exampleInput.numpy()).all())

    def test_non_trainable_model_evaluate(self):
        outputs = self.nonTrainableModel(inputs=self.exampleInput, training=False)
        modelLoss = self.nonTrainableModel.get_loss(outputs=self.nonTrainableExpectedOutput, targets=self.exampleTargets)
        metrics = self.nonTrainableModel.get_metrics(inputs=self.exampleInput, outputs=self.nonTrainableExpectedOutput, targets=self.exampleTargets)
        evaluationOutput = self.nonTrainableModel.evaluate(inputs=self.exampleInput, targets=self.exampleTargets)
        self.assertTrue((evaluationOutput[0].numpy() == outputs.numpy()).all())
        self.assertTrue(evaluationOutput[1] == modelLoss.numpy())
        self.assertTrue((evaluationOutput[2].numpy() == metrics.numpy()).all())

    def test_trainable_model_evaluate(self):
        self.trainableModel(inputs=self.exampleInput)
        weights1 = self.trainableModel.exampleBlock.exampleDenseLayer.weights[0].numpy()
        self.nonTrainableModel.evaluate(inputs=self.exampleInput, targets=self.exampleTargets)
        weights2 = self.trainableModel.exampleBlock.exampleDenseLayer.weights[0].numpy()
        self.assertNotEqual(weights1, np.array([]))
        self.assertNotEqual(weights2, np.array([]))
        self.assertTrue((weights1 == weights2).all())

    def test_model_get_outputs(self, **kwargs):
        modelOutput = self.nonTrainableModel.get_outputs(tensorInput=self.exampleInput)
        self.assertTrue((modelOutput.numpy() == self.nonTrainableExpectedOutput).all())

    def test_model_get_signatures(self):
        modelSignatures = self.nonTrainableModel.get_signatures()
        signatureOutput = modelSignatures['signature_default'](self.exampleInput)
        self.assertTrue((signatureOutput.numpy() == self.nonTrainableExpectedOutput).all())
