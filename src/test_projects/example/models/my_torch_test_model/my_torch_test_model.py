import torch
import torch.nn as nn
from hypergol import BaseTorchModel


class MyTorchTestModel(BaseTorchModel):

    def __init__(self, block1, block2, **kwargs):
        super(MyTorchTestModel, self).__init__(**kwargs)
        self.block1 = block1
        self.block2 = block2
        # you must create all pytorch layers here so PytorchScript can save it

    def get_loss(self, targets, training, exampleInput1, exampleInput2):
        raise NotImplementedError('BaseTorchModel must implement get_loss()')
        # calculate loss here and return it
        # input arguments must be the same in all three functions
        # and match with the keys of the return value of BatchProcessor.process_training_batch()

    @torch.jit.export
    def get_outputs(self, exampleInput1, exampleInput2):
        raise NotImplementedError('BaseTorchModel must implement get_outputs()')
        # calculate the output here and return it, update the decorator accordingly
        # use @torch.jit.export to make this function callable in serving by PytorchScript
        # all parameters must be tensors

    def produce_metrics(self, targets, training, globalStep, exampleInput1, exampleInput2s):
        # return a dictionary of {'tag': value} that will be pass to SummariWriter as
        # SummaryWriter.add_scalar(tag=tag, scalar_value=value, global_step=self.globalStep)
        pass
