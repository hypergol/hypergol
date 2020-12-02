from typing import List
from typing import Dict

from hypergol.repr import Repr
from hypergol.datachunk import DataChunk


class Job(Repr):
    """Class for passing information on chunks to tasks"""

    def __init__(self, id_, total, parameters: Dict = None, inputChunks: List[DataChunk] = None, loadedInputChunks: List[DataChunk] = None):
        """
        Parameters
        ----------
        id_: int
            what's the order of this job in the queue
        number: int
            number of total jobs in this task
        parameters: object
            any information to be passed to the source_iterator()
        inputChunks: List[DataChunk]
            these chunks will be iterated over while run() function is called
        loadedInputChunks: List[DataChunk]
            these chunks will be fully loaded before any run() function called
        """
        self.id = id_
        self.total = total
        self.parameters = parameters or {}
        self.inputChunks = inputChunks or []
        self.loadedInputChunks = loadedInputChunks or []
