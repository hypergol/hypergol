import json
from pathlib import Path
import tensorflow as tf
from tqdm.auto import tqdm


class TensorflowModelManager:
    """
    Class for managing tensorflow model training.
    """

    def __init__(self, model, optimizer, batchProcessor, saveDirectory, tensorboardPath, restoreWeightsPath=None):
        """
        Parameters
        ----------
        model: BaseModel
            model subclassed from BaseModel that is to be trained
        optimizer: tensorflow optimizer
            optimizer from tensorflow package to use for training
        batchProcessor: Dataset
            Hypergol dataset to use for training
        saveDirectory: path
            filepath to save model checkpoints and outputs
        tensorboardPath: path
            tensorboard path for metrics logging
        restoreWeightsPath: path
            path to restore variables from previously trained model
        """
        self.model = model
        self.optimizer = optimizer
        self.batchProcessor = batchProcessor
        self.saveDirectory = saveDirectory
        self.tensorboardPath = tensorboardPath
        self.restoreWeightsPath = restoreWeightsPath
        self.globalStep = 0
        self.trainingSummaryWriter = None
        self.evaluationSummaryWriter = None

    @property
    def modelSaveDirectory(self):
        saveDir = Path(self.saveDirectory, 'saved_models', str(self.globalStep))
        saveDir.mkdir(parents=True, exist_ok=True)
        return str(saveDir)

    def save_model(self):
        """ saves tensorflow model, block definitions, and weights """
        tf.saved_model.save(self.model, export_dir=self.modelSaveDirectory, signatures=self.model.get_signatures())
        for modelBlock in self.model.get_model_blocks():
            json.dump(modelBlock.get_config(), open(f'{self.modelSaveDirectory}/{modelBlock.get_name()}.json', 'w'))
        self.model.save_weights(f'{self.modelSaveDirectory}/{self.model.get_name()}.h5', save_format='h5')

    def restore_model_weights(self):
        """ restores tensorflow model weights """
        self.model.load_weights(f'{self.restoreWeightsPath}/{self.model.get_name()}.h5')

    def initialize(self):
        """
        initialization method, restores variables and creates summary writers
        """
        self.trainingSummaryWriter = tf.summary.create_file_writer(logdir=f'{self.tensorboardPath}/train')
        self.evaluationSummaryWriter = tf.summary.create_file_writer(logdir=f'{self.tensorboardPath}/evaluate')
        if self.restoreWeightsPath is not None:
            self.evaluate(withLogging=False, withMetadata=False)  # model call needed to initialize layers/weights before reloading
            self.model.restore_model_weights(path=self.restoreWeightsPath)

    def train(self, withLogging, withMetadata):
        """runs a training step for the model

        Parameters
        ----------
        withLogging: bool
            produce tensorflow logging for step
        withMetadata: bool
            log tensorflow graph metadata for step
        """
        batch = next(self.batchProcessor)
        if withMetadata and self.globalStep > 0:
            tf.summary.trace_on(graph=True, profiler=False)
        loss = self.model.train(inputs=batch['inputs'], targets=batch['targets'], optimizer=self.optimizer)
        if withLogging:
            with self.trainingSummaryWriter.as_default():
                tf.summary.scalar(name='Loss', data=loss, step=self.globalStep)
                if withMetadata and self.globalStep > 0:
                    tf.summary.trace_export(name=f'{self.model.get_name()}{self.globalStep}', step=self.globalStep, profiler_outdir=f'{self.tensorboardPath}/trainGraph')
        self.globalStep += 1
        return loss

    def evaluate(self, withLogging, withMetadata):
        """runs an evaluation step for the model

        Parameters
        ----------
        withLogging: bool
            produce tensorflow logging for step
        withMetadata: bool
            log tensorflow graph metadata for step
        """
        batch = next(self.batchProcessor)
        if withMetadata and self.globalStep > 0:
            tf.summary.trace_on(graph=True, profiler=False)
        outputs, loss, metrics = self.model.evaluate(inputs=batch['inputs'], targets=batch['targets'])
        if withLogging:
            with self.evaluationSummaryWriter.as_default():
                tf.summary.scalar(name='Loss', data=loss, step=self.globalStep)
                self.model.produce_metrics(inputs=batch['inputs'], outputs=outputs, targets=batch['targets'])
                if withMetadata and self.globalStep > 0:
                    tf.summary.trace_export(name=f'{self.model.get_name()}{self.globalStep}', step=self.globalStep, profiler_outdir=f'{self.tensorboardPath}/evaluateGraph')
        self.batchProcessor.save_batch(modelInputs=batch, modelOutputs=outputs)
        return outputs, loss, metrics

    def run(self, stepCount, evaluationSteps, tensorboardSteps, metadataSteps, trainingSteps=None):
        """runs a training schedule

        Parameters
        ----------
        stepCount: int
            num total steps in schedule
        evaluationSteps: list(int)
            which steps to produce metrics on an evaluation sample
        tensorboardSteps: list(int)
            which steps to log taining loss to tensorboard
        metadataSteps: list(int)
            which steps to log metadata to tensorboard
        trainingSteps: list(int)
            which steps to train model
        """
        if trainingSteps is None:
            trainingSteps = range(stepCount)
        self.initialize()
        for k in tqdm(range(stepCount)):
            if k in trainingSteps:
                self.train(withLogging=k in tensorboardSteps, withMetadata=k in metadataSteps)
            if k in evaluationSteps:
                self.save_model()
                self.evaluate(withLogging=k in tensorboardSteps, withMetadata=k in metadataSteps)
        self.save_model()
