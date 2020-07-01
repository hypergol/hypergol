import glob
import gzip
from pathlib import Path
from multiprocessing import Pool
from hypergol.base_task import BaseTask
from hypergol.base_task import Job
from hypergol.base_task import JobReport
from hypergol.dataset import DatasetFactory


class Task(BaseTask):

    def __init__(self, outputDataset, *args, **kwargs):
        super(Task, self).__init__(outputDataset=outputDataset, *args, **kwargs)
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

    def finish(self, jobReports, threads):
        def _merge_function(chunk):
            chunk.open()
            pattern = str(Path(
                chunk.dataset.location, chunk.dataset.project, f'{chunk.dataset.name}_temp',
                f'{chunk.dataset.name}_*', f'*_{chunk.chunkId}.json.gz'
            ))
            for filePath in sorted(glob.glob(pattern)):
                with gzip.open(filePath, 'rt') as inputFile:
                    for line in inputFile:
                        chunk.write(line)
            return chunk.close()
        pool = Pool(self.threads or threads)
        checksums = pool.map(_merge_function, self.outputDataset.get_data_chunks(mode='w'))
        pool.close()
        pool.join()
        pool.terminate()
        self.outputDataset.make_chk_file(checksums=checksums)
