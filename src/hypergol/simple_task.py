from hypergol.base_task import BaseTask
from hypergol.base_task import Job
from hypergol.base_task import JobReport


class SimpleTask(BaseTask):
    """Class to do simple update style processing, each :func:`run()` call must get inputs with the same if and create a class that has the same id as well
    """

    def execute(self, job: Job):
        """Organising the execution of the task, see Tutorial/SimpleTask for a detailed description of steps

        Parameters
        ----------
        job : Job
            parameters of chunks to be opened
        """
        self.initialise()
        self.log(f'{job.id:3}/{job.total:3} - execute - START')
        self._open_input_chunks(job)
        with self._get_temporary_dataset(jobId=job.id).open('w') as self.output:
            for inputValues in zip(*self.inputChunks):
                if not self.force:
                    self._check_if_same_hash(inputValues)
                self.run(*inputValues, *self.loadedData)
        self._close_input_chunks()
        self.log(f'{job.id:3}/{job.total:3} - execute - END')
        return JobReport(outputChecksum=0)

    def run(self, *args, **kwargs):
        """Main computation

        Input arguments will be an element from each inputDataset followed by the list of loadedInputDatasets
        Append domain object to self.output to store in in the output dataset.
        """
        raise NotImplementedError(f'run() function must be implemented in {self.__class__.__name__}')
