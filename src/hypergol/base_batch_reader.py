import tensorflow as tf


class BaseBatchReader:

    """
    Base class for batch readers.

    Converts Hypergol datasets to tensorflow datasets for CPU prefetching of batches.
    """

    def __init__(self, dataset, batchSize):
        """

        Parameters
        ----------
        dataset: Dataset
            Hypergol dataset to retrieve batches from
        batchSize: int
            number of samples to retrieve
        """
        self.dataset = dataset
        self.batchSize = batchSize
        self.datasetIterator = iter(tf.data.Dataset.from_generator(
            generator=self.read_batch(),
            output_types=self.outputTypes
        ).prefetch(1))

    def __next__(self):
        return next(self.datasetIterator)

    def read_batch(self):
        """Reads in Hypergol dataset as a generator"""
        batch = []
        while True:
            for value in self.dataset.open('r'):
                batch.append(value)
                if len(batch) == self.batchSize:
                    yield self.process_batch(batch)
                    batch = []

    def process_batch(self, batch):
        """Additional batch processing code for model-specific uses"""
        raise NotImplementedError(f'{self.__class__.__name__} must implement process_batch')

    @property
    def outputTypes(self):
        """Output types for tensors after batch has been processed"""
        raise NotImplementedError(f'{self.__class__.__name__} must implement tensorBatchTypes')
