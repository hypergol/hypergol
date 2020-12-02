import os
from pathlib import Path

from hypergol.cli.create_task import create_task
from hypergol.hypergol_project import HypergolProject

from tests.hypergol_test_case import TestRepoManager
from tests.cli.hypergol_create_test_case import HypergolCreateTestCase

TEST_SOURCE = """
from hypergol import Job
from hypergol import Task


class TestSource(Task):

    def __init__(self, exampleParameter, *args, **kwargs):
        super(TestSource, self).__init__(*args, **kwargs)
        # TODO: all member variables must be pickle-able, otherwise use the "Delayed" methodology
        # TODO: (e.g. for a DB connection), see the documentation <add link here>
        self.exampleParameter = exampleParameter

    def init(self):
        # TODO: initialise members that are NOT "Delayed" here (e.g. load spacy model)
        pass

    def get_jobs(self):
        raise NotImplementedError(f'{self.__class__.__name__} must implement get_jobs()')
        # TODO: Return a list of Job classes here that will be passed on to the source_iterator
        return [Job(id_=k, total= ..., parameters={...}) for k, ... in enumerate(...)]

    def source_iterator(self, parameters):
        raise NotImplementedError(f'{self.__class__.__name__} must implement source_iterator()')
        # TODO: use the parameters (from Job) to open
        # TODO: use yield in this function instead of return while you are consuming your source data
        # TODO: return type must be list or tuple as the * operator will be used on it
        yield (exampleData, )

    def run(self, exampleData):
        raise NotImplementedError(f'{self.__class__.__name__} must implement run()')
        # TODO: Use the exampleData from source_iterator to construct a domain object
        self.output.append(exampleOutputObject)
""".lstrip()

TEST_TASK = """
from hypergol import Task


class TestTask(Task):

    def __init__(self, exampleParameter, *args, **kwargs):
        super(TestTask, self).__init__(*args, **kwargs)
        # TODO: all member variables must be pickle-able, otherwise use the "Delayed" methodology
        # TODO: (e.g. for a DB connection), see the documentation <add link here>
        self.exampleParameter = exampleParameter

    def init(self):
        # TODO: initialise members that are NOT "Delayed" here (e.g. load spacy model)
        pass

    def run(self, exampleInputObject1, exampleInputObject2):
        raise NotImplementedError(f'{self.__class__.__name__} must implement run()')
        self.output.append(exampleOutputObject)
""".lstrip()


class TestCreateTask(HypergolCreateTestCase):

    def __init__(self, methodName):
        super(TestCreateTask, self).__init__(projectName='TestProject', methodName=methodName)
        self.allPaths = [
            Path(self.projectDirectory, 'tasks', 'test_task.py'),
            Path(self.projectDirectory, 'tasks'),
            Path(self.projectDirectory)
        ]
        self.project = None
        self.maxDiff = 10000

    def setUp(self):
        super().setUp()
        self.project = HypergolProject(
            projectDirectory=self.projectDirectory,
            repoManager=TestRepoManager(raiseIfDirty=False)
        )
        self.project.create_project_directory()
        self.project.create_tasks_directory()

    def test_create_task_creates_files(self):
        create_task(className='TestTask', projectDirectory=self.projectDirectory)
        for filePath in self.allPaths:
            self.assertEqual(os.path.exists(filePath), True)

    def test_create_task_creates_content(self):
        content = create_task(className='TestTask', projectDirectory=self.projectDirectory, dryrun=True)
        self.assertEqual(content[0], TEST_TASK)

    def test_create_task_creates_content_source(self):
        content = create_task(className='TestSource', source=True, projectDirectory=self.projectDirectory, dryrun=True)
        self.assertEqual(content[0], TEST_SOURCE)
