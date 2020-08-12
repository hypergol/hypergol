import tensorflow as tf
from hypergol import BaseBatchProcessor
from data_models.model_output import ModelOutput


class MyTestModelBatchProcessor(BaseBatchProcessor):

    def __init__(self, inputDataset, inputBatchSize, outputDataset, exampleArgument):
        super(MyTestModelBatchProcessor, self).__init__(inputDataset, inputBatchSize, outputDataset)
        self.exampleArgument = exampleArgument

    def process_input_batch(self, batch):
        raise NotImplementedError('BaseBatchProcessor must implement process_input_batch()')
        # batch is a list of datamodel objects cycle through them and build the data
        # that can be converted to tensorflow constants, e.g.:
        # exampleInput1 = []
        # exampleInput2 = []
        # exampleOutput = []
        # for exampleValue in batch:
        #      exampleInput1.append(exampleValue.exampleList)
        #      exampleInput2.append(len(exampleValue.exampleList))
        #      exampleOutput.append(exampleValue.exampleOutputList)
        # inputs = {
        #     'exampleInput1': tf.ragged.constant(lemmas, dtype=tf.string).to_tensor()[:, 10]
        #     'exampleInput2': tf.constant(sentenceLengths, dtype=tf.int32)
        # }
        # targets = tf.ragged.constant(, dtype=tf.string).to_tensor()[:, :10]
        return inputs, targets

    def process_output_batch(self, inputs, targets, outputs):
        raise NotImplementedError('BaseBatchProcessor must implement process_output_batch()')
        # create a list of data model classes from the argument, output classes must have an id because they will be saved into a dataset
        # outputBatch = []
        # for id_, i, t, o in zip(inputs['ids'], inputs, targets, outputs):
        #     outputBatch.append(ExampleOutput(eoid=id_, i=i, t=t, o=o)
        # return  outputBatch