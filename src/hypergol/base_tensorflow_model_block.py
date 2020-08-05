# pylint: disable=E0611, W0235

import inspect
from tensorflow.python.keras import layers


class BaseTensorflowModelBlock(layers.Layer):
    """Subclasses tensorflow-keras layers to provide logical groupings of functionality/layers."""

    def __init__(self, **kwargs):
        super(BaseTensorflowModelBlock, self).__init__(**kwargs)

    def get_config(self):
        constructorParameters = inspect.signature(self.__class__).parameters.keys()
        config = super(BaseTensorflowModelBlock, self).get_config()
        for name, value in self.__dict__.items():
            if name in constructorParameters:
                config[name] = value
        return config

    def get_name(self):
        return self.__class__.__name__

    def build(self, inputs_shape):
        """Contains the layer specification of a given block, attached to instance of the block"""
        raise NotImplementedError(f'Model block {self.__class__} should implement `build` function')

    def call(self, *args, **kwargs):
        """Contains code for how inputs should be processed"""
        raise NotImplementedError(f'Model block {self.__class__} should implement `call` function')
