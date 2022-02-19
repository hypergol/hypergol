from torch import nn


class BaseTorchModelBlock(nn.Module):
    """Subclasses Torch's module to provide logical groupings of functionality/layers.
    """

    def __init__(self, *args, blockName=None, **kwargs):
        """Implement layer definitions here"""
        super(BaseTorchModelBlock, self).__init__(*args, **kwargs)
        self.blockName = blockName or self.__class__.__name__

    def forward(self, *args, **kwargs):
        raise NotImplementedError(f'Module.forward() not implemented in Hypergol block {self.__class__.__name__}')
