from hypergol.repr import Repr


class JobReport(Repr):
    """Class for passing information from the tasks to the pipeline
    """

    def __init__(self, jobId, success, results=None):
        """

        Parameters
        ----------

        jobId: int
            Id of the job executed
        success: bool
            Outcome of the job
        results: dict
            Any information to be passed to the finish() function
        """
        self.jobId = jobId
        self.success = success
        self.results = results or {}
