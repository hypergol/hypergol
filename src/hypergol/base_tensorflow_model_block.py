# pylint: disable=E0611, W0235

import inspect

from tensorflow.python.keras import layers


class BaseTensorflowModelBlock(layers.Layer):
    """Subclasses TensorFlow-Keras  layers to provide logical groupings of functionality/layers.

        Neither ``call()`` nor ``build()`` should be used as those won't be called eventually by the model

        There are no delayed initialisation in Hypergol models.
    """

    def __init__(self, *args, blockName=None, **kwargs):
        """If further keras layers are required, they should be created here"""
        super(BaseTensorflowModelBlock, self).__init__(*args, **kwargs)
        self.blockName = blockName or self.__class__.__name__

    def get_config(self):
        """Function to get the configuration parameters for serialisation"""
        constructorParameters = inspect.signature(self.__class__.__init__).parameters.keys()
        config = super(BaseTensorflowModelBlock, self).get_config()
        for name, value in self.__dict__.items():
            if name in constructorParameters:
                config[name] = value
        return config

    def build(self, input_shape):
        """This should not be called"""
        raise Exception(f'keras.Layer.build() was called in Hypergol block {self.__class__.__name__}')

    def call(self, *args, **kwargs):
        """This should not be called"""
        raise Exception(f'keras.Layer.call() was called in Hypergol block {self.__class__.__name__}')
