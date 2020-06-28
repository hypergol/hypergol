import os
import glob
from pathlib import Path
from hypergol import Repr
from hypergol.name_string import NameString


class HypergolProject(Repr):

    def __init__(self, projectDirectory):
        self.projectDirectory = projectDirectory
        dataModelFiles = glob.glob(str(Path(projectDirectory, 'data_models', '*.py')))
        self._dataModelClasses = [NameString(os.path.split(filePath)[1][:-3]) for filePath in dataModelFiles]
        taskFiles = glob.glob(str(Path(projectDirectory, 'tasks', '*.py')))
        self._taskClasses = [NameString(os.path.split(filePath)[1][:-3]) for filePath in taskFiles]

    def is_data_model_class(self, value: NameString):
        return value in self._dataModelClasses

    def is_task_class(self, value: NameString):
        return value in self._taskClasses

    def is_project_class(self, value: NameString):
        return value in self._dataModelClasses or value in self._taskClasses
