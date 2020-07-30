# pylint: disable=E0611, W0235

import tensorflow as tf
from tensorflow.python import keras


class BaseTensorflowModel(keras.Model):

    def __init__(self, **kwargs):
        super(BaseTensorflowModel, self).__init__(**kwargs)

    def call(self, inputs, training, **kwargs):
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
        metrics = self.get_metrics(inputs=inputs, outputs=outputs, targets=targets)
        return outputs, loss, metrics

    def get_loss(self, outputs, targets):
        raise NotImplementedError('Must implement `get_loss` function')

    def get_metrics(self, inputs, outputs, targets):
        raise NotImplementedError('Must implement `get_metrics` function')

    def get_outputs(self, **kwargs):
        raise NotImplementedError('Must implement `get_outputs` function')

    def get_signatures(self):
        return {'signature_default': self.get_outputs}
