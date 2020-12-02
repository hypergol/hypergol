from hypergol.repr import Repr


class JobReport(Repr):
    """Class for passing information from the tasks to the pipeline
    """

    def __init__(self, jobId, success):
        """

        Parameters
        ----------

        jobId: int
            Id of the job executed
        success: bool
            Outcome of the job
        """
        self.jobId = jobId
        self.success = success
