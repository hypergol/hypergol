import tensorflow as tf
from tqdm.auto import tqdm
from pathlib import Path


class ModelManager:

    def __init__(self, model, optimizer, batchReader, outputSaver, modelSavePath, tensorboardPath, saveProtobuf=True, restoreVariablesPath=None):
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
        self.model.restore_variables(path=path)

    def initialize(self):
        if self.restoreVariablesPath is not None:
            _ = self.evaluate(withLogging=False, withMetadata=False)
            self.model.restore_variables(path=self.restoreVariablesPath)
        if self.tensorboardPath is not None:
            self.trainingSummaryWriter = tf.summary.create_file_writer(logdir=f'{self.tensorboardPath}/train')
            self.evaluationSummaryWriter = tf.summary.create_file_writer(logdir=f'{self.tensorboardPath}/evaluate')

    def train(self, withLogging, withMetadata):
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
        self.outputSaver.save_outputs(batch=batch, outputs=outputs, globalStep=self.globalStep)
        return outputs, loss, metrics

    def checkpoint(self):
        self.model.checkpoint(path=self.checkpointFolder, packageModel=self.saveProtobuf)

    def run(self, stepCount, evaluationSteps, tensorboardSteps, metadataSteps, trainingSteps=None):
        if trainingSteps is None:
            trainingSteps = range(len(evaluationSteps))
        self.initialize()
        for k in tqdm(range(stepCount)):
            if k in trainingSteps:
                self.train(withLogging=k in tensorboardSteps, withMetadata=k in metadataSteps)
            if k in evaluationSteps:
                self.model.checkpoint(path=self.checkpointFolder)
                self.evaluate(withLogging=k in tensorboardSteps, withMetadata=k in metadataSteps)
        self.model.checkpoint(path=self.checkpointFolder)
