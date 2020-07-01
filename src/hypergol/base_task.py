import logging

from typing import List
from hypergol.delayed import Delayed
from hypergol.dataset import Dataset
from hypergol.utils import Repr


class Job(Repr):

    def __init__(self, inputChunks, outputChunk, loadedInputChunks, jobIndex, jobCount):
        self.inputChunks = inputChunks
        self.outputChunk = outputChunk
        self.loadedInputChunks = loadedInputChunks
        self.jobIndex = jobIndex
        self.jobCount = jobCount


class JobReport(Repr):

    def __init__(self, outputChecksum):
        self.outputChecksum = outputChecksum


class BaseTask(Repr):

    def __init__(self, inputDatasets: List[Dataset], outputDataset: Dataset, loadedInputDatasets: List[Dataset] = None, threads=None, force=False):
        if len(inputDatasets) == 0:
            raise ValueError('If there are no inputs to this task use Source')
        self.inputDatasets = inputDatasets
        self.outputDataset = outputDataset
        self.loadedInputDatasets = loadedInputDatasets or []
        for inputDataset in self.inputDatasets:
            self.outputDataset.add_dependency(dataset=inputDataset)
        for loadedInputDataset in self.loadedInputDatasets:
            self.outputDataset.add_dependency(dataset=loadedInputDataset)
        self.threads = threads
        self.force = force
        self.inputChunks = None
        self.outputChunk = None
        self.loadedData = None

    def _check_same_hash(self, inputData):
        if len({value.get_hash_id() for value in inputData}) > 1:
            raise ValueError(f'different hashIds in the input of a single run() call, set force=True in {self.__class__.__name__} to continue')

    def _check_same_chunk_count(self):
        chunkCount = self.inputDatasets[0].chunkCount
        for inputDataset in self.inputDatasets + self.loadedInputDatasets:
            if inputDataset.chunkCount != chunkCount:
                raise ValueError(f'{self.__class__.__name__}: All datasets must have the same number of chunks: {inputDataset.name} != {chunkCount}')
        if self.outputDataset.chunkCount != chunkCount:
            raise ValueError(f'{self.__class__.__name__}: Input and output datasets must have the same number of chunks: {self.outputDataset.name} != {chunkCount}')

    def get_jobs(self):
        jobs = []
        self._check_same_chunk_count()
        for jobIndex, outputChunk in enumerate(self.outputDataset.get_data_chunks(mode='w')):
            jobs.append(Job(
                inputChunks=[],
                outputChunk=outputChunk,
                loadedInputChunks=[],
                jobIndex=jobIndex,
                jobCount=self.inputDatasets[0].chunkCount
            ))
        for inputDataset in self.inputDatasets:
            for jobIndex, inputChunk in enumerate(inputDataset.get_data_chunks(mode='r')):
                jobs[jobIndex].inputChunks.append(inputChunk)
        for loadedInputDataset in self.loadedInputDatasets:
            for jobIndex, loadedInputChunk in enumerate(loadedInputDataset.get_data_chunks(mode='r')):
                jobs[jobIndex].loadedInputChunks.append(loadedInputChunk)
        return jobs

    def init(self):
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
        for k, v in self.__dict__.items():
            if isinstance(v, Delayed):
                setattr(self, k, v.make())

    def log(self, message):
        logging.info(f'{self.__class__.__name__} - {message}')

    def _open_input_chunks(self, job):
        self.inputChunks = [inputChunk.open() for inputChunk in job.inputChunks]
        self.loadedData = []
        for loadInputChunk in job.loadedInputChunks:
            loadInputChunkIterator = loadInputChunk.open()
            self.loadedData.append(list(loadInputChunkIterator))
            loadInputChunk.close()

    def _close_input_chunks(self):
        for inputChunk in self.inputChunks:
            inputChunk.close()

    def execute(self, job: Job):
        raise NotImplementedError(f'execute() function must be implemented in {self.__class__.__name__}')

    def run(self, *args, **kwargs):
        raise NotImplementedError(f'run() function must be implemented in {self.__class__.__name__}')

    def finish(self, jobReports, threads):
        raise NotImplementedError(f'finish() function must be implemented in {self.__class__.__name__}')
