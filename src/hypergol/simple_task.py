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

        self._open_input_chunks(job)
        self.initialise()
        self.log(f'{job.jobIndex:3}/{job.jobCount:3} - execute - START')
        self.outputChunk = job.outputChunk.open()
        for inputValues in zip(*self.inputChunks):
            outputValue = self.run(*inputValues, *self.loadedData)
            if not self.force:
                self._check_if_same_hash(inputValues, outputValue)
            self.outputChunk.append(outputValue)
        self._close_input_chunks()
        outputChecksum = self.outputChunk.close()
        self.log(f'{job.jobIndex:3}/{job.jobCount:3} - execute - END')
        return JobReport(outputChecksum=outputChecksum)

    def run(self, *args, **kwargs):
        """Main computation

        must return the domain object that will be saved in the output dataset
        """
        raise NotImplementedError(f'run() function must be implemented in {self.__class__.__name__}')

    def finalise(self, jobReports, threads):
        """Collects the checksums and creates the output dataset's ``.chk`` file
        Parameters
        ----------
        jobReports : List[JobReport]
            Result of each run which contains the checkSum of the output file
        threads : unused
        """
        checksums = [jobReport.outputChecksum for jobReport in jobReports]
        self.outputDataset.chkFile.make_chk_file(checksums=checksums)
        self.finish(jobReports, threads)
