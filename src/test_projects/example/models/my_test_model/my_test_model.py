import tensorflow as tf
from hypergol import BaseTensorflowModel


class MyTestModel(BaseTensorflowModel):

    def __init__(self, block1, block2, **kwargs):
        super(MyTestModel, self).__init__(**kwargs)
        self.block1 = block1
        self.block2 = block2

    def get_loss(self, targets, training, exampleInput1, exampleInput2):
        raise NotImplementedError('BaseTensorflowModel must implement get_loss()')
        # calculate loss here and return it
        # input arguments must be the same in all three functions
        # and match with the keys of the return value of BatchProcessor.process_training_batch()

    @tf.function(input_signature=[
        tf.TensorSpec(shape=[None, None], dtype=tf.int32, name='exampleInput1'),
        tf.TensorSpec(shape=[None, None], dtype=tf.string, name='exampleInput2')
    ])
    def get_outputs(self, exampleInput1, exampleInput2):
        raise NotImplementedError('BaseTensorflowModel must implement get_outputs()')
        # calculate the output here and return it, update the decorator accordingly

    def produce_metrics(self, targets, training, globalStep, exampleInput1, exampleInput2s):
        # use tf.summary to record statistics in training/evaluation cycles like
        # tf.summary.scalar(name='exampleName', data=value, step=globalStep)
        pass
