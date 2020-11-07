import os
import glob
import gzip
from pathlib import Path
from multiprocessing import Pool

from hypergol.base_task import BaseTask
from hypergol.base_task import Job
from hypergol.base_task import JobReport
from hypergol.dataset_factory import DatasetFactory


class Task(BaseTask):
    """Class to create other datasets, created domain objects in :func:`run()` must be appended to the output with ``self.output.append(object)`` (any number of the same type)
    """

    def __init__(self, outputDataset, *args, **kwargs):
        """
        Also creates dataset factory for temporary datasets
        """
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
        """Based on the input chunk creates a temporary dataset and opens all chunks for writing so that the various output classes can be appended to the right chunk"""
        return self.datasetFactory.get(
            dataType=self.outputDataset.dataType,
            name=f'{self.outputDataset.name}_{inputChunkId}',
            chunkCount=self.outputDataset.chunkCount
        )

    def execute(self, job: Job):
        """Same as :class:`SimpleTask` apart from :func:`run()` doesn't have a return value because output is updated by calling ``self.output.append()``
        """
        self.initialise()
        self.log(f'{job.jobIndex:3}/{job.jobCount:3} - execute - START')
        self._open_input_chunks(job)
        with self._get_temporary_dataset(self.inputChunks[0].chunkId).open('w') as self.output:
            for inputData in zip(*self.inputChunks):
                if not self.force:
                    self._check_if_same_hash(inputData)
                self.run(*inputData, *self.loadedData)
        self._close_input_chunks()
        self.log(f'{job.jobIndex:3}/{job.jobCount:3} - execute - END')
        return JobReport(outputChecksum=0)

    def run(self, *args, **kwargs):
        raise NotImplementedError(f'run() function must be implemented in {self.__class__.__name__}')

    def finalise(self, jobReports, threads):
        """After func:`execute` finished, all the temporary datasets are opened and copied into the output dataset in a multithreaded way.

        Parameters
        ----------
            jobReports : IGNORED
                Checksums's are recalculated for the actual output dataset
            threads :
                Number of concurrent threads to do the merging
        """
        self.outputDataset.delete()
        jobs = [
            (chunk, self.__class__.__name__, k, self.outputDataset.chunkCount, self.logger)
            for k, chunk in enumerate(self.outputDataset.get_data_chunks(mode='w'))
        ]
        if threads == 0:
            checksums = []
            for job in jobs:
                checksums.append(_merge_function(job))
        else:
            pool = Pool(self.threads or threads)
            checksums = pool.map(_merge_function, jobs)
            pool.close()
            pool.join()
            pool.terminate()
        for inputChunkId in self.inputDatasets[0].get_chunk_ids():
            temporaryDataset = self._get_temporary_dataset(inputChunkId)
            temporaryDataset.delete()
        temporayBranchDirectory = Path(self.outputDataset.location, self.outputDataset.project, f'{self.outputDataset.name}_temp')
        try:
            if os.path.exists(temporayBranchDirectory):
                os.rmdir(temporayBranchDirectory)
        except OSError as ex:
            self.log(f'temporary directory cannot be deleted {ex}')
        self.outputDataset.chkFile.make_chk_file(checksums=checksums)
        self.finish(jobReports, threads)


def _merge_function(args):
    """This is the actual function that is running multithreaded. This function must be external to the ``Task`` class because, after initialising and execution, it is not possible to ensure that the ``Task`` class is pickle-able.

    Returns the checksum so the caller can create the ``.chk`` file.
    """
    chunk, name, k, total, logger = args
    logger.log(f'{name} - {k:3}/{total:3} - finish - START')
    chunk.open()
    pattern = str(Path(
        chunk.dataset.location, chunk.dataset.project, f'{chunk.dataset.name}_temp',
        f'{chunk.dataset.name}_*', f'*_{chunk.chunkId}.jsonl.gz'
    ))
    for filePath in sorted(glob.glob(pattern)):
        with gzip.open(filePath, 'rt') as inputFile:
            for line in inputFile:
                chunk.write(line)
    logger.log(f'{name} - {k:3}/{total:3} - finish - END')
    return chunk.close()
