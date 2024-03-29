import torch
import torch.nn as nn
from hypergol import BaseTorchModelBlock


class TorchLstmBlock(BaseTorchModelBlock):

    def __init__(self, exampleParameter1, exampleParameter2, **kwargs):
        super(TorchLstmBlock, self).__init__(**kwargs)
        self.exampleParameter1 = exampleParameter1
        self.exampleParameter2 = exampleParameter2
        # you must create all pytorch layers here so PytorchScript can save it

    def get_example(self, tensor1, tensor2):
        # do pytorch calculations here using arguments and the member variables from the constructor
        pass
