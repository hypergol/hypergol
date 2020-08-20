import os
from pathlib import Path
import mock

from hypergol.cli.create_model import create_model
from hypergol.hypergol_project import HypergolProject
from tests.hypergol_test_case import TestRepoManager
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
        # calculate loss here and return it
        # input arguments must be the same in all three functions
        # and match with the keys of the return value of BatchProcessor.process_training_batch()

    @tf.function(input_signature=[
        tf.TensorSpec(shape=[None, None], dtype=tf.int32, name='exampleInput1'),
        tf.TensorSpec(shape=[None, None], dtype=tf.string, name='exampleInput2')
    ])
    def get_outputs(self, exampleInput1, exampleInput2):
        raise NotImplementedError('BaseTensorflowModel must implement get_outputs()')
        # calculate the output here and return it, update the decorator accordingly

    def produce_metrics(self, targets, training, globalStep, exampleInput1, exampleInput2s):
        # use tf.summary to record statistics in training/evaluation cycles like
        # tf.summary.scalar(name='exampleName', data=value, step=globalStep)
        pass
""".lstrip()

TEST_BATCH_PROCESSOR = """
import tensorflow as tf
from hypergol import BaseBatchProcessor
from data_models.test_evaluation_class import TestEvaluationClass
from data_models.test_output import TestOutput


class TestModelBatchProcessor(BaseBatchProcessor):

    def __init__(self, inputDataset, inputBatchSize, outputDataset, exampleArgument):
        super(TestModelBatchProcessor, self).__init__(inputDataset, inputBatchSize, outputDataset)
        self.exampleArgument = exampleArgument

    def process_input_batch(self, batch):
        raise NotImplementedError(f'{self.__class__.__name__} must implement `process_input_batch`')
        # batch is a list of datamodel objects cycle through them and build the data
        # that can be converted to tensorflow constants, e.g.:
        # exampleInput1 = []
        # exampleInput2 = []
        # for exampleValue in batch:
        #     exampleInput1.append(exampleValue.exampleList)
        #     exampleInput2.append(len(exampleValue.exampleList))
        # inputs = {
        #     'exampleInput1': tf.ragged.constant(lemmas, dtype=tf.string).to_tensor()[:, 10]
        #     'exampleInput2': tf.constant(sentenceLengths, dtype=tf.int32)
        # }
        # logic can be combined with process_training_batch
        return inputs

    def process_training_batch(self, batch):
        raise NotImplementedError('BaseBatchProcessor must implement process_training_batch()')
        # batch is a list of datamodel objects cycle through them and build the data
        # that can be converted to tensorflow constants, e.g.:
        # exampleInput1 = []
        # exampleInput2 = []
        # exampleOutput = []
        # for exampleValue in batch:
        #     exampleInput1.append(exampleValue.exampleList)
        #     exampleInput2.append(len(exampleValue.exampleList))
        #     exampleOutput.append(exampleValue.exampleOutputList)
        # inputs = {
        #     'exampleInput1': tf.ragged.constant(lemmas, dtype=tf.string).to_tensor()[:, 10]
        #     'exampleInput2': tf.constant(sentenceLengths, dtype=tf.int32)
        # }
        # targets = tf.ragged.constant(, dtype=tf.string).to_tensor()[:, :10]
        return inputs, targets

    def process_output_batch(self, outputs):
        raise NotImplementedError(f'{self.__class__.__name__} must implement `process_output_batch`')
        # create a list of data model classes from the argument and return them
        # outputBatch = []
        # for o in outputs:
        #     outputBatch.append(ExampleOutput(o=o))
        # return outputBatch

    def process_evaluation_batch(self, inputs, targets, outputs):
        raise NotImplementedError('BaseBatchProcessor must implement process_evaluation_batch()')
        # create a list of data model classes from the argument, evaluation classes must have an id because they will be saved into a dataset
        # evaluationBatch = []
        # for id_, i, t, o in zip(inputs['ids'], inputs, targets, outputs):
        #     evaluationBatch.append(ExampleOutput(eoid=id_, i=i, t=t, o=o))
        # return evaluationBatch
""".lstrip()

TEST_TRAIN_MODEL = """
import fire
import tensorflow as tf
from hypergol import HypergolProject
from hypergol import TensorflowModelManager
from models.test_model_batch_processor import TestModelBatchProcessor
from models.test_model import TestModel
from models.test_block1 import TestBlock1
from models.test_block2 import TestBlock2
from data_models.test_training_class import TestTrainingClass
from data_models.test_evaluation_class import TestEvaluationClass


def train_test_model(force=False):
    project = HypergolProject(dataDirectory='.', force=force)

    batchProcessor = TestModelBatchProcessor(
        inputDataset=project.datasetFactory.get(dataType=TestTrainingClass, name='inputs'),
        inputBatchSize=16,
        outputDataset=project.datasetFactory.get(dataType=TestEvaluationClass, name='outputs'),
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
        project=project,
        modelName='TestModel',
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

TEST_SERVE = """
import json
from typing import List
import fire
import uvicorn
import tensorflow as tf
from fastapi import FastAPI
from hypergol.utils import create_pydantic_type
from models.test_model_batch_processor import TestModelBatchProcessor
from data_models.test_input import TestInput
from data_models.test_output import TestOutput

TITLE = 'Serve TestModel'
VERSION = '0.1'
DESCRIPTION = 'FastApi wrapper on TestModel, see /docs for API details'
USE_GPU = False
THREADS = None
MODEL_DIRECTORY = '<data directory>/<project>/<branch>/models/TestModel/<epoch>'


def load_model(modelDirectory, threads, useGPU):
    if not useGPU:
        tf.config.experimental.set_visible_devices([], 'GPU')
    if threads is not None:
        tf.config.threading.set_inter_op_parallelism_threads(threads)
        tf.config.threading.set_intra_op_parallelism_threads(threads)
    return tf.saved_model.load(export_dir=modelDirectory)


model = load_model(modelDirectory=MODEL_DIRECTORY, threads=THREADS, useGPU=USE_GPU)
batchProcessor = TestModelBatchProcessor(
    inputDataset=None,
    inputBatchSize=0,
    maxTokenCount=100,
    outputDataset=None
)

pyDanticTestInput = create_pydantic_type(TestInput)
pyDanticTestOutput = create_pydantic_type(TestOutput)

app = FastAPI(
    title=TITLE,
    version=VERSION,
    description=DESCRIPTION
)


@app.get("/")
def test_main():
    return {
        'title': TITLE,
        'version': VERSION,
        'description': DESCRIPTION
    }


@app.post("/output", response_model=List[pyDanticTestOutput])
def get_outputs(testInputs: List[pyDanticTestInput]):
    testInputs = [TestInput.from_data(json.loads(testInput.json())) for testInput in testInputs]
    tensorInputs = batchProcessor.process_input_batch(testInputs)
    tensorOutputs = model.get_outputs(**tensorInputs)
    testOutputs = batchProcessor.process_output_batch(tensorOutputs)
    return [pyDanticTestOutput.parse_raw(json.dumps(testOutput.to_data())) for testOutput in testOutputs]


def uvicorn_serve_test_model_run(port=8000, host='0.0.0.0'):
    uvicorn.run("serve_test_model:app", port=port, host=host, reload=True)


if __name__ == "__main__":
    tf.get_logger().setLevel('ERROR')
    fire.Fire(uvicorn_serve_test_model_run)
""".lstrip()

TEST_SERVE_SCRIPT = """
export PYTHONPATH="${PWD}/..:${PWD}/../..:"

python3 \\
    ./models/serve_test_model.py \\
    --port=8000 \\
    --host="0.0.0.0"
""".lstrip()


class TestCreateModel(HypergolCreateTestCase):

    def __init__(self, methodName):
        super(TestCreateModel, self).__init__(projectName='TestProject', methodName=methodName)
        self.allPaths = [
            Path(self.projectDirectory, 'models', 'test_model.py'),
            Path(self.projectDirectory, 'models', 'test_model_batch_processor.py'),
            Path(self.projectDirectory, 'models', 'train_test_model.py'),
            Path(self.projectDirectory, 'models', 'serve_test_model.py'),
            Path(self.projectDirectory, 'models'),
            Path(self.projectDirectory, 'train_test_model.sh'),
            Path(self.projectDirectory, 'serve_test_model.sh'),
            Path(self.projectDirectory)
        ]
        self.project = None
        self.maxDiff = 30000

    def setUp(self):
        super().setUp()
        self.project = HypergolProject(
            projectDirectory=self.projectDirectory,
            repoManager=TestRepoManager()
        )
        self.project.create_project_directory()
        self.project.create_models_directory()

    @mock.patch('hypergol.cli.create_pipeline.HypergolProject.check_dependencies')
    def test_create_model_creates_files(self, mock_check_dependencies):
        create_model(
            modelName='TestModel',
            trainingClass='TestTrainingClass',
            evaluationClass='TestEvaluationClass',
            inputClass='TestInput',
            outputClass='TestOutput',
            projectDirectory=self.projectDirectory
        )
        for filePath in self.allPaths:
            self.assertEqual(os.path.exists(filePath), True)

    @mock.patch('hypergol.cli.create_pipeline.HypergolProject.check_dependencies')
    @mock.patch('hypergol.cli.create_pipeline.HypergolProject.is_model_block_class', side_effect=lambda x: x.asClass in ['TestBlock1', 'TestBlock2'])
    def test_create_model_creates_content(self, mock_is_model_block_class, mock_check_dependencies):
        content, batchProcessorContent, trainModelContent, scriptContent, serveContent, serveScriptContent = create_model(
            'TestModel', 'TestTrainingClass', 'TestEvaluationClass', 'TestInput', 'TestOutput', 'TestBlock1', 'TestBlock2', projectDirectory=self.projectDirectory, dryrun=True)
        self.assertEqual(content, TEST_CONTENT)
        self.assertEqual(batchProcessorContent, TEST_BATCH_PROCESSOR)
        self.assertEqual(trainModelContent, TEST_TRAIN_MODEL)
        self.assertEqual(scriptContent, TEST_SCRIPT)
        self.assertEqual(serveContent, TEST_SERVE)
        self.assertEqual(serveScriptContent, TEST_SERVE_SCRIPT)
