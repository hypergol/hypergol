import logging

from typing import List
from hypergol.delayed import Delayed
from hypergol.dataset import Dataset
from hypergol.utils import Repr


class Job(Repr):

    def __init__(self, inputChunks, outputChunk):
        self.inputChunks = inputChunks
        self.outputChunk = outputChunk


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
        inputChunkIterator = zip(*[inputDataset.get_chunks(mode='r') for inputDataset in self.inputDatasets])
        return [
            Job(inputChunks=inputChunks, outputChunk=outputChunk)
            for inputChunks, outputChunk
            in zip(inputChunkIterator, self.outputDataset.get_chunks(mode='w'))
        ]

    def execute(self, job):
        if not isinstance(job, Job):
            raise ValueError(f'{self.__class__.__name__}.execute() argument must be of type Job')
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
        logging.info(f'{self.__class__.__name__} - execute - START')
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
        logging.info(f'{self.__class__.__name__} - execute - END')
        return JobReport(outputChecksum=outputChecksum)

    def init(self):
        pass

    def run(self, *args, **kwargs):
        raise NotImplementedError('run() function must be implemented')
