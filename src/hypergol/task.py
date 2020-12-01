from collections.abc import Iterable

from hypergol.base_task import BaseTask
from hypergol.base_task import Job
from hypergol.base_task import JobReport


class SourceIteratorNotIterableException(Exception):
    pass


class Task(BaseTask):
    """Class to create other datasets, created domain objects in :func:`run()` must be appended to the output with ``self.output.append(object)`` (any number of the same type)
    """

    def execute(self, job: Job):
        """Organising the execution of the task, see Tutorial/Task for a detailed description of steps

        Parameters
        ----------
        job : Job
            parameters of chunks to be opened
        """
        self.initialise()
        self.log(f'{job.id:3}/{job.total:3} - execute - START')
        self._open_input_chunks(job)
        with self._get_temporary_dataset(jobId=job.id).open('w') as self.output:
            sourceIterator = self.source_iterator()
            if not isinstance(sourceIterator, Iterable):
                raise SourceIteratorNotIterableException(f'{self.__class__.__name__}.source_iterator is not iterable, use yield instead of return')
            for inputData in sourceIterator:
                if not self.force:
                    self._check_if_same_hash(inputData)
                self.run(*inputData, *self.loadedData)
        self._close_input_chunks()
        self.log(f'{job.id:3}/{job.total:3} - execute - END')
        return JobReport(outputChecksum=0)

    def run(self, *args, **kwargs):
        """Main computation

        Input arguments will be an element from each inputDataset followed by the list of loadedInputDatasets
        Append domain object to self.output to store in in the output dataset.
        """
        raise NotImplementedError(f'run() function must be implemented in {self.__class__.__name__}')
