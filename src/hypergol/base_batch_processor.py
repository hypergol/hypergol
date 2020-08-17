

class BaseBatchProcessor:
    """
    Base class for batch processors.

    Converts Hypergol datasets to batches for training models and converts tensorflow model outputs to Datamodel classes and then saves them.
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
        self.datasetWriter = None

    def start(self):
        """:class:`.TensorflowModelManager` calls this to open the output for writing"""
        self.datasetWriter = self.outputDataset.open('w')

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
        """Additional batch processing code for model-specific uses

        Must return (inputs, targets) tuple, where inputs is a dictionary of tensors, where keys matching the last arguments of functions ``get_loss()``, ``produce_metrics()`` and ``get_outputs()`` in the implemented model.

        Parameters
        ----------
        batch: List[BaseData]
            Values to be converted into tensors
        """
        raise NotImplementedError(f'{self.__class__.__name__} must implement `process_input_batch`')

    def save_batch(self, inputs, targets, outputs):
        """Saves batch of model inputs + targets + outputs into Hypergol dataset"""
        for value in self.process_output_batch(inputs=inputs, targets=targets, outputs=outputs):
            self.datasetWriter.append(value)

    def process_output_batch(self, inputs, targets, outputs):
        """Processing code for saving batches of model inputs + targets + outputs into Hypergol dataset
        Must return an instance compatible with ``self.outputDataset``.

        Parameters
        ----------
        inputs :
            Created by `process_input_batch()`
        targets :
            Created by `process_input_batch()`
        outputs :
            Model response to `inputs`
        """
        raise NotImplementedError(f'{self.__class__.__name__} must implement `process_output_batch`')

    def finish(self):
        """:class:`.TensorflowModelManager` calls this to close the output after writing

        This function runs even if training was stopped by Ctrl-C, otherwise the Dataset would remain in an undefinied state (with no ``.chk`` file).
        """
        if self.datasetWriter is not None:
            self.datasetWriter.close()
        self.datasetWriter = None
