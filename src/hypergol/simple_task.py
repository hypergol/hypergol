from hypergol.base_task import BaseTask
from hypergol.base_task import Job
from hypergol.base_task import JobReport


class SimpleTask(BaseTask):

    def execute(self, job: Job):
        self.initialise()
        self.log(f'{job.jobIndex:3}/{job.jobCount:3} - execute - START')
        self._open_input_chunks(job)
        self.outputChunk = job.outputChunk.open()
        for inputData in zip(*self.inputChunks):
            if not self.force:
                self._check_same_hash(inputData)
            self.outputChunk.append(self.run(*inputData, *self.loadedData))
        self._close_input_chunks()
        outputChecksum = self.outputChunk.close()
        self.log(f'{job.jobIndex:3}/{job.jobCount:3} - execute - END')
        return JobReport(outputChecksum=outputChecksum)

    def run(self, *args, **kwargs):
        raise NotImplementedError(f'run() function must be implemented in {self.__class__.__name__}')

    def finalise(self, jobReports, threads):
        checksums = [jobReport.outputChecksum for jobReport in jobReports]
        self.outputDataset.make_chk_file(checksums=checksums)
        self.finish(jobReports, threads)
