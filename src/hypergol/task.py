import logging

from typing import List
from hypergol.delayed import Delayed
from hypergol.dataset import Dataset
from hypergol.utils import Repr


class Job(Repr):

    def __init__(self, inputChunks, outputChunk, jobIndex, jobCount):
        self.inputChunks = inputChunks
        self.outputChunk = outputChunk
        self.jobIndex = jobIndex
        self.jobCount = jobCount


class JobReport(Repr):

    def __init__(self, outputChecksum):
        self.outputChecksum = outputChecksum


class Task(Repr):

    def __init__(self, inputDatasets: List[Dataset], outputDataset: Dataset, threads=None):
        if len(inputDatasets) == 0:
            raise ValueError('If there are no inputs to this task use Source')
        self.inputDatasets = inputDatasets
        self.outputDataset = outputDataset
        for inputDataset in self.inputDatasets:
            self.outputDataset.add_dependency(dataset=inputDataset)
        self.threads = threads

    def get_jobs(self):
        jobs = []
        if len({inputDataset.chunks for inputDataset in self.inputDatasets}) > 1:
            raise ValueError(f'{self.__class__.__name__}: All datasets must have the same number of chunks')
        if self.inputDatasets[0].chunks != self.outputDataset.chunks:
            raise ValueError(f'{self.__class__.__name__}: Input and output datasets must have the same number of chunks')
        for jobIndex, outputChunk in enumerate(self.outputDataset.get_data_chunks(mode='w')):
            jobs.append(Job(
                inputChunks=[],
                outputChunk=outputChunk,
                jobIndex=jobIndex,
                jobCount=self.inputDatasets[0].chunks
            ))
        for inputDataset in self.inputDatasets:
            for jobIndex, inputChunk in enumerate(inputDataset.get_data_chunks(mode='r')):
                jobs[jobIndex].inputChunks.append(inputChunk)
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
        self.init()
        for inputData in zip(*inputChunks):
            outputChunk.append(self.run(*inputData))
        for inputChunk in inputChunks:
            inputChunk.close()
        outputChecksum = outputChunk.close()
        logging.info(f'{self.__class__.__name__} - {job.jobIndex:3}/{job.jobCount:3} - execute - END')
        return JobReport(outputChecksum=outputChecksum)

    def init(self):
        pass

    def run(self, *args, **kwargs):
        raise NotImplementedError('run() function must be implemented')
