from torch import nn


class BaseTorchModelBlock(nn.Module):
    """Subclasses Torch's module to provide logical groupings of functionality/layers.
    """

    def __init__(self, *args, blockName=None, **kwargs):
        """Implement layer definitions here"""
        super(BaseTorchModelBlock, self).__init__(*args, **kwargs)
        self.blockName = blockName or self.__class__.__name__

    def forward(self, x):
        """This function is obsolete"""
        raise Exception(f'nn.Module.forward() was called in Hypergol model {self.name}')
