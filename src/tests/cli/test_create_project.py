import os
from pathlib import Path
from hypergol.utils import Mode
from hypergol.utils import HypergolFileAlreadyExistsException
from hypergol.cli.create_project import create_project
from tests.cli.hypergol_create_test_case import HypergolCreateTestCase


class TestCreateProject(HypergolCreateTestCase):

    def __init__(self, methodName):
        super(TestCreateProject, self).__init__(projectName='TestProject', methodName=methodName)
        self.allPaths = [
            Path(self.projectDirectory, 'data_models'),
            Path(self.projectDirectory, 'tasks'),
            Path(self.projectDirectory, 'pipelines'),
            Path(self.projectDirectory, 'make_venv.sh'),
            Path(self.projectDirectory, 'requirements.txt'),
            Path(self.projectDirectory, '.gitignore'),
            Path(self.projectDirectory)
        ]

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
