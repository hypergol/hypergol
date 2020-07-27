import os
from pathlib import Path
from hypergol.utils import HypergolFileAlreadyExistsException
from hypergol.cli.create_project import create_project
from tests.cli.hypergol_create_test_case import HypergolCreateTestCase
from tests.cli.hypergol_create_test_case import delete_if_exists


class TestCreateProject(HypergolCreateTestCase):

    def __init__(self, methodName):
        super(TestCreateProject, self).__init__(projectName='TestProject', methodName=methodName)
        self.allPaths = [
            Path(self.projectDirectory, 'tests'),
            Path(self.projectDirectory, 'data_models', '__init__.py'),
            Path(self.projectDirectory, 'data_models'),
            Path(self.projectDirectory, 'tasks', '__init__.py'),
            Path(self.projectDirectory, 'tasks'),
            Path(self.projectDirectory, 'pipelines', '__init__.py'),
            Path(self.projectDirectory, 'pipelines'),
            Path(self.projectDirectory, 'tensorflow_models', 'blocks', '__init__.py'),
            Path(self.projectDirectory, 'tensorflow_models', 'blocks'),
            Path(self.projectDirectory, 'tensorflow_models', '__init__.py'),
            Path(self.projectDirectory, 'tensorflow_models'),
            Path(self.projectDirectory, 'README.md'),
            Path(self.projectDirectory, 'make_venv.sh'),
            Path(self.projectDirectory, 'run_tests.sh'),
            Path(self.projectDirectory, 'run_pylint.sh'),
            Path(self.projectDirectory, 'requirements.txt'),
            Path(self.projectDirectory, '.gitignore'),
            Path(self.projectDirectory, 'pylintrc'),
            Path(self.projectDirectory)
        ]

    def test_create_project_only_creates_files_expected(self):
        create_project(self.projectName)
        for filePath in self.allPaths:
            self.assertEqual(os.path.exists(filePath), True)
        for filePath in self.allPaths:
            delete_if_exists(filePath)

    def test_create_project_throws_error_if_already_exists(self):
        create_project(self.projectName)
        with self.assertRaises(HypergolFileAlreadyExistsException):
            create_project(self.projectName)

    def test_create_project_dry_run_mode_does_not_create(self):
        create_project(self.projectName, dryrun=True)
        for filePath in self.allPaths:
            self.assertEqual(os.path.exists(filePath), False)

    def test_create_project_dry_run_does_not_throw_error_if_already_exists(self):
        create_project(self.projectName)
        create_project(self.projectName, dryrun=True)

    def test_create_project_force_does_not_throw_error_if_already_exists(self):
        create_project(self.projectName)
        create_project(self.projectName, force=True)
        for filePath in self.allPaths:
            self.assertEqual(os.path.exists(filePath), True)
