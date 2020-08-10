import os
from pathlib import Path
import mock

from hypergol.cli.create_model import create_model
from hypergol.hypergol_project import HypergolProject
from tests.cli.hypergol_create_test_case import HypergolCreateTestCase


TEST_CONTENT = """
import tensorflow as tf
from hypergol import BaseTensorflowModel


class TestModel(BaseTensorflowModel):

    def __init__(self, block1, block2, **kwargs):
        super(TestModel, self).__init__(**kwargs)
        self.block1 = block1
        self.block2 = block2

    def get_loss(self, targets, training, exampleInput1, exampleInput2):
        raise NotImplementedError('BaseTensorflowModel must implement get_loss()')
        # calculate loss here and return it
        # input arguments must be the same in all three functions
        # and match with the keys of the return value of DataProcessor.process_input_batch()

    @tf.function(input_signature=[
        tf.TensorSpec(shape=[None, None], dtype=tf.int32, name='exampleInput1'),
        tf.TensorSpec(shape=[None, None], dtype=tf.string, name='exampleInput2')
    ])
    def get_outputs(self, exampleInput1, exampleInput2):
        raise NotImplementedError('BaseTensorflowModel must implement get_outputs()')
        # calculate the output here and return it, update the decorator accordingly

    def produce_metrics(self, targets, training, globalStep, exampleInput1, exampleInput2s):
        # use tf.summary to record statistics in training/evaluation cycles like
        # tf.summary.scalar(name='exampleName', data=value, step=globalStep)
        pass
""".lstrip()

TEST_DATA_PROCESSOR = """
import tensorflow as tf
from hypergol import BaseBatchProcessor
from data_models.test_output import TestOutput


class TestModelDataProcessor(BaseBatchProcessor):

    def __init__(self, inputDataset, inputBatchSize, outputDataset, exampleArgument):
        super(TestModelDataProcessor, self).__init__(inputDataset, inputBatchSize, outputDataset)
        self.exampleArgument = exampleArgument

    def process_input_batch(self, batch):
        raise NotImplementedError('BaseBatchProcessor must implement process_input_batch()')
        # batch is a list of datamodel objects cycle through them and build the data
        # that can be converted to tensorflow constants, e.g.:
        # exampleInput1 = []
        # exampleInput2 = []
        # exampleOutput = []
        # for exampleValue in batch:
        #      exampleInput1.append(exampleValue.exampleList)
        #      exampleInput2.append(len(exampleValue.exampleList))
        #      exampleOutput.append(exampleValue.exampleOutputList)
        # inputs = {
        #     'exampleInput1': tf.ragged.constant(lemmas, dtype=tf.string).to_tensor()[:, 10]
        #     'exampleInput2': tf.constant(sentenceLengths, dtype=tf.int32)
        # }
        # targets = tf.ragged.constant(, dtype=tf.string).to_tensor()[:, :10]
        return inputs, targets

    def process_output_batch(self, inputs, targets, outputs):
        raise NotImplementedError('BaseBatchProcessor must implement process_output_batch()')
        # create a list of data model classes from the argument, output classes must have an id because they will be saved into a dataset
        # outputBatch = []
        # for id_, i, t, o in zip(inputs['ids'], inputs, targets, outputs):
        #     outputBatch.append(ExampleOutput(eoid=id_, i=i, t=t, o=o)
        # return  outputBatch
""".lstrip()

TEST_TRAIN_MODEL = """
import fire
from git import Repo
import tensorflow as tf
from hypergol import DatasetFactory
from hypergol import RepoData
from hypergol import TensorflowModelManager
from models.test_model_data_processor import TestModelDataProcessor
from models.test_model import TestModel
from models.test_block1 import TestBlock1
from models.test_block2 import TestBlock2
from data_models.test_input import TestInput
from data_models.test_output import TestOutput


LOCATION = '.'
PROJECT = 'example_project'
BRANCH = 'example_branch'


def train_test_model(force=False):
    repo = Repo(path='.')
    if repo.is_dirty():
        if force:
            print('Warning! Current git repo is dirty, this will result in incorrect commit hash in datasets')
        else:
            raise ValueError("Current git repo is dirty, please commit your work befour you run the pipeline")

    commit = repo.commit()
    repoData = RepoData(
        branchName=repo.active_branch.name,
        commitHash=commit.hexsha,
        commitMessage=commit.message,
        comitterName=commit.committer.name,
        comitterEmail=commit.committer.email
    )

    datasetFactory = DatasetFactory(
        location=LOCATION,
        project=PROJECT,
        branch=BRANCH,
        chunkCount=16,
        repoData=repoData
    )

    batchProcessor = TestModelDataProcessor(
        inputDataset=datasetFactory.get(dataType=TestInput, name='inputs'),
        inputBatchSize=16,
        outputDataset=datasetFactory.get(dataType=TestOutput, name='outputs'),
        exampleArgument=''
    )
    testModel = TestModel(
        testBlock1=TestBlock1(
            blockArgument1='',
            blockArgument2='',
        ),
        testBlock2=TestBlock2(
            blockArgument1='',
            blockArgument2='',
        ),
    )
    modelManager = TensorflowModelManager(
        model=testModel,
        optimizer=tf.keras.optimizers.Adam(lr=1),
        batchProcessor=batchProcessor,
        location=LOCATION,
        project=PROJECT,
        branch=BRANCH,
        name='TestModel',
        restoreWeightsPath=None
    )
    modelManager.run(
        stepCount=100,
        evaluationSteps=list(range(0, 100, 10)),
        tracingSteps=list(range(0, 100, 5))
    )


if __name__ == '__main__':
    tf.get_logger().setLevel('ERROR')
    fire.Fire(train_test_model)
""".lstrip()

TEST_SCRIPT = """
export PYTHONPATH="${PWD}/..:${PWD}/../..:"

python3 \\
    ./models/train_test_model.py \\
    $1
""".lstrip()


class TestCreateModel(HypergolCreateTestCase):

    def __init__(self, methodName):
        super(TestCreateModel, self).__init__(projectName='TestProject', methodName=methodName)
        self.allPaths = [
            Path(self.projectDirectory, 'models', 'test_model.py'),
            Path(self.projectDirectory, 'models', 'test_model_data_processor.py'),
            Path(self.projectDirectory, 'models', 'train_test_model.py'),
            Path(self.projectDirectory, 'models'),
            Path(self.projectDirectory, 'train_test_model.sh'),
            Path(self.projectDirectory)
        ]
        self.project = None

    def setUp(self):
        super().setUp()
        self.project = HypergolProject(projectDirectory=self.projectDirectory)
        self.project.create_project_directory()
        self.project.create_models_directory()

    @mock.patch('hypergol.cli.create_pipeline.HypergolProject.check_dependencies')
    def test_create_model_creates_files(self, check_dependencies):
        create_model(modelName='TestModel', inputClass='TestInput', outputClass='TestOutput', projectDirectory=self.projectDirectory)
        for filePath in self.allPaths:
            self.assertEqual(os.path.exists(filePath), True)

    @mock.patch('hypergol.cli.create_pipeline.HypergolProject.check_dependencies')
    @mock.patch('hypergol.cli.create_pipeline.HypergolProject.is_model_block_class', side_effect=lambda x: x.asClass in ['TestBlock1', 'TestBlock2'])
    def test_create_model_creates_content(self, mock_is_model_block_class, check_dependencies):
        content, dataProcessorContent, trainModelContent, scriptContent = create_model(
            'TestModel', 'TestInput', 'TestOutput', 'TestBlock1', 'TestBlock2', projectDirectory=self.projectDirectory, dryrun=True)
        self.assertEqual(content, TEST_CONTENT)
        self.assertEqual(dataProcessorContent, TEST_DATA_PROCESSOR)
        self.assertEqual(trainModelContent, TEST_TRAIN_MODEL)
        self.assertEqual(scriptContent, TEST_SCRIPT)

    # def test_create_model_block_creates_content(self):
    #     content = create_model_block(className='TestModelBlock', projectDirectory=self.projectDirectory, dryrun=True)
    #     self.assertEqual(content[0], TEST_MODEL_BLOCK)
