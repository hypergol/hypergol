import numpy as np
import tensorflow as tf
from hypergol.base_batch_processor import BaseBatchProcessor
from hypergol.base_data import BaseData
from hypergol.base_tensorflow_model_block import BaseTensorflowModelBlock
from hypergol.base_tensorflow_model import BaseTensorflowModel


class ExampleOutputDataClass(BaseData):

    def __init__(self, id_: int, value1: int, predictionTarget: int, modelPrediction: int):
        self.id_ = id_
        self.value1 = value1
        self.predictionTarget = predictionTarget
        self.modelPrediction = modelPrediction

    def get_id(self):
        return (self.id_, )

    def __hash__(self):
        return hash((self.id_, self.value1, self.modelPrediction))


class ExampleBatchProcessor(BaseBatchProcessor):

    def __init__(self, inputDataset, inputBatchSize, outputDataset):
        super(ExampleBatchProcessor, self).__init__(inputDataset=inputDataset, inputBatchSize=inputBatchSize, outputDataset=outputDataset)

    def process_input_batch(self, batch):
        # sorting needs to happen for testing, because impossible to know ordering of items that come out of dataset
        inputs = {
            'batchIds': sorted([v.id_ for v in batch]),
            'input1': sorted([v.value1 for v in batch]),
            'input2': sorted([v.value1 + 1 for v in batch])
        }
        targets = sorted([v.value1 for v in batch])
        return inputs, targets

    def process_output_batch(self, inputs, targets, outputs):
        outputData = []
        for k, batchId in enumerate(inputs['batchIds']):
            outputData.append(ExampleOutputDataClass(
                id_=batchId,
                value1=inputs['input1'][k],
                predictionTarget=targets[k],
                modelPrediction=outputs[k]
            ))
        return outputData


class ExampleTensorflowBatchProcessor(BaseBatchProcessor):

    def __init__(self, inputDataset, inputBatchSize, outputDataset):
        super(ExampleTensorflowBatchProcessor, self).__init__(inputDataset=inputDataset, inputBatchSize=inputBatchSize, outputDataset=outputDataset)

    def process_input_batch(self, batch):
        inputs = {
            'batchIds': [v.id_ for v in batch],
            'input1': tf.constant([[v.value1, v.value1 + 1, v.value1 + 2] for v in batch], dtype=tf.float32)
        }
        targets = tf.constant([v.value1 for v in batch], dtype=tf.float32)
        return inputs, targets

    def process_output_batch(self, modelInputs, modelOutputs):
        outputData = []
        for index, batchId in enumerate(modelInputs['batchIds']):
            outputData.append(ExampleOutputDataClass(
                id_=batchId,
                value1=int(modelInputs['inputs']['input1'][index, 0].numpy()),
                predictionTarget=int(modelInputs['targets'].numpy()[index]),
                modelPrediction=int(modelOutputs.numpy()[index, 0])
            ))
        return outputData


class ExampleNonTrainableBlock(BaseTensorflowModelBlock):

    def __init__(self, **kwargs):
        super(ExampleNonTrainableBlock, self).__init__(**kwargs)
        self.softmaxLayer = tf.keras.layers.Softmax(axis=-1)

    def get_output(self, inputs):
        return self.softmaxLayer(inputs)


class ExampleTrainableBlock(BaseTensorflowModelBlock):

    def __init__(self, requiredOutputSize, **kwargs):
        super(ExampleTrainableBlock, self).__init__(**kwargs)
        self.requiredOutputSize = requiredOutputSize
        self.exampleDenseLayer = tf.keras.layers.Dense(units=self.requiredOutputSize)

    def get_output(self, inputs):
        return self.exampleDenseLayer(inputs)


class TensorflowModelExample(BaseTensorflowModel):

    def __init__(self, exampleBlock, **kwargs):
        super(TensorflowModelExample, self).__init__(**kwargs)
        self.exampleBlock = exampleBlock

    # rename this to something, was call() before
    def get_call(self, inputs, **kwargs):
        return self.exampleBlock(inputs['input1'])

    def get_loss(self, outputs, targets):
        return tf.reduce_sum(outputs - targets)

    def produce_metrics(self, inputs, outputs, targets):
        return inputs['input1']

    @ tf.function(input_signature=[tf.TensorSpec(shape=[1, 3], dtype=tf.float32, name="tensorInput")])
    def get_outputs(self, tensorInput):
        return self.exampleBlock(tensorInput)
