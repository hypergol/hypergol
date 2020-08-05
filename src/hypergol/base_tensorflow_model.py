# pylint: disable=E0611, W0235

import inspect
import tensorflow as tf
from tensorflow.python import keras
from hypergol.base_tensorflow_model_block import BaseTensorflowModelBlock


class BaseTensorflowModel(keras.Model):

    def __init__(self, **kwargs):
        super(BaseTensorflowModel, self).__init__(**kwargs)

    def get_model_blocks(self):
        constructorParameters = inspect.signature(self.__class__).parameters.keys()
        return [v for k, v in self.__dict__.items() if k in constructorParameters and isinstance(v, BaseTensorflowModelBlock)]

    def get_name(self):
        return self.__class__.__name__

    def call(self, inputs, training=None, mask=None):
        raise NotImplementedError(f'{self.__class__} model must implement `call` method')

    def train(self, inputs, targets, optimizer):
        with tf.GradientTape() as tape:
            loss = self.get_loss(inputs=inputs, targets=targets, training=True)
        grads = tape.gradient(loss, self.trainable_variables)
        optimizer.apply_gradients(zip(grads, self.trainable_variables))
        return loss

    def eval(self, inputs, targets, globalStep):
        loss = self.get_loss(inputs=inputs, targets=targets, training=False)
        outputs = self.produce_metrics(inputs=inputs, targets=targets, training=False, globalStep=globalStep)
        return loss, outputs

    def get_loss(self, inputs, targets, training):
        raise NotImplementedError('Must implement `get_loss` function')

    def produce_metrics(self, inputs, targets, training, globalStep):
        raise NotImplementedError('Must implement `produce_metrics` function')

    def get_outputs(self, **kwargs):
        raise NotImplementedError('Must implement `get_outputs` function')
