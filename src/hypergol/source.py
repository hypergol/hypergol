from collections.abc import Iterable

from hypergol.repr import Repr
from hypergol.logger import Logger

class SourceIteratorNotIterableException(Exception):
    pass


class Source(Repr):
    """Class for single-threaded execution and creating datasets"""

    def __init__(self, outputDataset, logger=None):
        """
        Parameters
        ----------
        outputDataset : Dataset
            output dataset
        """
        self.outputDataset = outputDataset
        self.logger = logger or Logger()

    def source_iterator(self):
        """Must be implemented in the derived class, iterates over and yield's data that is fed into the :func:`run()` functions
        """
        raise NotImplementedError(f'f{self.__class__.__name__} must implement source_iterator()')

    def execute(self):
        """Organising the execution of the task: open's outputDataset for writing, iterates over :func:`source_iterator()` and calls :func:`run` with the data"""
        with self.outputDataset.open(mode='w') as outputDatasetWriter:
            sourceIterator = self.source_iterator()
            if not isinstance(sourceIterator, Iterable):
                raise SourceIteratorNotIterableException(f'{self.__class__.__name__}.source_iterator is not iterable, use yield instead of return')
            for data in sourceIterator:
                outputDatasetWriter.append(self.run(data))

    def run(self, data):
        """This is the main computation of the task

        Parameters
        ----------
        data : object
            Any data that the :func:`source_iterator()` returns
        """
        raise NotImplementedError('run() function must be implemented')
