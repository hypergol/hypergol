import os
import glob
import gzip
from pathlib import Path
from multiprocessing import Pool
from typing import List
from types import GeneratorType

from hypergol.delayed import Delayed
from hypergol.dataset import Dataset

from hypergol.job import Job
from hypergol.job_report import JobReport
from hypergol.repr import Repr
from hypergol.logger import Logger
from hypergol.dataset_factory import DatasetFactory
from hypergol.dataset import DatasetAlreadyExistsException


class SourceIteratorNotIterableException(Exception):
    pass


class Task(Repr):
    """Class to create other datasets, created domain objects in :func:`run()` must be appended to the output with ``self.output.append(object)`` (any number of the same type)
    """

    def __init__(self, outputDataset: Dataset, inputDatasets: List[Dataset] = None, loadedInputDatasets: List[Dataset] = None, logger=None, threads=None, logAtEachN=0, debug=False, force=False):
        """
        Parameters
        ----------

        outputDataset: Dataset
            Return values of ``.run()`` functions will be saved into the chunks of this dataset.
        inputDatasets: List[Dataset]
            Chunks of these will be loaded line by line and passed onto the ``.run()`` function in each thread.
        loadedInputDatasets: List[Dataset] = None
            Data from these will be available in each job as a list.
        logger: Logger
            Standard logger class for each of the jobs
        threads: int = None
            Number of threads this task should run parallel
        logAtEachN: int = 0
            Log progress at each of the value, default = 0 means no logs
        debug: bool = False
            If true errors during execution stop the pipeline, otherwise they just get logged.
        force: bool = False
            All input object's hashes must match in a single run() call. Use ``force=True`` to override this.
        """
        self.outputDataset = outputDataset
        self.inputDatasets = inputDatasets or []
        self.loadedInputDatasets = loadedInputDatasets or []
        for inputDataset in self.inputDatasets:
            self.outputDataset.add_dependency(dataset=inputDataset)
        for loadedInputDataset in self.loadedInputDatasets:
            self.outputDataset.add_dependency(dataset=loadedInputDataset)
        self.logger = logger or Logger()
        self.threads = threads
        self.logAtEachN = logAtEachN
        self.debug = debug
        self.force = force
        self.output = None      # <------- Append data modell instances to this variable in the run() function to be saved in the output dataset
        self.inputChunks = None
        self.loadedData = None
        self.results = None
        self.exceptions = False
        self.counter = 0
        self.jobId = None
        self.jobTotal = None
        self.temporaryDatasetFactory = DatasetFactory(
            location=outputDataset.location,
            project='temp',
            branch=f'{outputDataset.name}_temp',
            chunkCount=outputDataset.chunkCount,
            repoData=outputDataset.repoData
        )

    def check_if_output_exists(self):
        if self.outputDataset.exists():
            raise DatasetAlreadyExistsException(f"Dataset {self.outputDataset.directory} already exists, delete the dataset first with Dataset.delete()")
        if os.path.exists(self.temporaryDatasetFactory.branchDirectory):
            raise DatasetAlreadyExistsException(f"Temporary data location {self.temporaryDatasetFactory.branchDirectory} already exists, delete the directory first")

    def _get_temporary_dataset(self, jobId):
        """Based on the input chunk creates a temporary dataset and opens all chunks for writing so that the various output classes can be appended to the right chunk"""
        return self.temporaryDatasetFactory.get(dataType=self.outputDataset.dataType, name=f'{self.outputDataset.name}_{jobId:03}')

    def log(self, message):
        """Standard logging"""
        self.logger.info(f'{self.__class__.__name__} - {self.jobId:3}/{self.jobTotal:3} - {message}')

    def log_exception(self, ex):
        self.log(ex)
        self.exceptions = True
        if self.debug:
            raise ex

    def log_counter(self, final=False):
        self.counter += 1
        if self.logAtEachN != 0 and (self.counter % self.logAtEachN == 0 or final):
            self.log(f'Processed: {self.counter}')

    def get_jobs(self):
        """Generates a list of :class:`Job` to be processed"""
        chunkCounts = {v.chunkCount for v in self.inputDatasets + self.loadedInputDatasets}
        if len(chunkCounts) > 1:
            raise ValueError(f'{self.__class__.__name__}: All datasets must have the same number of chunks: {chunkCounts}')
        jobs = [Job(id_=id_, total=self.inputDatasets[0].chunkCount) for id_ in range(self.inputDatasets[0].chunkCount)]
        for inputDataset in self.inputDatasets:
            for id_, inputChunk in enumerate(inputDataset.get_data_chunks(mode='r')):
                jobs[id_].inputChunks.append(inputChunk)
        for loadedInputDataset in self.loadedInputDatasets:
            for id_, loadedInputChunk in enumerate(loadedInputDataset.get_data_chunks(mode='r')):
                jobs[id_].loadedInputChunks.append(loadedInputChunk)
        return jobs

    def execute(self, job: Job):
        """Organising the execution of the task, see Tutorial/Task for a detailed description of steps

        Parameters
        ----------
        job : Job
            parameters of chunks to be opened
        """
        self.jobId = job.id
        self.jobTotal = job.total
        self.log('Execute - START')
        try:
            self._open_input_chunks(job=job)
            self.initialise()
            with self._get_temporary_dataset(jobId=job.id).open('w') as self.output:
                sourceIterator = self.source_iterator(parameters=job.parameters)
                if not isinstance(sourceIterator, GeneratorType):
                    raise SourceIteratorNotIterableException(f'{self.__class__.__name__}.source_iterator is not iterable, use yield instead of return')
                for inputData in sourceIterator:
                    self.log_counter()
                    try:
                        self.run(*inputData, *self.loadedData)
                    except Exception as ex:  # pylint: disable=broad-except
                        self.log_exception(ex)
            self._close_input_chunks()
            self.log_counter(final=True)
        except Exception as ex:  # pylint: disable=broad-except
            self.log_exception(ex)
        self.log('Execute - END')
        jobReport = JobReport(jobId=job.id, exceptions=self.exceptions, results=self.results)
        self.finish_job(jobReport=jobReport)
        return jobReport

    def initialise(self):
        """After opening input chunks and loading loaded inputs, creates :term:`delayed` classes, initialises the results to be returned in JobReports and calls the task's custom `init()`"""
        for k, v in self.__dict__.items():
            if isinstance(v, Delayed):
                setattr(self, k, v.make())
        self.results = {}
        self.init()

    def init(self):
        """User-defined initialisation in each thread. Load files or complex classes here (e.g. a spacy model)"""

    def _open_input_chunks(self, job):
        """Opens input chunks and loads loaded input chunks"""
        self.inputChunks = [inputChunk.open() for inputChunk in job.inputChunks]
        self.loadedData = []
        for loadInputChunk in job.loadedInputChunks:
            self.loadedData.append(list(loadInputChunk.open()))
            loadInputChunk.close()

    def source_iterator(self, parameters):
        if len(parameters) > 0:
            raise ValueError('source_iterators in Tasks with inputDatasets cannot have job parameters, pass data as member variables of the Task')
        for inputValues in zip(*self.inputChunks):
            if not self.force and len({value.get_hash_id() for value in inputValues}) > 1:
                raise ValueError(f'different hashIds in a tuple of input values, set force=True in {self.__class__.__name__} to continue')
            yield inputValues

    def run(self, *args):
        """This is the main computation of the task

        Parameters
        ----------
        args: List[object]
            list of single domain objects one from each `inputDataset` in the same order as in the task construction, after these a list of domain objects which is the entire list from the `loadedInputDatasets` list.
        """
        raise NotImplementedError(f'run() function must be implemented in {self.__class__.__name__}')

    def _close_input_chunks(self):
        """Closes input chunks"""
        for inputChunk in self.inputChunks:
            inputChunk.close()

    def finish_job(self, jobReport):
        """User-defined finalisation in each thread. Close file handlers or release memory of non-python objects here if necessary"""

    def finalise(self, jobReports, threads):
        """After func:`execute` finished, all the temporary datasets are opened and copied into the output dataset in a multithreaded way.

        Parameters
        ----------
            jobReports : List[JobReport]
                Reports on the executed jobs
            threads :
                Number of concurrent threads to do the merging
        """
        jobs = []
        for k, chunk in enumerate(self.outputDataset.get_data_chunks(mode='w')):
            jobs.append(Job(
                id_=k,
                total=self.outputDataset.chunkCount,
                parameters={
                    'name': self.__class__.__name__,
                    'chunk': chunk,
                    'logger': self.logger
                }))
        pool = Pool(self.threads or threads)
        checksums = pool.map(_merge_function, jobs)
        pool.close()
        pool.join()
        pool.terminate()
        for jobId in range(len(jobReports)):
            temporaryDataset = self._get_temporary_dataset(jobId=jobId)
            temporaryDataset.delete()
        temporayBranchDirectory = Path(self.outputDataset.location, 'temp', f'{self.outputDataset.name}_temp')
        try:
            if os.path.exists(temporayBranchDirectory):
                os.rmdir(temporayBranchDirectory)
        except OSError as ex:
            self.log(f'temporary directory cannot be deleted {ex}')
        self.outputDataset.chkFile.make_chk_file(checksums=checksums)
        self.finish_task(jobReports=jobReports, threads=threads)

    def finish_task(self, jobReports, threads):
        """User-defined finalisation at the end of the task."""


def _merge_function(job):
    """This is the actual function that is running multithreaded. This function must be external to the ``Task`` class because, after initialising and execution, it is not possible to ensure that the ``Task`` class is pickle-able.

    Returns the checksum so the caller can create the ``.chk`` file.
    """
    chunk = job.parameters['chunk']
    logger = job.parameters['logger']
    logger.log(f'{job.parameters["name"]} - {job.id:3}/{job.total:3} - finish - START')
    chunk.open()
    pattern = str(Path(
        chunk.dataset.location, 'temp', f'{chunk.dataset.name}_temp',
        f'{chunk.dataset.name}_*', f'*_{chunk.chunkId}.jsonl.gz'
    ))
    for filePath in sorted(glob.glob(pattern)):
        with gzip.open(filePath, 'rt') as inputFile:
            for line in inputFile:
                chunk.write(line)
    logger.log(f'{job.parameters["name"]} - {job.id:3}/{job.total:3} - finish - END')
    return chunk.close()
