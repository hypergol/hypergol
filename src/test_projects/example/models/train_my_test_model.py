import json
import fire
import tensorflow as tf
from tensorflow.keras import layers
from hypergol import DatasetFactory
from hypergol import TensorflowModelManager
from data_models.sentence import Sentence
from data_models.model_output import ModelOutput

from hypergol import DatasetFactory
from hypergol import RepoData
from hypergol import TensorflowModelManager
from models._data_processor import DataProcessor
from models. import 
from data_models. import 
from data_models. import 


LOCATION = '.'
PROJECT = 'example_project'
BRANCH = 'example_branch'


def my_test_model(force=False):
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

    dsf = DatasetFactory(
        location=LOCATION,
        project=PROJECT,
        branch=BRANCH,
        chunkCount=16,
        repoData=repoData
    )

    batchProcessor = DataProcessor(
        inputDataset=datasetFactory.get(dataType=Sentence, name='sentences'),
        inputBatchSize=16,
        maxTokenCount=100,
        outputDataset=datasetFactory.get(dataType=ModelOutput, name='outputs')
    )
    embeddingDimension = 256
    vocabulary = json.load(open(VOCABULARY_PATH, 'r'))
    posVocabulary = json.load(open(POS_VOCABULARY_PATH, 'r'))
    posModel = PosModel(
        embeddingBlock=EmbeddingBlock(
            vocabulary=vocabulary,
            embeddingDimension=embeddingDimension
        ),
        lstmBlock=LstmBlock(
            embeddingDimension=embeddingDimension,
            layerCount=2,
            posTypeCount=len(posVocabulary),
            dropoutRate=0.1
        ),
        outputBlock=OutputBlock(
            posTypes=posVocabulary
        )
    )
    modelManager = TensorflowModelManager(
        model=posModel,
        optimizer=tf.keras.optimizers.Adam(lr=1),
        batchProcessor=batchProcessor,
        location=LOCATION, project=PROJECT, branch=BRANCH,
        name='testPosModel',
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
