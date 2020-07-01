from hypergol.base_task import BaseTask
from hypergol.base_task import Job
from hypergol.base_task import JobReport


class SimpleTask(BaseTask):

    def execute(self, job: Job):
        self.init()
        self.log(f'{job.jobIndex:3}/{job.jobCount:3} - execute - START')
        self._open_chunks(job)
        for inputData in zip(*self.inputChunks):
            if not self.force:
                self._check_same_hash(inputData)
            self.outputChunk.append(self.run(*inputData, *self.loadedData))
        outputChecksum = self._close_chunks()
        self.log(f'{job.jobIndex:3}/{job.jobCount:3} - execute - END')
        return JobReport(outputChecksum=outputChecksum)

    def run(self, *args, **kwargs):
        raise NotImplementedError(f'run() function must be implemented in {self.__class__.__name__}')

    def finish(self, jobReports):
        checksums = [jobReport.outputChecksum for jobReport in jobReports]
        self.outputDataset.make_chk_file(checksums=checksums)
