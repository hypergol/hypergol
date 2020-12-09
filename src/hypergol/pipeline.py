from typing import List
from multiprocessing import Pool

from hypergol.logger import Logger
from hypergol.task import Task


class Pipeline:
    """A simple pipeline that enables multithreaded execution of tasks"""

    def __init__(self, tasks: List[Task], logger: Logger = None):
        """
        Parameters
        ----------
        tasks: List[Task]
            List of tasks to be executed in the given order

        logger: Logger
            logger class
        """
        self.tasks = tasks
        self.logger = logger or Logger()

    def run(self, threads=1):
        """Runs each task
        Opens a set of threads, creates the list of job and calls the task's ``execute()`` function. Upon finishing it calls ``finalise`` to create the ``.chk`` file of the output dataset.

        Parameters
        ----------
        threads : int = 1
            Number of threads to run
        """
        self.logger.log(f'{self.__class__.__name__} - Pipeline - START')
        for task in self.tasks:
            task.check_if_output_exists()
        for task in self.tasks:
            if not isinstance(task, Task):
                raise ValueError('Task must be of type Task')
            pool = Pool(task.threads or threads)
            jobReports = pool.map(task.execute, task.get_jobs())
            task.finalise(jobReports=jobReports, threads=task.threads or threads)
            pool.close()
            pool.join()
            pool.terminate()
        self.logger.log(f'{self.__class__.__name__} - Pipeline - END')
