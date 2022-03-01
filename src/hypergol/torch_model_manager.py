# pylint: skip-file
from pathlib import Path

import torch
from torch.utils.tensorboard import SummaryWriter
from tqdm.auto import tqdm


class TorchModelManager:
    """
    Class for managing Torch model training.
    """

    def __init__(self, model, optimizer, batchProcessor, project, restoreWeightsPath=None):
        """
        Parameters
        ----------
        model: BaseModel
            model subclassed from BaseModel that is to be trained
        optimizer: Torch optimizer
            optimizer from Torch package to use for training
        batchProcessor: Dataset
            Hypergol dataset to use for training
        project: HypergolProject
            Hypergol project to handle directories
        restoreWeightsPath: path
            path to restore variables from a previously trained model
        """
        self.model = model
        self.optimizer = optimizer
        self.batchProcessor = batchProcessor
        self.project = project
        self.restoreWeightsPath = restoreWeightsPath
        self.globalStep = 0
        self.trainingSummaryWriter = None
        self.evaluationSummaryWriter = None

    def save_model(self):
        """Saves Torch model"""
        modelDirectory = Path(self.project.modelDataPath, self.model.modelName, str(self.globalStep))
        modelDirectory.mkdir(parents=True, exist_ok=False)
        scriptModel = torch.jit.script(self.model)
        scriptModel.save(f'{modelDirectory}/saved_model.pt')
        if torch.cuda.is_available():
            model = model.cuda()
            cudaScriptModel = torch.jit.script(self.model)
            cudaScriptModel.save(f'{modelDirectory}/saved_model_cuda.pt')
            model = model.cpu()
        # TODO: This is not equivalent to TF, doesn't support block by block saving/loading
        torch.save(self.model.state_dict(), f'{modelDirectory}/model_state.pt')

    def restore_model_weights(self):
        """Restores Torch model weights """
        self.model.load_state_dict(torch.load(f'{self.restoreWeightsPath}/model_state.pt'))

    def train(self, withTracing):
        """Runs a single training step for the model

        Parameters
        ----------
        withTracing: bool
            log TensorFlow graph metadata for the step
        """
        self.model.train()
        inputs, targets = next(self.batchProcessor)
        if withTracing:
            pass
            # tf.summary.trace_on(graph=True, profiler=False)

        loss = self.model.get_loss(targets=targets, **inputs)
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()
        self.trainingSummaryWriter.add_scalar(tag='Loss', scalar_value=loss, global_step=self.globalStep)
        if withTracing:
            # no tracing in pytorch
            pass
        self.globalStep += 1
        return loss

    def evaluate(self, withTracing):
        """Runs a single evaluation step for the model

        Parameters
        ----------
        withTracing: bool
            TODO: what's this in torch?????? log TensorFlow graph metadata for step
        """
        self.model.eval()
        inputs, targets = next(self.batchProcessor)
        if withTracing:
            # no tracing in pytorch
            pass
        loss = self.model.get_loss(targets=targets, **inputs)
        outputs = self.model.get_evaluation_outputs(**inputs)
        self.evaluationSummaryWriter.add_scalar(tag='Loss', scalar_value=loss, global_step=self.globalStep)
        for tag, value in self.model.produce_metrics(targets=targets, **inputs).items():
            self.evaluationSummaryWriter.add_scalar(tag=tag, scalar_value=value, global_step=self.globalStep)
        self.batchProcessor.save_batch(inputs=inputs, targets=targets, outputs=outputs)
        if withTracing:
            # no tracing in pytorch
            pass
        return loss

    def start(self):
        """Prepares to run the training cycle by creating the model data directories, create the ``SummaryWriters`` for Tensorboard for training and evaluation, initialises the batchprocessor (opens the output dataset for writing) and reloads the weights if ``restoreWeightsPath`` is specified.
        """
        Path(self.project.tensorboardPath, self.model.modelName).mkdir(parents=True, exist_ok=True)
        self.trainingSummaryWriter = SummaryWriter(log_dir=str(Path(self.project.tensorboardPath, self.model.modelName, 'train')))
        self.evaluationSummaryWriter = SummaryWriter(log_dir=str(Path(self.project.tensorboardPath, self.model.modelName, 'evaluate')))
        self.batchProcessor.start()
        if self.restoreWeightsPath is not None:
            self.restore_model_weights()

    def run(self, stepCount, evaluationSteps, tracingSteps):
        """Runs a training schedule

        Model is saved in every evaluation step and at the very last step.

        Parameters
        ----------
        stepCount: int
            num total steps in the schedule
        evaluationSteps: List[int]
            which steps to produce metrics on an evaluation sample
        tracingSteps: List[int]
            which steps to log graph metadata (components, memory consumption, etc.) to Tensorboard
        """
        self.start()
        try:
            for step in tqdm(range(stepCount)):
                if step in evaluationSteps:
                    self.save_model()
                    self.evaluate(withTracing=step in tracingSteps)
                self.train(withTracing=step in tracingSteps)
            self.save_model()
        finally:
            self.finish()

    def finish(self):
        """Finishes training run by closing the output dataset.

        Runs even if the training was interrupted by an exception (e.g. Ctrl-C)
        """
        self.batchProcessor.finish()
