import os
import stat
import glob
from pathlib import Path
import jinja2
import hypergol
from hypergol.utils import Mode
from hypergol.name_string import NameString
from hypergol.utils import create_text_file
from hypergol.utils import create_directory


def locate(fname):
    return Path(hypergol.__path__[0], 'cli', 'templates', fname)


class HypergolProject:

    def __init__(self, projectDirectory, projectName=None, dryrun=None, force=None):
        self.projectName = projectName
        self.projectDirectory = projectDirectory
        self.dataModelsPath = Path(projectDirectory, 'data_models')
        self.tasksPath = Path(projectDirectory, 'tasks')
        self.pipelinesPath = Path(projectDirectory, 'pipelines')
        self.testsPath = Path(projectDirectory, 'tests')
        self._dataModelClasses = []
        self._taskClasses = []
        if os.path.exists(self.dataModelsPath):
            dataModelFiles = glob.glob(str(Path(self.dataModelsPath, '*.py')))
            self._dataModelClasses = [NameString(os.path.split(filePath)[1][:-3]) for filePath in dataModelFiles]
        if os.path.exists(self.tasksPath):
            taskFiles = glob.glob(str(Path(projectDirectory, 'tasks', '*.py')))
            self._taskClasses = [NameString(os.path.split(filePath)[1][:-3]) for filePath in taskFiles]
        self.templateEnvironment = jinja2.Environment(
            loader=jinja2.FileSystemLoader(
                searchpath=Path(hypergol.__path__[0], 'cli', 'templates')
            )
        )
        if force and dryrun:
            raise ValueError('Both force and dryrun are set')
        self.mode = Mode.DRY_RUN if dryrun else Mode.FORCE if force else Mode.NORMAL

    @property
    def isDryRun(self):
        return self.mode == Mode.DRY_RUN

    @property
    def modeMessage(self):
        if self.mode == Mode.NORMAL:
            return ''
        return f' - Mode: {self.mode}'

    def create_project_directory(self):
        create_directory(self.projectDirectory, self.mode)

    def create_data_models_directory(self):
        create_directory(self.dataModelsPath, self.mode)
        self.render_simple(templateName='__init__.py.j2', filePath=Path(self.dataModelsPath, '__init__.py'))

    def create_tasks_directory(self):
        create_directory(self.tasksPath, self.mode)
        self.render_simple(templateName='__init__.py.j2', filePath=Path(self.tasksPath, '__init__.py'))

    def create_pipelines_directory(self):
        create_directory(self.pipelinesPath, self.mode)
        self.render_simple(templateName='__init__.py.j2', filePath=Path(self.pipelinesPath, '__init__.py'))

    def create_tests_directory(self):
        create_directory(self.testsPath, self.mode)
        # Test directory should not have __init__.py

    def is_data_model_class(self, value: NameString):
        return value in self._dataModelClasses

    def is_task_class(self, value: NameString):
        return value in self._taskClasses

    def check_dependencies(self, dependencies):
        for dependency in dependencies:
            if dependency not in self._dataModelClasses + self._taskClasses:
                raise ValueError(f'Unknown dependency {dependency}')

    def create_text_file(self, filePath, content):
        create_text_file(filePath=filePath, content=content, mode=self.mode)

    def render(self, templateName, templateData, filePath):
        # TODO(Laszlo): jinja seems to be stripping ending newlines
        content = self.templateEnvironment.get_template(templateName).render(templateData)
        if len(content) > 0 and content[-1] != '\n':
            content += '\n'
        self.create_text_file(filePath=filePath, content=content)
        return content

    def make_file_executable(self, filePath):
        print(f'Making file {filePath} executable.{self.modeMessage}')
        self._test_existence(filePath, 'File')
        if self.mode != Mode.DRY_RUN:
            fileStat = os.stat(filePath)
            if os.getuid() == fileStat.st_uid:
                os.chmod(filePath, fileStat.st_mode | stat.S_IXUSR)

    def _test_existence(self, path, objectName):
        if not os.path.exists(path):
            if self.mode == Mode.DRY_RUN:
                print(f'{objectName} {path} does not exist.{self.modeMessage}')
            else:
                raise ValueError(f'{objectName} {path} does not exist.{self.modeMessage}')

    def render_executable(self, templateName, templateData, filePath):
        content = self.render(templateName, templateData, filePath)
        self.make_file_executable(filePath=filePath)
        return content

    def render_simple(self, templateName, filePath):
        return self.render(templateName=templateName, templateData={'name': self.projectName}, filePath=filePath)
