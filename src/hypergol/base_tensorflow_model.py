import inspect
import tensorflow as tf
from tensorflow.python import keras

from hypergol.base_tensorflow_model_block import BaseTensorflowModelBlock


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

    def save_variables(self, path):
        self.save_weights(f'{path}/{self.__class__.__name__}.h5', save_format='h5')

    def restore_variables(self, path):
        self.load_weights(f'{path}/{self.__class__.__name__}.h5')

    def checkpoint(self, path, packageModel=False):
        if packageModel:
            self.package_model(path=f'{path}/packaged_model')
        parameters = {k: v for k, v in self.__dict__.items() if k in inspect.signature(self.__class__).parameters.keys()}
        for k, v in parameters.items():
            if isinstance(v, BaseTensorflowModelBlock):
                v.save_to_dictionary(directory=path)
        self.save_variables(path=path)

    def get_outputs(self, **kwargs):
        raise NotImplementedError('Must implement `get_outputs` function')

    def get_signatures(self):
        return {'signature_default': self.get_outputs}

    def package_model(self, path):
        tf.saved_model.save(self, export_dir=path, signatures=self.get_signatures())
