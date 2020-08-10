import os
from pathlib import Path
import mock

from hypergol.cli.create_pipeline import create_pipeline
from hypergol.hypergol_project import HypergolProject
from tests.cli.hypergol_create_test_case import HypergolCreateTestCase

TEST_CONTENT = """
import fire
from hypergol import HypergolProject
from hypergol import Pipeline
from tasks.example_source import ExampleSource
from tasks.other_task import OtherTask
from data_models.data_model_test_class import DataModelTestClass


def test_pipeline(threads=1, force=False):
    project = HypergolProject(dataDirectory='.', force=force)
    dataModelTestClasses = project.datasetFactory.get(dataType=DataModelTestClass, name='data_model_test_classes')
    exampleSource = ExampleSource(
        inputDatasets=[exampleInputDataset1,  exampleInputDataset2],
        outputDataset=exampleOutputDataset,
    )
    otherTask = OtherTask(
        inputDatasets=[exampleInputDataset1,  exampleInputDataset2],
        outputDataset=exampleOutputDataset,
    )

    pipeline = Pipeline(
        tasks=[
            exampleSource,
            otherTask,
        ]
    )
    pipeline.run(threads=threads)


if __name__ == '__main__':
    fire.Fire(test_pipeline)
""".lstrip()

TEST_SHELL = """
export PYTHONPATH="${PWD}/..:${PWD}/../..:"

THREADS=4

# Disable multithreading in all numerical packages
export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export NUMEXPR_NUM_THREADS=1

python3 \\
    ./pipelines/test_pipeline.py \\
    --threads=${THREADS} \\
    $1
""".lstrip()


class TestCreatePipeline(HypergolCreateTestCase):

    def __init__(self, methodName):
        super(TestCreatePipeline, self).__init__(projectName='TestProject', methodName=methodName)
        self.allPaths = [
            Path(self.projectDirectory, 'test_pipeline.sh'),
            Path(self.projectDirectory, 'pipelines', 'test_pipeline.py'),
            Path(self.projectDirectory, 'pipelines'),
            Path(self.projectDirectory)
        ]
        self.project = None

    def setUp(self):
        super().setUp()
        self.project = HypergolProject(projectDirectory=self.projectDirectory)
        self.project.create_project_directory()
        self.project.create_pipelines_directory()

    def test_create_pipeline_creates_files(self):
        create_pipeline(pipeLineName='TestPipeline', projectDirectory=self.projectDirectory)
        for filePath in self.allPaths:
            self.assertEqual(os.path.exists(filePath), True)

    @mock.patch('hypergol.cli.create_pipeline.HypergolProject.check_dependencies')
    @mock.patch('hypergol.cli.create_pipeline.HypergolProject.is_data_model_class', side_effect=lambda x: x.asClass in ['DataModelTestClass'])
    @mock.patch('hypergol.cli.create_pipeline.HypergolProject.is_task_class', side_effect=lambda x: x.asClass in ['OtherTask', 'ExampleSource'])
    def test_create_pipeline_creates_content(self, mock_is_task_class, mock_is_data_model_class, mock_check_dependencies):
        content, scriptContent = create_pipeline('TestPipeline', 'DataModelTestClass', 'ExampleSource', 'OtherTask', dryrun=True)
        self.assertEqual(content, TEST_CONTENT)
        self.assertEqual(scriptContent, TEST_SHELL)
