import os
import glob
from pathlib import Path
from unittest import TestCase
from hypergol.utils import Mode
from hypergol.utils import HypergolFileAlreadyExistsException
from hypergol.cli.create_project import create_project


def delete_if_exists(filePath):
    if os.path.exists(filePath):
        if os.path.isdir(filePath):
            os.rmdir(filePath)
        else:
            os.remove(filePath)


class TestCreateProject(TestCase):

    def __init__(self, methodName):
        super(TestCreateProject, self).__init__(methodName=methodName)
        self.projectName = 'TestProject'
        self.projectDirectory = 'test_project'
        self.dataModelsDirectory = Path(self.projectDirectory, 'data_models')
        self.tasksDirectory = Path(self.projectDirectory, 'tasks')
        self.pipelinesDirectory = Path(self.projectDirectory, 'pipelines')
        self.makeVenvFilePath = Path(self.projectDirectory, 'make_venv.sh')
        self.requirementsFilePath = Path(self.projectDirectory, 'requirements.txt')
        self.gitignorePath = Path(self.projectDirectory, '.gitignore')
        self.allPaths = [
            self.dataModelsDirectory,
            self.tasksDirectory,
            self.pipelinesDirectory,
            self.makeVenvFilePath,
            self.requirementsFilePath,
            self.gitignorePath,
            self.projectDirectory
        ]

    def clean_up(self):
        for filePath in self.allPaths:
            try:
                delete_if_exists(filePath)
            except OSError:
                for unexpectedFilePath in glob.glob(str(Path(filePath, '*'))):
                    print(f'deleting unexpected filed {unexpectedFilePath}')
                    delete_if_exists(unexpectedFilePath)
                delete_if_exists(filePath)

    def setUp(self):
        super().setUp()
        self.clean_up()

    def tearDown(self):
        super().tearDown()
        self.clean_up()

    def test_create_project_creates(self):
        create_project(self.projectName, mode=Mode.NORMAL)
        for filePath in self.allPaths:
            self.assertEqual(os.path.exists(filePath), True)

    def test_create_project_throws_error_if_already_exists(self):
        create_project(self.projectName, mode=Mode.NORMAL)
        with self.assertRaises(HypergolFileAlreadyExistsException):
            create_project(self.projectName, mode=Mode.NORMAL)

    def test_create_project_dry_run_mode_does_not_create(self):
        create_project(self.projectName, mode=Mode.DRY_RUN)
        for filePath in self.allPaths:
            self.assertEqual(os.path.exists(filePath), False)

    def test_create_project_dry_run_does_not_throw_error_if_already_exists(self):
        create_project(self.projectName, mode=Mode.NORMAL)
        create_project(self.projectName, mode=Mode.DRY_RUN)

    def test_create_project_force_does_not_throw_error_if_already_exists(self):
        create_project(self.projectName, mode=Mode.NORMAL)
        create_project(self.projectName, mode=Mode.FORCE)
        for filePath in self.allPaths:
            self.assertEqual(os.path.exists(filePath), True)
