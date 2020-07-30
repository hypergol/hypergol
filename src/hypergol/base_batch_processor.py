

class BaseBatchProcessor:
    """
    Base class for batch readers.

    Converts Hypergol datasets to batches for training models.
    """

    def __init__(self, inputDataset, inputBatchSize, outputDataset):
        """
        Parameters
        ----------
        inputDataset: Dataset
            Hypergol dataset to retrieve batches from
        outputDataset: Dataset
            Hypergol dataset to save batches of model-processed samples
        inputBatchSize: int
            number of samples to retrieve
        """
        self.inputDataset = inputDataset
        self.inputBatchSize = inputBatchSize
        self.outputDataset = outputDataset
        self.datasetIterator = iter(self.read_batch())

    def __next__(self):
        return next(self.datasetIterator)

    def read_batch(self):
        """Reads in Hypergol dataset as a generator"""
        batch = []
        while True:
            for value in self.inputDataset.open('r'):
                batch.append(value)
                if len(batch) == self.inputBatchSize:
                    yield self.process_input_batch(batch=batch)
                    batch = []

    def process_input_batch(self, batch):
        """Additional batch processing code for model-specific uses"""
        raise NotImplementedError(f'{self.__class__.__name__} must implement `process_input_batch`')

    def save_batch(self, modelInputs, modelOutputs):
        """Saves batch of model inputs + outputs into Hypergol dataset"""
        datasetOutputs = self.process_output_batch(modelInputs=modelInputs, modelOutputs=modelOutputs)
        with self.outputDataset.open('w') as datasetWriter:
            for output in datasetOutputs:
                datasetWriter.append(output)

    def process_output_batch(self, modelInputs, modelOutputs):
        """Processing code for saving batches of model inputs + outputs into Hypergol dataset"""
        raise NotImplementedError(f'{self.__class__.__name__} must implement `process_output_batch`')
