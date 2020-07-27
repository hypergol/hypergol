import inspect
import json
from tensorflow.python.keras import layers


class BaseModelBlock(layers.Layer):
    """Subclasses tensorflow-keras layers to provide logical groupings of functionality/layers."""

    def __init__(self, *args, **kwargs):
        super(BaseModelBlock, self).__init__(*args, **kwargs)

    def get_config(self):
        parameters = {k: v for k, v in self.__dict__.items() if k in inspect.signature(self.__class__).parameters.keys()}
        config = super(BaseModelBlock, self).get_config()
        for name, value in parameters.items():
            config.update({name: value})
        return config

    def save_to_dictionary(self, directory):
        json.dump(self.get_config(), open(f'{directory}/{self.__class__.__name__}.json', 'w'))

    @classmethod
    def load_from_dictionary(cls, directory):
        return cls.from_config(config=json.load(open(f'{directory}/{cls.__name__}.json', 'r')))

    def copy(self, **kwargs):
        config = self.get_config()
        return self.__class__.from_config(config={**config, **kwargs})

    def build(self, inputs_shape):
        """Contains the layer specification of a given block, attached to instance of the block"""
        raise NotImplementedError(f'Model block {self.__class__} should implement `build` function')

    def call(self, inputs, *args, **kwargs):
        """Contains code for how inputs should be processed"""
        raise NotImplementedError(f'Model block {self.__class__} should implement `call` function')
