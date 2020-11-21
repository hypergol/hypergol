from datetime import date

import fire
import tensorflow as tf
from hypergol import HypergolProject
from hypergol import TensorflowModelManager

from models.my_test_model.my_test_model_batch_processor import MyTestModelBatchProcessor
from models.my_test_model.my_test_model import MyTestModel
from models.blocks.embedding_block import EmbeddingBlock
from models.blocks.lstm_block import LstmBlock
from models.blocks.output_block import OutputBlock
from data_models.sentence import Sentence
from data_models.evaluation_output import EvaluationOutput


def train_my_test_model(force=False):
    project = HypergolProject(dataDirectory='.', force=force)

    batchProcessor = MyTestModelBatchProcessor(
        inputDataset=project.datasetFactory.get(dataType=Sentence, name='inputs'),
        inputBatchSize=16,
        outputDataset=project.datasetFactory.get(dataType=EvaluationOutput, name='outputs'),
        exampleArgument=''
    )
    myTestModel = MyTestModel(
        modelName=MyTestModel.__name__,
        longName=f'{MyTestModel.__name__}_{date.today().strftime("%Y%m%d")}_{project.repoManager.commitHash}',
        inputDatasetChkFileCheckSum=f'{batchProcessor.inputDataset.chkFile.get_checksum()}',
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
        project=project,
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
