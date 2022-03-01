from datetime import date

import fire
import torch
from hypergol import HypergolProject
from hypergol import TorchModelManager

from models.my_torch_test_model.my_torch_test_model_batch_processor import MyTorchTestModelBatchProcessor
from models.my_torch_test_model.my_torch_test_model import MyTorchTestModel
from models.blocks.torch_embedding_block import TorchEmbeddingBlock
from models.blocks.torch_lstm_block import TorchLstmBlock
from data_models.sentence import Sentence
from data_models.evaluation_output import EvaluationOutput


def train_my_torch_test_model(force=False):
    project = HypergolProject(dataDirectory='.', force=force)

    batchProcessor = MyTorchTestModelBatchProcessor(
        inputDataset=project.datasetFactory.get(dataType=Sentence, name='inputs'),
        inputBatchSize=16,
        outputDataset=project.datasetFactory.get(dataType=EvaluationOutput, name='outputs'),
        exampleArgument=''
    )
    myTorchTestModel = MyTorchTestModel(
        modelName=MyTorchTestModel.__name__,
        longName=f'{MyTorchTestModel.__name__}_{date.today().strftime("%Y%m%d")}_{project.repoManager.commitHash}',
        inputDatasetChkFileChecksum=f'{batchProcessor.inputDataset.chkFile.get_checksum()}',
        torchEmbeddingBlock=TorchEmbeddingBlock(
            blockArgument1='',
            blockArgument2='',
        ),
        torchLstmBlock=TorchLstmBlock(
            blockArgument1='',
            blockArgument2='',
        ),
    )
    modelManager = TorchModelManager(
        model=myTorchTestModel,
        optimizer=torch.optim.Adam(lr=1),
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
    #TODO:Fix this: tf.get_logger().setLevel('ERROR')
    fire.Fire(train_my_torch_test_model)
