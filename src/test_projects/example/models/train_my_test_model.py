import fire
from git import Repo
import tensorflow as tf
from hypergol import DatasetFactory
from hypergol import RepoData
from hypergol import TensorflowModelManager
from models.my_test_model_data_processor import MyTestModelDataProcessor
from models.my_test_model import MyTestModel
from models.embedding_block import EmbeddingBlock
from models.lstm_block import LstmBlock
from models.output_block import OutputBlock
from data_models.sentence import Sentence
from data_models.model_output import ModelOutput


LOCATION = '.'
PROJECT = 'example_project'
BRANCH = 'example_branch'


def train_my_test_model(force=False):
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

    batchProcessor = MyTestModelDataProcessor(
        inputDataset=datasetFactory.get(dataType=Sentence, name='inputs'),
        inputBatchSize=16,
        outputDataset=datasetFactory.get(dataType=ModelOutput, name='outputs'),
        exampleArgument=''
    )
    myTestModel = MyTestModel(
        embeddingBlock=EmbeddingBlock(
            blockArgument1='',
            blockArgument2='',
        ),
        lstmBlock=LstmBlock(
            blockArgument1='',
            blockArgument2='',
        ),
        outputBlock=OutputBlock(
            blockArgument1='',
            blockArgument2='',
        ),
    )
    modelManager = TensorflowModelManager(
        model=myTestModel,
        optimizer=tf.keras.optimizers.Adam(lr=1),
        batchProcessor=batchProcessor,
        location=LOCATION,
        project=PROJECT,
        branch=BRANCH,
        name='MyTestModel',
        restoreWeightsPath=None
    )
    modelManager.run(
        stepCount=100,
        evaluationSteps=list(range(0, 100, 10)),
        tracingSteps=list(range(0, 100, 5))
    )


if __name__ == '__main__':
    tf.get_logger().setLevel('ERROR')
    fire.Fire(train_my_test_model)
