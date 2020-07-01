from hypergol.base_task import BaseTask
from hypergol.base_task import Job
from hypergol.base_task import JobReport
from hypergol.dataset import DatasetFactory


class Task(BaseTask):

    def __init__(self, outputDataset, *args, **kwargs):
        super(Task, self).__init__(outputDataset, *args, **kwargs)
        self.output = None
        self.datasetFactory = DatasetFactory(
            location=outputDataset.location,
            project=outputDataset.project,
            branch=f'{outputDataset.name}_temp',
            chunkCount=outputDataset.chunkCount,
            repoData=outputDataset.repoData
        )

    def _get_temporary_dataset(self, inputChunkId):
        return self.datasetFactory.get(
            dataType=self.outputDataset.dataType,
            name=f'{self.outputDataset.name}_{inputChunkId}',
            chunkCount=self.outputDataset.chunkCount
        )

    def execute(self, job: Job):
        self.init()
        self.log(f'{job.jobIndex:3}/{job.jobCount:3} - execute - START')
        self._open_chunks(job)
        with self._get_temporary_dataset(self.inputChunks[0].chunkId).open('w') as self.output:
            for inputData in zip(*self.inputChunks):
                if not self.force:
                    self._check_same_hash(inputData)
                self.run(*inputData, *self.loadedData)
        outputChecksum = self._close_chunks()
        self.log(f'{job.jobIndex:3}/{job.jobCount:3} - execute - END')
        return JobReport(outputChecksum=outputChecksum)

    def run(self, *args, **kwargs):
        raise NotImplementedError(f'run() function must be implemented in {self.__class__.__name__}')

    def finish(self, jobReports):
        raise ValueError('not done yet')
        # self.log(f'{job.jobIndex:3}/{job.jobCount:3} - finish - START')

        # pool = Pool(task.threads or threads)
        # jobReports = pool.map(task.execute, task.get_jobs())
        # task.finish(jobReports=jobReports)
        # pool.close()
        # pool.join()
        # pool.terminate()


        # checksums = [jobReport.outputChecksum for jobReport in jobReports]
        # self.log(f'{job.jobIndex:3}/{job.jobCount:3} - finish - END')
        # self.outputDataset.make_chk_file(checksums=checksums)
