import os
import re
import json
import stat
import glob
from pathlib import Path

import jinja2
from git import Repo
from git.exc import NoSuchPathError
from git.exc import InvalidGitRepositoryError

import hypergol
from hypergol import DatasetFactory
from hypergol import RepoData
from hypergol.utils import Mode
from hypergol.utils import create_text_file
from hypergol.utils import create_directory
from hypergol.name_string import NameString


DATASET_TEMPLATE = """sys.path.insert(0, '{projectDirectory}')
from data_models.{dataTypeFile} import {dataType}
from hypergol import Dataset
from hypergol import RepoData
ds=Dataset(
    dataType={dataType},
    location='{location}',
    project='{project}',
    branch='{branch}',
    name='{name}',
    chunkCount={chunkCount},
    repoData=RepoData(
        branchName='{branchName}',
        commitHash='{commitHash}',
        commitMessage='{commitMessage}',
        comitterName='{comitterName}',
        comitterEmail='{comitterEmail}'
    )
)"""


def locate(fname):
    return Path(hypergol.__path__[0], 'cli', 'templates', fname)


class RepoManager:
    """Wrapper class around git that provides all information about the repo connected to the project.

    """

    def __init__(self, repoDirectory=None, raiseIfDirty=True):
        """
        Parameters
        ----------
        repoDirectory : string
            directory where the the `.git` directory is located
        raiseIfDirty : bool
            if set and the repo contains uncommitted code, it raises an error
        """
        self.repoDirectory = repoDirectory
        self.raiseIfDirty = raiseIfDirty
        self.repoExists = False
        try:
            repo = Repo(path=self.repoDirectory)
            self.repoExists = True
        except NoSuchPathError:
            print(f'Directory {self.repoDirectory} does not exist')
            return
        except InvalidGitRepositoryError:
            print(f'No git repository in {self.repoDirectory}')
            return
        if repo.is_dirty():
            if self.raiseIfDirty:
                raise ValueError("The current git repo is dirty; please commit your work before you run the pipeline.")
            print('Warning! The current git repo is dirty; this will result in incorrect commit hash in datasets.')
        try:
            commit = repo.commit()
        except ValueError as ex:
            print('No commits in this repo; please create an initial commit.')
            raise ex
        self.commitHash = commit.hexsha
        self.commitMessage = commit.message
        self.comitterName = commit.committer.name
        self.comitterEmail = commit.committer.email
        try:
            self.branchName = repo.active_branch.name
        except TypeError:
            self.branchName = 'DETACHED'


class HypergolProject:
    """Owner of all information about the project

    CLI functions define what needs to be created, and this class creates them. It also consistently handles the mode flags (normal/dryrun/force)

    It also verifies if a requested class exists in the respective directory (data_models, tasks) and identifies its type, e.g.: for ``HelloWorld`` it checks if ``data_models/hello_world.py`` or ``tasks/hello_world.py`` exists and assumes its role from that. Used in :func:`.create_data_model` and :func:`.create_pipeline`

    """

    def __init__(self, projectDirectory=None, dataDirectory='.', chunkCount=16, dryrun=None, force=None, repoManager=None):
        """
        Parameters
        ----------
        projectDirectory : string
            location of the project: e.g.: ``~/repo_name``, models will be in ``~/repo_name/models``
        projectDirectory : string
            location of the data for the project project: e.g.: ``~/data``, files will be stored in ``~/data/repo_name``
        dryrun : bool (default=None)
            If set to ``True`` it returns the generated code as a string
        force : bool (default=None)
            If set to ``True`` it overwrites the target file
        """
        if force and dryrun:
            raise ValueError('Both force and dryrun are set')
        if projectDirectory is None:
            projectDirectory = os.getcwd()
        if projectDirectory.endswith('/'):
            projectDirectory = projectDirectory[:-1]
        if dataDirectory.endswith('/'):
            dataDirectory = dataDirectory[:-1]
        if repoManager is None:
            repoManager = RepoManager(repoDirectory=projectDirectory, raiseIfDirty=not force)
        self.repoManager = repoManager
        self.projectName = NameString(os.path.basename(projectDirectory))
        self.projectDirectory = projectDirectory
        self.dataDirectory = dataDirectory
        self.dataModelsPath = Path(projectDirectory, 'data_models')
        self.tasksPath = Path(projectDirectory, 'tasks')
        self.pipelinesPath = Path(projectDirectory, 'pipelines')
        self.modelsPath = Path(projectDirectory, 'models')
        self.blocksPath = Path(projectDirectory, 'models', 'blocks')
        self.testsPath = Path(projectDirectory, 'tests')
        self.notebooksPath = Path(projectDirectory, 'notebooks')
        self._init_known_class_lists()
        self.templateEnvironment = jinja2.Environment(
            loader=jinja2.FileSystemLoader(
                searchpath=Path(hypergol.__path__[0], 'cli', 'templates')
            )
        )
        self.mode = Mode.DRY_RUN if dryrun else Mode.FORCE if force else Mode.NORMAL

        if not self.repoManager.repoExists:
            self.datasetFactory = None
            self.tensorboardPath = None
            self.modelDataPath = None
            print('Repo does not exist, data related functionality disabled.')
            return

        self.datasetFactory = DatasetFactory(
            location=self.dataDirectory,
            project=self.projectName.asSnake,
            branch=self.repoManager.branchName,
            chunkCount=chunkCount,
            repoData=RepoData(
                branchName=self.repoManager.branchName,
                commitHash=self.repoManager.commitHash,
                commitMessage=self.repoManager.commitMessage,
                comitterName=self.repoManager.comitterName,
                comitterEmail=self.repoManager.comitterEmail
            )
        )
        self.tensorboardPath = Path(dataDirectory, self.projectName.asSnake, 'tensorboard', self.repoManager.branchName)
        self.modelDataPath = Path(dataDirectory, self.projectName.asSnake, self.repoManager.branchName, 'models')

    def _init_known_class_lists(self):
        self._dataModelClasses = []
        self._taskClasses = []
        self._modelBlockClasses = []
        if os.path.exists(self.dataModelsPath):
            dataModelFiles = glob.glob(str(Path(self.dataModelsPath, '[!_][!_]*.py')))
            self._dataModelClasses = [NameString(os.path.split(filePath)[1][:-3]) for filePath in dataModelFiles]
        if os.path.exists(self.tasksPath):
            taskFiles = glob.glob(str(Path(self.projectDirectory, 'tasks', '[!_][!_]*.py')))
            self._taskClasses = [NameString(os.path.split(filePath)[1][:-3]) for filePath in taskFiles]
        if os.path.exists(self.blocksPath):
            blockFiles = glob.glob(str(Path(self.projectDirectory, 'models', 'blocks', '[!_][!_]*.py')))
            self._modelBlockClasses = [NameString(os.path.split(filePath)[1][:-3]) for filePath in blockFiles]

    @property
    def isDryRun(self):
        return self.mode == Mode.DRY_RUN

    @property
    def modeMessage(self):
        if self.mode == Mode.NORMAL:
            return ''
        return f' - Mode: {self.mode}'

    def cli_final_message(self, creationType, name, content):
        creationPath = None
        if creationType == 'Model':
            creationPath = self.modelsPath
        elif creationType == 'Class':
            creationPath = self.dataModelsPath
        elif creationType == 'ModelBlock':
            creationPath = self.modelsPath
        elif creationType == 'PipeLine':
            creationPath = self.pipelinesPath
        elif creationType == 'Project':
            creationPath = self.projectDirectory
        elif str(creationType) in ['Source', 'Task']:
            creationPath = self.tasksPath
        if creationPath is None:
            raise ValueError(f'{creationType} is an unknown type')
        print('')
        print(f'{creationType} {name} was created in directory {creationPath}.{self.modeMessage}')
        print('')
        if self.isDryRun:
            return content
        return None

    def create_model_directory(self, modelName):
        create_directory(path=Path(self.modelsPath, modelName.asSnake), mode=self.mode)

    def create_project_directory(self):
        create_directory(path=self.projectDirectory, mode=self.mode)

    def create_data_models_directory(self):
        create_directory(path=self.dataModelsPath, mode=self.mode)

    def create_tasks_directory(self):
        create_directory(path=self.tasksPath, mode=self.mode)

    def create_pipelines_directory(self):
        create_directory(path=self.pipelinesPath, mode=self.mode)

    def create_blocks_directory(self):
        create_directory(path=self.blocksPath, mode=self.mode)

    def create_models_directory(self):
        create_directory(path=self.modelsPath, mode=self.mode)

    def create_tests_directory(self):
        create_directory(path=self.testsPath, mode=self.mode)

    def create_notebooks_directory(self):
        create_directory(path=self.notebooksPath, mode=self.mode)

    def is_data_model_class(self, value: NameString):
        """Checks if a name is a data_model class (based on if the snakecase .py file exists)"""
        return value in self._dataModelClasses

    def is_task_class(self, value: NameString):
        """Checks if a name is in tasks class (based on if the snakecase .py file exists)"""
        return value in self._taskClasses

    def is_model_block_class(self, value: NameString):
        """Checks if a name is in blocks class (based on if the snakecase .py file exists)"""
        return value in self._modelBlockClasses

    def check_dependencies(self, dependencies):
        """Raises an error if any dependency is unknown"""
        for dependency in dependencies:
            if dependency not in self._dataModelClasses + self._taskClasses + self._modelBlockClasses:
                raise ValueError(f'Unknown dependency {dependency}')

    def create_text_file(self, filePath, content):
        create_text_file(filePath=filePath, content=content, mode=self.mode)

    def render(self, templateName, templateData, filePath):
        """Creates a file from a template using jinja2

        Parameters
        ----------
        templateName : string
            filename of the template
        templateData : dict
            data to fill the template with
        filePath : Path
            full path of the destination file (ignored if self.mode != Mode.DRY_RUN)
        """
        content = self.templateEnvironment.get_template(templateName).render(templateData)
        if len(content) > 0 and content[-1] != '\n':
            content += '\n'
        self.create_text_file(filePath=filePath, content=content)
        return content

    def make_file_executable(self, filePath):
        print(f'Making file {filePath} executable.{self.modeMessage}')
        self._test_existence(path=filePath, objectName='File')
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
        content = self.render(templateName=templateName, templateData=templateData, filePath=filePath)
        self.make_file_executable(filePath=filePath)
        return content

    def render_simple(self, templateName, filePath):
        return self.render(templateName=templateName, templateData={'name': self.projectName}, filePath=filePath)

    def render_notebook(self, notebookName, filePath):
        templateNotebookPath = f"{Path(hypergol.__path__[0], 'cli', 'templates')}/{notebookName}"
        content = open(templateNotebookPath, 'rt').read()
        self.create_text_file(filePath=filePath, content=content)
        return content

    def list_datasets(self, pattern=None, asCode=False):
        """Convenience function to list datasets for a project

        Returns a list of data loaded from the ``.def`` files in the directory

        Parameters
        ----------
        pattern : string (None)
            Regex pattern to filter on dataset names, if unspecified, defaults to ``.*``
        asCode : bool (False)
            If True prints a code snippet that allows the dataset to be loaded (with imports and path updates)
        """
        if pattern is None:
            pattern = '.*'
        dataPath = Path(self.dataDirectory, self.projectName.asSnake)
        result = []
        for pathName, _, fileNames in os.walk(dataPath):
            for fileName in fileNames:
                if fileName.endswith('.def') and re.match(pattern, fileName[:-4]) is not None:
                    data = json.load(open(Path(pathName, fileName), 'rt'))
                    result.append(data)
                    if asCode:
                        values = {**data, **data['repo']}
                        values['location'] = self.dataDirectory
                        values['commitMessage'] = values['commitMessage'].replace('\n', '\\n')
                        values['dataTypeFile'] = NameString(name=values['dataType']).asSnake
                        values['projectDirectory'] = self.projectDirectory
                        print(DATASET_TEMPLATE.format(**values))
        return result

    def diff_data_model(self, commit, *args):
        """Convenience function to compare old data model class definitions to the current one

        Prints the diffs from the specified commit to the current commit

        Parameters
        ----------
        commit : string
            The git commit from where the comparison starts
        *args : List[string]
            List of class names to compare, if empty it compares all
        """
        if len(args) == 0:
            names = self._dataModelClasses
        else:
            names = [NameString(name) for name in args]
        repo = Repo(self.projectDirectory)
        if repo.is_dirty():
            print('Warning! Current git repo is dirty, this will result in incorrect diff')
        currentCommit = repo.commit().hexsha
        for name in names:
            print(f'------ data_models/{name.asSnake}.py ------')
            print(repo.git.diff(commit, currentCommit, f'data_models/{name.asSnake}.py'))

    def create_old_data_model(self, commit, *args):
        """Convenience function to generate data model classes at an old commit to be able to load datasets created then

        Full commit hash required.

        ``project.create_old_data_model(commit='fbd8110b7194425e2323f68ef54dac15bb01ee7b', 'OneClass', 'TwoClass')``

        Will create ``data_models/one_class_fbd8110.py`` and ``data_models/two_class_fbd8110.py`` and replaces all occurences of ``OneClass`` and ``TwoClass`` to ``OneClassFBD8110`` and ``TwoClassFBD8110`` in each file.

        Parameters
        ----------
        commit : string
            git commit to retrieve classes from
        args : List[string]
            List of class names to generate, if empty it generates all
        """
        if len(args) == 0:
            names = self._dataModelClasses
        else:
            names = [NameString(name) for name in args]
        result = []
        repo = Repo(self.projectDirectory)
        if repo.is_dirty():
            print('Warning! The current git repo is dirty; this will result in incorrect data_model_files created.')
        for name in names:
            content = repo.git.show(f'{commit}:data_models/{name.asSnake}.py')
            for oldName in names:
                content = content.replace(oldName.asClass, f'{oldName.asClass}{commit[:7].upper()}')
                content = content.replace(f'data_models.{oldName.asSnake}', f'data_models.{oldName.asSnake}_{commit[:7]}')
            if self.isDryRun:
                result.append(content)
                print(f'DRYRUN - Creating class {name.asClass}{commit[:7].upper()} in {name.asSnake}_{commit[:7]}.py')
                print(content+'\n')
            else:
                print(f'Creating class {name.asClass}{commit[:7].upper()} in {name.asSnake}_{commit[:7]}.py')
                with open(Path(self.dataModelsPath, f'{name.asSnake}_{commit[:7]}.py'), 'wt') as outFile:
                    outFile.write(content+'\n')
        self._init_known_class_lists()
        return result
