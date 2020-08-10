import fire
import tensorflow as tf
from hypergol import HypergolProject
from hypergol import TensorflowModelManager
from models.my_test_model_batch_processor import MyTestModelBatchProcessor
from models.my_test_model import MyTestModel
from models.embedding_block import EmbeddingBlock
from models.lstm_block import LstmBlock
from models.output_block import OutputBlock
from data_models.sentence import Sentence
from data_models.model_output import ModelOutput


def train_my_test_model(force=False):
    project = HypergolProject(dataDirectory='.', force=force)

    batchProcessor = MyTestModelBatchProcessor(
        inputDataset=project.datasetFactory.get(dataType=Sentence, name='inputs'),
        inputBatchSize=16,
        outputDataset=project.datasetFactory.get(dataType=ModelOutput, name='outputs'),
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
