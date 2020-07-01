import logging

from typing import List
from hypergol.delayed import Delayed
from hypergol.dataset import Dataset
from hypergol.utils import Repr


class Job(Repr):

    def __init__(self, inputChunks, outputChunk, loadedInputChunks, jobIndex, jobCount, force):
        self.inputChunks = inputChunks
        self.outputChunk = outputChunk
        self.loadedInputChunks = loadedInputChunks
        self.jobIndex = jobIndex
        self.jobCount = jobCount
        self.force = force


class JobReport(Repr):

    def __init__(self, outputChecksum):
        self.outputChecksum = outputChecksum


class SimpleTask(Repr):

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

    def get_jobs(self):
        jobs = []
        if len({inputDataset.chunkCount for inputDataset in self.inputDatasets + self.loadedInputDatasets}) > 1:
            raise ValueError(f'{self.__class__.__name__}: All datasets must have the same number of chunks')
        if self.inputDatasets[0].chunkCount != self.outputDataset.chunkCount:
            raise ValueError(f'{self.__class__.__name__}: Input and output datasets must have the same number of chunks')
        for jobIndex, outputChunk in enumerate(self.outputDataset.get_data_chunks(mode='w')):
            jobs.append(Job(
                inputChunks=[],
                outputChunk=outputChunk,
                loadedInputChunks=[],
                jobIndex=jobIndex,
                jobCount=self.inputDatasets[0].chunkCount,
                force=self.force
            ))
        for inputDataset in self.inputDatasets:
            for jobIndex, inputChunk in enumerate(inputDataset.get_data_chunks(mode='r')):
                jobs[jobIndex].inputChunks.append(inputChunk)
        for loadedInputDataset in self.loadedInputDatasets:
            for jobIndex, loadedInputChunk in enumerate(loadedInputDataset.get_data_chunks(mode='r')):
                jobs[jobIndex].loadedInputChunks.append(loadedInputChunk)
        return jobs

    def execute(self, job):
        if not isinstance(job, Job):
            raise ValueError(f'{self.__class__.__name__}.execute() argument must be of type Job')
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
        logging.info(f'{self.__class__.__name__} - {job.jobIndex:3}/{job.jobCount:3} - execute - START')
        for k, v in self.__dict__.items():
            if isinstance(v, Delayed):
                setattr(self, k, v.make())
        inputChunks = [inputChunk.open() for inputChunk in job.inputChunks]
        outputChunk = job.outputChunk.open()
        loadedData = []
        for loadInputChunk in job.loadedInputChunks:
            loadInputChunkIterator = loadInputChunk.open()
            loadedData.append(list(loadInputChunkIterator))
            loadInputChunk.close()
        self.init()
        for inputData in zip(*inputChunks):
            if len({value.get_hash_id() for value in inputData}) > 1 and not job.force:
                raise ValueError('different hashIds in the input of a single run() call, set force=True in the task to continue')
            outputChunk.append(self.run(*inputData, *loadedData))
        for inputChunk in inputChunks:
            inputChunk.close()
        outputChecksum = outputChunk.close()
        logging.info(f'{self.__class__.__name__} - {job.jobIndex:3}/{job.jobCount:3} - execute - END')
        return JobReport(outputChecksum=outputChecksum)

    def init(self):
        pass

    def run(self, *args, **kwargs):
        raise NotImplementedError('run() function must be implemented')
