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
        raise Exception(f'keras.Model.call() was called in Hypergol model {self.name}')

    def get_loss(self, targets, training, **kwargs):
        raise NotImplementedError('Must implement `get_loss` function')

    def produce_metrics(self, targets, training, globalStep, **kwargs):
        raise NotImplementedError('Must implement `produce_metrics` function')

    def get_outputs(self, **kwargs):
        raise NotImplementedError('Must implement `get_outputs` function')

    def get_evaluation_outputs(self, **kwargs):
        return self.get_outputs(**kwargs)
