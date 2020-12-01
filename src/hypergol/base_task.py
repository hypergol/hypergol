import os
import glob
import gzip
from pathlib import Path
from multiprocessing import Pool

from typing import List

from hypergol.delayed import Delayed
from hypergol.dataset import Dataset
from hypergol.repr import Repr
from hypergol.logger import Logger
from hypergol.dataset_factory import DatasetFactory


class Job(Repr):
    """Class for passing information on chunks to tasks"""

    def __init__(self, outputChunk, id_, total, parameters):
        """
        Parameters
        ----------
        outputChunk: DataChunk
            chunk to save objects into
        id_: int
            what's the order of this job in the queue
        number: int
            number of total jobs in this task
        parameters: object
            any information to be passed to the source_iterator()
            In case of a task it will be: {'inputChunks': [], 'loadedInputChunks': []}
        """
        self.outputChunk = outputChunk
        self.id = id_
        self.total = total
        self.parameters = parameters


class JobReport(Repr):
    """Class for passing information from the tasks to the pipeline

    Mainly used to pass the hash of the created chunk data for creating the output dataset's ``.chk`` file.
    """

    def __init__(self, outputChecksum):
        """

        Parameters
        ----------

        outputChecksum: str
            The 40 digit SHA1 checksum of the output file
        """
        self.outputChecksum = outputChecksum


class BaseTask(Repr):
    # TODO(Laszlo): fix this doc
    """Base class for multithreaded abstract class Task"""

    def __init__(self, inputDatasets: List[Dataset], outputDataset: Dataset, loadedInputDatasets: List[Dataset] = None, logger=None, threads=None, force=False):
        """
        Parameters
        ----------

        inputDatasets: List[Dataset]
            Chunks of these will be loaded line by line and passed onto the ``.run()`` function in each thread
        outputDataset: Dataset
            Return value of ``.run()`` will be saved into the chunks of this dataset
        loadedInputDatasets: List[Dataset] = None
            Data from these will be available in each job.
        threads=None
            Number of threads this task should run parallel
        force=False
            All input object's hashes must match in a single run() call. Use ``force=True`` to override this.
        """
        if len(inputDatasets) == 0:
            raise ValueError('If there are no inputs to this task use Source')
        self.inputDatasets = inputDatasets
        self.outputDataset = outputDataset
        self.loadedInputDatasets = loadedInputDatasets or []
        for inputDataset in self.inputDatasets:
            self.outputDataset.add_dependency(dataset=inputDataset)
        for loadedInputDataset in self.loadedInputDatasets:
            self.outputDataset.add_dependency(dataset=loadedInputDataset)
        self.logger = logger or Logger()
        self.threads = threads
        self.force = force
        self.inputChunks = None
        self.outputChunk = None
        self.loadedData = None
        self.output = None
        self.datasetFactory = DatasetFactory(
            location=outputDataset.location,
            project=outputDataset.project,
            branch=f'{outputDataset.name}_temp',
            chunkCount=outputDataset.chunkCount,
            repoData=outputDataset.repoData
        )

    def _get_temporary_dataset(self, jobId):
        """Based on the input chunk creates a temporary dataset and opens all chunks for writing so that the various output classes can be appended to the right chunk"""
        return self.datasetFactory.get(
            dataType=self.outputDataset.dataType,
            name=f'{self.outputDataset.name}_{jobId:03}',
            chunkCount=self.outputDataset.chunkCount
        )

    def _check_if_same_hash(self, inputValues):
        """Raises error if inputs of ``run()`` have different :term:`hash id`"""
        hashIds = {value.get_hash_id() for value in inputValues}
        if len(hashIds) > 1:
            raise ValueError(f'different hashIds in the input of a single run() call, set force=True in {self.__class__.__name__} to continue')

    def _check_same_chunk_count(self):
        """Raises an error if any of the input datasets :term:`chunk count` differs, cannot be overridden by `force=True`"""
        chunkCount = self.inputDatasets[0].chunkCount
        for inputDataset in self.inputDatasets + self.loadedInputDatasets:
            if inputDataset.chunkCount != chunkCount:
                raise ValueError(f'{self.__class__.__name__}: All datasets must have the same number of chunks: {inputDataset.name} != {chunkCount}')

    def source_iterator(self):
        for inputValues in zip(*self.inputChunks):
            yield inputValues

    def get_jobs(self):
        """Generates a list of :class:`Job` to be processed"""
        jobs = []
        self._check_same_chunk_count()
        for id_, outputChunk in enumerate(self.outputDataset.get_data_chunks(mode='w')):
            jobs.append(Job(
                outputChunk=outputChunk,
                id_=id_,
                total=self.inputDatasets[0].chunkCount,
                parameters={
                    'inputChunks': [],
                    'loadedInputChunks': []
                }
            ))
        for inputDataset in self.inputDatasets:
            for id_, inputChunk in enumerate(inputDataset.get_data_chunks(mode='r')):
                jobs[id_].parameters['inputChunks'].append(inputChunk)
        for loadedInputDataset in self.loadedInputDatasets:
            for id_, loadedInputChunk in enumerate(loadedInputDataset.get_data_chunks(mode='r')):
                jobs[id_].parameters['loadedInputChunks'].append(loadedInputChunk)
        return jobs

    def initialise(self):
        """After opening input chunks and loading loaded inputs, creates :term:`delayed` classes and calls the task's custom `init()`"""
        for k, v in self.__dict__.items():
            if isinstance(v, Delayed):
                setattr(self, k, v.make())
        self.init()

    def init(self):
        """User-defined initialisation in each thread. Load files or complex classes here (e.g. a spacy model)"""

    def log(self, message):
        """Standard logging"""
        self.logger.info(f'{self.__class__.__name__} - {message}')

    def _open_input_chunks(self, job):
        """Opens input chunks and loads loaded input chunks"""
        self.inputChunks = [inputChunk.open() for inputChunk in job.parameters['inputChunks']]
        self.loadedData = []
        for loadInputChunk in job.parameters['loadedInputChunks']:
            loadInputChunkIterator = loadInputChunk.open()
            self.loadedData.append(list(loadInputChunkIterator))
            loadInputChunk.close()

    def _close_input_chunks(self):
        """Closes input chunks"""
        for inputChunk in self.inputChunks:
            inputChunk.close()

    def execute(self, job: Job):
        """This function is implemented in the derived :class:`.Task` classes"""
        raise NotImplementedError(f'execute() function must be implemented in {self.__class__.__name__}')

    def run(self, *args):
        """This is the main computation of the task

        Parameters
        ----------
        args: List[object]
            list of single domain objects one from each `inputDataset` in the same order as in the task construction, after these a list of domain objects which is the entire list from the `loadedInputDatasets` list.
        """
        raise NotImplementedError(f'run() function must be implemented in {self.__class__.__name__}')

    def finish(self, jobReports, threads):
        """User-defined finalisation in each thread. Close file handlers or release memory of non-python objects here if necessary"""

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
        for jobId in range(len(jobReports)):
            temporaryDataset = self._get_temporary_dataset(jobId=jobId)
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
