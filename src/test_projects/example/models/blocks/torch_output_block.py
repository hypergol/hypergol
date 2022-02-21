import torch
import torch.nn as nn
from hypergol import BaseTorchModelBlock


class TorchOutputBlock(BaseTorchModelBlock):

    def __init__(self, exampleParameter1, exampleParameter2, **kwargs):
        super(TorchOutputBlock, self).__init__(**kwargs)
        self.exampleParameter1 = exampleParameter1
        self.exampleParameter2 = exampleParameter2
        # create torch variables or nn layers here

    def get_example(self, tensor1, tensor2):
        # do torch calculations here using arguments and the member variables from the constructor
        pass
