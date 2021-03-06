import tensorflow as tf
from tensorflow.keras import layers
from hypergol import BaseTensorflowModelBlock


class EmbeddingBlock(BaseTensorflowModelBlock):

    def __init__(self, exampleParameter1, exampleParameter2, **kwargs):
        super(EmbeddingBlock, self).__init__(**kwargs)
        self.exampleParameter1 = exampleParameter1
        self.exampleParameter2 = exampleParameter2
        # create tensorflow variables or keras.layers here

    def get_example(self, tensor1, tensor2):
        # do tensorflow calculations here using arguments and the member variables from the constructor
        pass
