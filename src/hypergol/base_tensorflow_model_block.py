# pylint: disable=E0611, W0235

import inspect
from tensorflow.python.keras import layers


class BaseTensorflowModelBlock(layers.Layer):
    """Subclasses tensorflow-keras layers to provide logical groupings of functionality/layers."""

    def __init__(self, *args, **kwargs):
        super(BaseTensorflowModelBlock, self).__init__(*args, **kwargs)

    def get_config(self):
        constructorParameters = inspect.signature(self.__class__.__init__).parameters.keys()
        config = super(BaseTensorflowModelBlock, self).get_config()
        for name, value in self.__dict__.items():
            if name in constructorParameters:
                config[name] = value
        return config

    def get_name(self):
        return self.__class__.__name__

    def build(self, input_shape):
        raise Exception(f'keras.Layer.build() was called in Hypergol block {self.__class__.__name__}')

    def call(self, *args, **kwargs):
        raise Exception(f'keras.Layer.call() was called in Hypergol block {self.__class__.__name__}')
