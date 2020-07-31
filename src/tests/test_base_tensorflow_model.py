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
        self.exampleInputs = {'input1': tf.constant([[2, 3, 4]], dtype=tf.float32)}
        self.nonTrainableExpectedOutput = np.array([[0.09003057, 0.24472848, 0.66524094]], dtype=np.float32)
        self.exampleTargets = tf.constant([[1, 2, 3]], dtype=tf.float32)
        self.expectedLoss = -5

    def setUp(self):
        super().setUp()
        self.trainableBlock = ExampleTrainableBlock(requiredOutputSize=self.nonTrainableExpectedOutput.shape[1])
        self.nonTrainableBlock = ExampleNonTrainableBlock()
        self.trainableModel = TensorflowModelExample(exampleBlock=self.trainableBlock)
        self.nonTrainableModel = TensorflowModelExample(exampleBlock=self.nonTrainableBlock)

    def tearDown(self):
        super().tearDown()

    def test_get_model_blocks(self):
        nonTrainableBlocks = self.nonTrainableModel.get_model_blocks()
        nonTrainableBlockConfigs = [block.get_config() for block in nonTrainableBlocks]
        self.assertEqual(nonTrainableBlockConfigs, [self.nonTrainableBlock.get_config()])
        trainableBlocks = self.trainableModel.get_model_blocks()
        trainableBlockConfigs = [block.get_config() for block in trainableBlocks]
        self.assertEqual(trainableBlockConfigs, [self.trainableBlock.get_config()])

    def test_non_trainable_model_call(self):
        modelOutput = self.nonTrainableModel(inputs=self.exampleInputs)
        self.assertTrue((modelOutput.numpy() == self.nonTrainableExpectedOutput).all())

    def test_trainable_model_call(self):
        modelOutput1 = self.trainableModel(inputs=self.exampleInputs)
        weights1 = self.trainableModel.exampleBlock.exampleDenseLayer.weights[0].numpy()  # need numpy calls here, otherwise reference to tensor is stored and updated
        modelOutput2 = self.trainableModel(inputs=self.exampleInputs)
        weights2 = self.trainableModel.exampleBlock.exampleDenseLayer.weights[0].numpy()
        self.assertTrue((modelOutput1.numpy() == modelOutput2.numpy()).all())
        self.assertNotEqual(weights1, np.array([]))
        self.assertNotEqual(weights2, np.array([]))
        self.assertTrue((weights1 == weights2).all())

    def test_model_get_loss(self):
        modelLoss = self.nonTrainableModel.get_loss(outputs=self.nonTrainableExpectedOutput, targets=self.exampleTargets)
        self.assertEqual(modelLoss.numpy(), self.expectedLoss)

    def test_model_train(self):
        self.trainableModel(inputs=self.exampleInputs)  # first call initializes layers and weights
        weights1 = self.trainableModel.exampleBlock.exampleDenseLayer.weights[0].numpy()
        self.trainableModel.train(inputs=self.exampleInputs, targets=self.exampleTargets, optimizer=tf.keras.optimizers.Adam(lr=1))
        weights2 = self.trainableModel.exampleBlock.exampleDenseLayer.weights[0].numpy()
        self.assertNotEqual(weights1, np.array([]))
        self.assertNotEqual(weights2, np.array([]))
        self.assertFalse((weights1 == weights2).all())

    def test_model_produce_metrics(self):
        metrics = self.nonTrainableModel.produce_metrics(inputs=self.exampleInputs, outputs=self.nonTrainableExpectedOutput, targets=self.exampleTargets)
        self.assertTrue((metrics.numpy() == self.exampleInputs['input1'].numpy()).all())

    def test_non_trainable_model_evaluate(self):
        outputs = self.nonTrainableModel(inputs=self.exampleInputs, training=False)
        modelLoss = self.nonTrainableModel.get_loss(outputs=self.nonTrainableExpectedOutput, targets=self.exampleTargets)
        metrics = self.nonTrainableModel.produce_metrics(inputs=self.exampleInputs, outputs=self.nonTrainableExpectedOutput, targets=self.exampleTargets)
        evaluationOutput = self.nonTrainableModel.evaluate(inputs=self.exampleInputs, targets=self.exampleTargets)
        self.assertTrue((evaluationOutput[0].numpy() == outputs.numpy()).all())
        self.assertTrue(evaluationOutput[1] == modelLoss.numpy())
        self.assertTrue((evaluationOutput[2].numpy() == metrics.numpy()).all())

    def test_trainable_model_evaluate(self):
        self.trainableModel(inputs=self.exampleInputs)
        weights1 = self.trainableModel.exampleBlock.exampleDenseLayer.weights[0].numpy()
        self.nonTrainableModel.evaluate(inputs=self.exampleInputs, targets=self.exampleTargets)
        weights2 = self.trainableModel.exampleBlock.exampleDenseLayer.weights[0].numpy()
        self.assertNotEqual(weights1, np.array([]))
        self.assertNotEqual(weights2, np.array([]))
        self.assertTrue((weights1 == weights2).all())

    def test_model_get_outputs(self):
        modelOutput = self.nonTrainableModel.get_outputs(tensorInput=self.exampleInputs['input1'])
        self.assertTrue((modelOutput.numpy() == self.nonTrainableExpectedOutput).all())

    def test_model_get_signatures(self):
        modelSignatures = self.nonTrainableModel.get_signatures()
        signatureOutput = modelSignatures['signature_default'](self.exampleInputs['input1'])
        self.assertTrue((signatureOutput.numpy() == self.nonTrainableExpectedOutput).all())
