

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
        inputBatchSize: int
            number of samples to retrieve
        outputDataset: Dataset
            Hypergol dataset to save batches of model-processed samples
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

    def save_batch(self, inputs, targets, outputs):
        """Saves batch of model inputs + outputs into Hypergol dataset"""
        with self.outputDataset.open('w') as datasetWriter:
            for value in self.process_output_batch(inputs=inputs, targets=targets, outputs=outputs):
                datasetWriter.append(value)

    def process_output_batch(self, inputs, targets, outputs):
        """Processing code for saving batches of model inputs + outputs into Hypergol dataset"""
        raise NotImplementedError(f'{self.__class__.__name__} must implement `process_output_batch`')
