from multiprocessing import Pool
from hypergol.source import Source
from hypergol.simple_task import SimpleTask
from hypergol.task import Task


class Pipeline:

    def __init__(self, tasks):
        self.tasks = tasks

    def run(self, threads=1):
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
                raise ValueError('task must be of type Task, SimpleTask or Source')
