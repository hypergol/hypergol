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
        self.exceptions = {}
        self.tasks = tasks
        self.logger = logger or Logger()

    def log(self, message):
        self.logger.log(f'{self.__class__.__name__} - {message}')

    def run(self, threads=1, onlyTasks=None):
        """Runs each task
        Opens a set of threads, creates the list of job and calls the task's ``execute()`` function. Upon finishing it calls ``finalise`` to create the ``.chk`` file of the output dataset.

        Parameters
        ----------
        threads : int = 1
            Number of threads to run
        onlyTasks : list = None
            list of task numbers in the task list to run (for debugging purpose). Add --onlyTasks=0 or --onlyTasks=1,2 parameter to the shell script in the CLI
        """
        self.log('START')
        if onlyTasks is not None:
            if isinstance(onlyTasks, int):
                onlyTasks = [onlyTasks]
            tasksToRun = [self.tasks[k] for k in onlyTasks]
        else:
            tasksToRun = self.tasks
        for task in tasksToRun:
            task.check_if_output_exists()
        for task in tasksToRun:
            if not isinstance(task, Task):
                raise ValueError('Task must be of type Task')
            pool = Pool(task.threads or threads)
            jobReports = pool.map(task.execute, task.get_jobs())
            self.exceptions[task.__class__.__name__] = any(jobReport.exceptions for jobReport in jobReports)
            task.finalise(jobReports=jobReports, threads=task.threads or threads)
            pool.close()
            pool.join()
            pool.terminate()
        for taskName, exceptions in self.exceptions.items():
            self.log(f'{taskName}: exceptions: {exceptions}')
        self.log('END')
