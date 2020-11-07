from multiprocessing import Pool

from hypergol.source import Source
from hypergol.simple_task import SimpleTask
from hypergol.task import Task


class Pipeline:
    """A simple pipeline that enables multithreaded execution of tasks"""

    def __init__(self, tasks):
        """
        Parameters
        ----------
        tasks: List[BaseTask or Source]
            List of tasks to be executed in the given order
        """
        self.tasks = tasks

    def run(self, threads=1):
        """Runs each task
        Opens a set of threads, creates the list of job and calls the task's ``execute()`` function. Upon finishing it calls ``finalise`` to create the ``.chk`` file of the output dataset.

        Parameters
        ----------
        threads : int = 1
            Number of threads to run
        """
        for task in self.tasks:
            if isinstance(task, Source):
                task.execute()
            elif isinstance(task, (SimpleTask, Task)):
                pool = Pool(task.threads or threads)
                jobReports = pool.map(task.execute, task.get_jobs())
                task.finalise(jobReports=jobReports, threads=task.threads or threads)
                pool.close()
                pool.join()
                pool.terminate()
            else:
                raise ValueError('Task must be of type Task, SimpleTask or Source')
