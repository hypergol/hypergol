from hypergol.repr import Repr


class JobReport(Repr):
    """Class for passing information from the tasks to the pipeline
    """

    def __init__(self, jobId, exceptions, results=None):
        """

        Parameters
        ----------

        jobId: int
            Id of the job executed
        exceptions: bool
            Was there any exception during execute()
        results: dict
            Any information to be passed to the finish() function
        """
        self.jobId = jobId
        self.exceptions = exceptions
        self.results = results or {}
