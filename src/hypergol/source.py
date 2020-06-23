from hypergol.utils import Repr
from collections.abc import Iterable


class SourceIteratorNotIterableException(Exception):
    pass


class Source(Repr):

    def __init__(self, outputDataset):
        self.outputDataset = outputDataset
        # TODO(Laszlo): test that run returns the same class as the type of the dataset (runtime)

    def source_iterator(self):
        raise NotImplementedError(f'f{self.__class__.__name__} must implement source_iterator()')

    def execute(self):
        with self.outputDataset.open(mode='w') as outputDatasetWriter:
            sourceIterator = self.source_iterator()
            if not isinstance(sourceIterator, Iterable):
                raise SourceIteratorNotIterableException(f'{self.__class__.__name__}.source_iterator is not iterable, use yield instead of return')
            for data in sourceIterator:
                outputDatasetWriter.append(self.run(data))

    def run(self, data):
        raise NotImplementedError('run() function must be implemented')
