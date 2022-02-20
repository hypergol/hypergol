import os
import hypergol

from pathlib import Path

from hypergol.utils import HypergolFileAlreadyExistsException
from hypergol.cli.create_project import create_project

from tests.cli.hypergol_create_test_case import HypergolCreateTestCase
from tests.cli.hypergol_create_test_case import delete_if_exists


MAKE_VENV_SCRIPT = """
python3 -m venv .venv
source .venv/bin/activate
pip3 install --upgrade pip
pip3 install setuptools==57.1.0
pip3 install wheel
pip3 install -r requirements.txt
""".lstrip()

RUN_TEST_SCRIPT = """
export PYTHONPATH="${PWD}/..:${PWD}/../..:"
nose2 -s tests/
""".lstrip()

RUN_PYLINT_SCRIPT = """
pylint --rcfile=pylintrc data_models pipelines tasks
""".lstrip()

REQUIREMENTS_CONTENT = """
fire==0.3.1
nose2==0.9.2
pylint==2.5.3
hypergol==VERSION
tensorflow==2.5.3
torch==1.10.2
pydantic==1.6.2
fastapi==0.65.2
uvicorn==0.11.8
""".replace('VERSION', hypergol.__version__).lstrip()

GITIGNORE_CONTENT = """
.venv/
.vscode/
.idea/
__pycache__
__pycache__/*
""".lstrip()

README_CONTENT = """
""".lstrip()

PYLINTRC_CONTENT = """
""".lstrip()


class TestCreateProject(HypergolCreateTestCase):

    def __init__(self, methodName):
        super(TestCreateProject, self).__init__(projectName='TestProject', methodName=methodName)
        self.allPaths = [
            Path(self.projectDirectory, 'tests'),
            Path(self.projectDirectory, 'data_models', '__init__.py'),
            Path(self.projectDirectory, 'data_models'),
            Path(self.projectDirectory, 'tasks', '__init__.py'),
            Path(self.projectDirectory, 'tasks'),
            Path(self.projectDirectory, 'models', 'blocks', '__init__.py'),
            Path(self.projectDirectory, 'models', 'blocks'),
            Path(self.projectDirectory, 'models', '__init__.py'),
            Path(self.projectDirectory, 'models'),
            Path(self.projectDirectory, 'pipelines', '__init__.py'),
            Path(self.projectDirectory, 'pipelines'),
            Path(self.projectDirectory, 'README.md'),
            Path(self.projectDirectory, 'LICENSE'),
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

    def test_create_project_creates_content(self):
        allContent = create_project(self.projectName, dryrun=True)
        makeVenvScript, runTestScript, runPylintScript, requirementsContent, gitignoreContent, readmeContent, licenseContent, pylintrcContent = allContent
        self.assertEqual(makeVenvScript, MAKE_VENV_SCRIPT)
        self.assertEqual(runTestScript, RUN_TEST_SCRIPT)
        self.assertEqual(runPylintScript, RUN_PYLINT_SCRIPT)
        self.assertEqual(requirementsContent, REQUIREMENTS_CONTENT)
        self.assertEqual(gitignoreContent, GITIGNORE_CONTENT)
        self.assertEqual(len(readmeContent), 5744)
        self.assertEqual(len(licenseContent), 1070)
        self.assertEqual(len(pylintrcContent), 18741)
