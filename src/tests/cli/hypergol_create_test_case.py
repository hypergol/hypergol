import os
import glob
from pathlib import Path
from unittest import TestCase

from hypergol.name_string import NameString


def delete_if_exists(filePath):
    if os.path.exists(filePath):
        if os.path.isdir(filePath):
            os.rmdir(filePath)
        else:
            os.remove(filePath)


class HypergolCreateTestCase(TestCase):

    def __init__(self, projectName, methodName):
        super(HypergolCreateTestCase, self).__init__(methodName=methodName)
        self.projectName = projectName
        self.projectDirectory = NameString(self.projectName).asSnake
        self.allPaths = []

    def clean_up(self):
        for filePath in self.allPaths:
            try:
                delete_if_exists(filePath)
            except OSError:
                for unexpectedFilePath in glob.glob(str(Path(filePath, '*'))):
                    print(f'deleting unexpected files {unexpectedFilePath}')
                    delete_if_exists(unexpectedFilePath)
                delete_if_exists(filePath)

    def setUp(self):
        super().setUp()
        self.clean_up()

    def tearDown(self):
        super().tearDown()
        self.clean_up()
