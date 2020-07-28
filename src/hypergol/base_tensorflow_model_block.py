import inspect
import json
from tensorflow.python.keras import layers


class BaseTensorflowModelBlock(layers.Layer):
    """Subclasses tensorflow-keras layers to provide logical groupings of functionality/layers."""

    def __init__(self, **kwargs):
        super(BaseTensorflowModelBlock, self).__init__(**kwargs)

    def get_config(self):
        parameters = {k: v for k, v in self.__dict__.items() if k in inspect.signature(self.__class__).parameters.keys()}
        config = super(BaseTensorflowModelBlock, self).get_config()
        for name, value in parameters.items():
            config.update({name: value})
        return config

    def get_name(self):
        return self.__class__.__name__

    def save_to_dictionary(self, directory):
        json.dump(self.get_config(), open(f'{directory}/{self.get_name()}.json', 'w'))

    @classmethod
    def load_from_dictionary(cls, directory):
        return cls.from_config(config=json.load(open(f'{directory}/{cls.__name__}.json', 'r')))

    def build(self, inputs_shape):
        """Contains the layer specification of a given block, attached to instance of the block"""
        raise NotImplementedError(f'Model block {self.__class__} should implement `build` function')

    def call(self, inputs, **kwargs):
        """Contains code for how inputs should be processed"""
        raise NotImplementedError(f'Model block {self.__class__} should implement `call` function')
