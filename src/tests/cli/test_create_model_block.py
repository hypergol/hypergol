import os
from pathlib import Path

from hypergol.cli.create_model_block import create_model_block
from hypergol.hypergol_project import HypergolProject

from tests.hypergol_test_case import TestRepoManager
from tests.cli.hypergol_create_test_case import HypergolCreateTestCase


TEST_MODEL_BLOCK = """
import tensorflow as tf
from tensorflow.keras import layers
from hypergol import BaseTensorflowModelBlock


class TestModelBlock(BaseTensorflowModelBlock):

    def __init__(self, exampleParameter1, exampleParameter2, **kwargs):
        super(TestModelBlock, self).__init__(**kwargs)
        self.exampleParameter1 = exampleParameter1
        self.exampleParameter2 = exampleParameter2
        # create tensorflow variables or keras.layers here

    def get_example(self, tensor1, tensor2):
        # do tensorflow calculations here using arguments and the member variables from the constructor
        pass
""".lstrip()


class TestCreateModelBlock(HypergolCreateTestCase):

    def __init__(self, methodName):
        super(TestCreateModelBlock, self).__init__(projectName='TestProject', methodName=methodName)
        self.allPaths = [
            Path(self.projectDirectory, 'models', 'test_model_block.py'),
            Path(self.projectDirectory, 'models'),
            Path(self.projectDirectory)
        ]
        self.project = None

    def setUp(self):
        super().setUp()
        self.project = HypergolProject(
            projectDirectory=self.projectDirectory,
            repoManager=TestRepoManager()
        )
        self.project.create_project_directory()
        self.project.create_models_directory()

    def test_create_model_block_creates_files(self):
        create_model_block(className='TestModelBlock', projectDirectory=self.projectDirectory)
        for filePath in self.allPaths:
            self.assertEqual(os.path.exists(filePath), True)

    def test_create_model_block_creates_content(self):
        content = create_model_block(className='TestModelBlock', projectDirectory=self.projectDirectory, dryrun=True)
        self.assertEqual(content[0], TEST_MODEL_BLOCK)
