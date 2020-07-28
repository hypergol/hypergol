import tensorflow as tf
from tqdm.auto import tqdm
from pathlib import Path


class TensorflowModelManager:
    """
    Class for managing tensorflow model training.
    """

    def __init__(self, model, optimizer, batchReader, modelSavePath, tensorboardPath, outputSaver=None, saveProtobuf=True, restoreVariablesPath=None):
        """
        Parameters
        ----------
        model: BaseModel
            model subclassed from BaseModel that is to be trained
        optimizer: tensorflow optimizer
            optimizer from tensorflow package to use for training
        batchReader: Dataset
            Hypergol dataset to use for training
        modelSavePath: path
            filepath to save model checkpoints and outputs
        tensorboardPath: path
            tensorboard path for metrics logging
        outputSaver: BaseModelOutputSaver
            subclass of model output saver class that can save each evaluation batch
        saveProtobuf: bool
            save the model protobuf at each checkpoint step
        restoreVariablesPath: path
            path to restore variables from previously trained model
        """
        self.model = model
        self.optimizer = optimizer
        self.batchReader = batchReader
        self.outputSaver = outputSaver
        self.modelSavePath = modelSavePath
        self.tensorboardPath = tensorboardPath
        self.saveProtobuf = saveProtobuf
        self.restoreVariablesPath = restoreVariablesPath
        self.globalStep = 0
        self.trainingSummaryWriter = None
        self.evaluationSummaryWriter = None
        self.initialize()

    @property
    def checkpointFolder(self):
        folder = Path(self.modelSavePath, 'models', str(self.globalStep))
        folder.mkdir(parents=True, exist_ok=True)
        return folder

    def restore_variables(self, path):
        """restore variables from given path

        Parameters
        ----------
        path: path
        """
        self.model.restore_variables(path=path)

    def initialize(self):
        """
        initialization method, restores variables and creates summary writers
        """
        if self.restoreVariablesPath is not None:
            _ = self.evaluate(withLogging=False, withMetadata=False)
            self.model.restore_variables(path=self.restoreVariablesPath)
        if self.tensorboardPath is not None:
            self.trainingSummaryWriter = tf.summary.create_file_writer(logdir=f'{self.tensorboardPath}/train')
            self.evaluationSummaryWriter = tf.summary.create_file_writer(logdir=f'{self.tensorboardPath}/evaluate')

    def train(self, withLogging, withMetadata):
        """runs a training step for the model

        Parameters
        ----------
        withLogging: bool
            produce tensorflow logging for step
        withMetadata: bool
            log tensorflow graph metadata for step
        """
        batch = next(self.batchReader)
        if withMetadata and self.globalStep > 0:
            tf.summary.trace_on(graph=True, profiler=False)
        loss = self.model.train(inputs=batch['inputs'], targets=batch['targets'], optimizer=self.optimizer)
        if withLogging:
            with self.trainingSummaryWriter.as_default():
                tf.summary.scalar(name='Loss', data=loss, step=self.globalStep)
                if withMetadata and self.globalStep > 0:
                    tf.summary.trace_export(name=f'{self.model.__class__.__name__}{self.globalStep}', step=self.globalStep, profiler_outdir=f'{self.tensorboardPath}/trainGraph')
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
        batch = next(self.batchReader)
        if withMetadata and self.globalStep > 0:
            tf.summary.trace_on(graph=True, profiler=False)
        outputs, loss, metrics = self.model.evaluate(inputs=batch['inputs'], targets=batch['targets'])
        if withLogging:
            with self.evaluationSummaryWriter.as_default():
                tf.summary.scalar(name='Loss', data=loss, step=self.globalStep)
                for scalarName, scalarMetric in metrics.get_scalar_metrics().items():
                    tf.summary.scalar(name=f'Evaluation/{scalarName}', data=scalarMetric, step=self.globalStep)
                for histogramName, histogramMetric in metrics.get_histogram_metrics().items():
                    tf.summary.histogram(name=f'Evaluation/{histogramName}', data=histogramMetric, step=self.globalStep)
                if withMetadata and self.globalStep > 0:
                    tf.summary.trace_export(name=f'{self.model.__class__.__name__}{self.globalStep}', step=self.globalStep, profiler_outdir=f'{self.tensorboardPath}/evaluateGraph')
        if self.outputSaver is not None:
            self.outputSaver.save_outputs(batch=batch, outputs=outputs, globalStep=self.globalStep)
        return outputs, loss, metrics

    def checkpoint(self):
        """checkpoint the model"""
        self.model.checkpoint(path=self.checkpointFolder, packageModel=self.saveProtobuf)

    def run(self, stepCount, evaluationSteps, tensorboardSteps, metadataSteps, trainingSteps=None):
        """runs a training schedule

        Parameters
        ----------
        stepCount: int
            num total steps in schedule
        evaluationSteps: list(int)
            which steps to perform evaluation
        tensorboardSteps: list(int)
            which steps to log metrics to tensorboard
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
                self.model.checkpoint(path=self.checkpointFolder)
                self.evaluate(withLogging=k in tensorboardSteps, withMetadata=k in metadataSteps)
        self.model.checkpoint(path=self.checkpointFolder)
