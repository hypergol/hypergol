import tensorflow as tf
from pathlib import Path


class ModelManager:

    def __init__(self, model, optimizer, batchGenerator, outputDataManager, modelSavePath, tensorboardPath=None, saveProtobuf=True, restoreVariablesPath=None):
        self.model = model
        self.optimizer = optimizer
        self.batchGenerator = batchGenerator
        self.outputDataManager = outputDataManager
        self.modelSavePath = modelSavePath
        self.tensorboardPath = tensorboardPath
        self.saveProtobuf = saveProtobuf
        self.restoreVariablesPath = restoreVariablesPath
        self.globalStep = 0
        self.trainingSummaryWriter = None
        self.evaluationSummaryWriter = None

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
        batch = next(self.batchGenerator)
        if withMetadata and self.globalStep > 0:
            tf.summary.trace_on(graph=True, profiler=False)
        loss = self.model.train(inputs=batch['inputs'], targets=batch['targets'], optimizer=self.optimizer)
        if withLogging:
            with self.trainingSummaryWriter.as_default():
                tf.summary.scalar(name='Loss', data=loss, step=self.globalStep)
                if withMetadata and self.globalStep > 0:
                    tf.summary.trace_export(name=f'{self.model.__class__.__name__}{self.globalStep}', step=self.globalStep, profiler_outdir=get_path(self.tensorboardPath, 'trainGraph'))
        self.globalStep += 1
        return loss

    def evaluate(self, withLogging, withMetadata):
        batch = next(self.batchGenerator)
        if withMetadata and self.globalStep > 0:
            tf.summary.trace_on(graph=True, profiler=False)
        outputs, loss, metrics = self.model.run_evaluation(inputs=batch['inputs'], targets=batch['targets'])
        self.outputDataManager.process_model_outputs(batch=batch, outputs=outputs, globalStep=self.globalStep)
        if withLogging:
            with self.evaluationSummaryWriter.as_default():
                tf.summary.scalar(name='Loss', data=loss, step=self.globalStep)
                for scalarName, scalarMetric in metrics.get_scalar_metrics().items():
                    tf.summary.scalar(name=f'Evaluation/{scalarName}', data=scalarMetric, step=self.globalStep)
                for histogramName, histogramMetric in metrics.get_histogram_metrics().items():
                    tf.summary.histogram(name=f'Evaluation/{histogramName}', data=histogramMetric, step=self.globalStep)
                if withMetadata and self.globalStep > 0:
                    tf.summary.trace_export(name=f'{self.model.__class__.__name__}{self.globalStep}', step=self.globalStep, profiler_outdir=get_path(self.tensorboardPath, 'evaluateGraph'))
        return outputs, loss, metrics

    def checkpoint(self):
        self.model.checkpoint(path=self.checkpointFolder, packageModel=self.saveProtobuf)

    def run(self, stepCount, evaluationSteps, tensorboardSteps, metricSteps, trainingSteps=None):
        if trainingSteps is None:
            trainingSteps = list(range(evaluationSteps))
        self.initialize()
        for k in range(stepCount):
            if k in trainingSteps:
                self.train(withLogging=k in tensorboardSteps, withMetadata=k in metricSteps)
            if k in evaluationSteps:
                self.model.checkpoint(path=self.checkpointFolder)
                self.evaluate(withLogging=k in tensorboardSteps, withMetadata=k in metricSteps)
        self.model.checkpoint(path=self.checkpointFolder)
