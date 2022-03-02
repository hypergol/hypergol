from torch import nn


class BaseTorchModelBlock(nn.Module):
    """Subclasses Torch's module to provide logical groupings of functionality/layers.
    """

    def __init__(self, *args, blockName=None, **kwargs):
        """Implement layer definitions here"""
        super(BaseTorchModelBlock, self).__init__(*args, **kwargs)
        self.blockName = blockName or self.__class__.__name__

    def forward(self, x): # pylint: disable=R0201
        # R0201: Method could be a function (no-self-use)
        """This function is obsolete"""
        raise Exception('nn.Module.forward() was called in Hypergol model BaseTorchModelBlock')
