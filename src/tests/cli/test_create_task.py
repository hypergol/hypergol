import os
from pathlib import Path

from hypergol.cli.create_task import create_task
from hypergol.hypergol_project import HypergolProject
from tests.cli.hypergol_create_test_case import HypergolCreateTestCase

TEST_SOURCE = """
from hypergol import Source


class TestSource(Source):

    def __init__(self, exampleParameter, *args, **kwargs):
        super(TestSource, self).__init__(*args, **kwargs)
        # TODO: Source tasks are single threaded, no need for members to be pickle-able
        self.exampleParameter = exampleParameter

    def source_iterator(self):
        raise NotImplementedError(f'{self.__class__.__name__} must implement source_iterator()')
        # TODO: use yield in this function instead of return while your are consuming your source data
        yield exampleData

    def run(self, data):
        raise NotImplementedError(f'{self.__class__.__name__} must implement run()')
        return exampleOutputObject
""".lstrip()

TEST_TASK = """
from hypergol import SimpleTask


class TestTask(SimpleTask):

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
        return exampleOutputObject
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

    def setUp(self):
        super().setUp()
        self.project = HypergolProject(projectDirectory=self.projectDirectory)
        self.project.create_project_directory()
        self.project.create_tasks_directory()

    def test_create_task_creates_files(self):
        create_task(className='TestTask', projectDirectory=self.projectDirectory, simple=True)
        for filePath in self.allPaths:
            self.assertEqual(os.path.exists(filePath), True)

    def test_create_task_creates_content(self):
        content = create_task(className='TestTask', projectDirectory=self.projectDirectory, simple=True, dryrun=True)
        self.assertEqual(content[0], TEST_TASK)

    def test_create_task_creates_content_source(self):
        content = create_task(className='TestSource', source=True, simple=False, projectDirectory=self.projectDirectory, dryrun=True)
        self.assertEqual(content[0], TEST_SOURCE)
