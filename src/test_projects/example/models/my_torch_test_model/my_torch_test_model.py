import torch
from hypergol import BaseTorchModel


class MyTorchTestModel(BaseTorchModel):

    def __init__(self, block1, block2, **kwargs):
        super(MyTorchTestModel, self).__init__(**kwargs)
        self.block1 = block1
        self.block2 = block2

    def get_loss(self, targets, training, exampleInput1, exampleInput2):
        raise NotImplementedError('BaseTorchModel must implement get_loss()')
        # calculate loss here and return it
        # input arguments must be the same in all three functions
        # and match with the keys of the return value of BatchProcessor.process_training_batch()

    def get_outputs(self, exampleInput1, exampleInput2):
        raise NotImplementedError('BaseTorchModel must implement get_outputs()')
        # calculate the output here and return it, update the decorator accordingly

    def produce_metrics(self, targets, training, globalStep, exampleInput1, exampleInput2s):
        # use tf.summary to record statistics in training/evaluation cycles like
        # tf.summary.scalar(name='exampleName', data=value, step=globalStep)
        pass
