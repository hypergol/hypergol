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

    def call(self, inputs, **kwargs):
        raise NotImplementedError(f'{self.__class__} model must implement `call` method')

    def train(self, inputs, targets, optimizer):
        with tf.GradientTape() as tape:
            outputs = self.call(inputs=inputs, training=True)
            loss = self.get_loss(outputs=outputs, targets=targets)
        grads = tape.gradient(loss, self.trainable_variables)
        optimizer.apply_gradients(zip(grads, self.trainable_variables))
        return loss

    def evaluate(self, inputs, targets):
        outputs = self.call(inputs=inputs, training=False)
        loss = self.get_loss(outputs=outputs, targets=targets)
        metrics = self.produce_metrics(inputs=inputs, outputs=outputs, targets=targets)
        return outputs, loss, metrics

    def get_loss(self, outputs, targets):
        raise NotImplementedError('Must implement `get_loss` function')

    def produce_metrics(self, inputs, outputs, targets):
        raise NotImplementedError('Must implement `produce_metrics` function')

    def get_outputs(self, **kwargs):
        raise NotImplementedError('Must implement `get_outputs` function')

    def get_signatures(self):
        return {'signature_default': self.get_outputs}
