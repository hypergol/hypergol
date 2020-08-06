import json
from pathlib import Path
import tensorflow as tf
from tqdm.auto import tqdm


class TensorflowModelManager:
    """
    Class for managing tensorflow model training.
    """

    def __init__(self, model, optimizer, batchProcessor, location, project, branch, name=None, restoreWeightsPath=None):
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
        self.location = location
        self.project = project
        self.branch = branch
        self.name = name or self.model.get_name()
        self.restoreWeightsPath = restoreWeightsPath
        self.globalStep = 0
        self.trainingSummaryWriter = None
        self.evaluationSummaryWriter = None

    @property
    def tensorboardPath(self):
        tensorboardPath = Path(self.location, self.project, 'tensorboard', self.branch, self.name)
        tensorboardPath.mkdir(parents=True, exist_ok=True)
        return str(tensorboardPath)

    def save_model(self):
        """ saves tensorflow model, block definitions, and weights """
        modelDirectory = Path(self.location, self.project, self.branch, 'models', self.name, str(self.globalStep))
        modelDirectory.mkdir(parents=True, exist_ok=True)
        tf.saved_model.save(self.model, export_dir=str(modelDirectory), signatures={'signature_default': self.model.get_outputs})
        for modelBlock in self.model.get_model_blocks():
            json.dump(modelBlock.get_config(), open(f'{modelDirectory}/{modelBlock.get_name()}.json', 'w'))
        self.model.save_weights(f'{modelDirectory}/{self.model.get_name()}.h5', save_format='h5')

    def restore_model_weights(self):
        """ restores tensorflow model weights """
        self.model.load_weights(f'{self.restoreWeightsPath}/{self.model.get_name()}.h5')

    def train(self, withTracing):
        """runs a training step for the model

        Parameters
        ----------
        withMetadata: bool
            log tensorflow graph metadata for step
        """
        inputs, targets = next(self.batchProcessor)
        if withTracing:
            tf.summary.trace_on(graph=True, profiler=False)

        with tf.GradientTape() as tape:
            loss = self.model.get_loss(targets=targets, training=True, **inputs)
        grads = tape.gradient(loss, self.model.trainable_variables)
        self.optimizer.apply_gradients(zip(grads, self.model.trainable_variables))

        with self.trainingSummaryWriter.as_default():
            tf.summary.scalar(name='Loss', data=loss, step=self.globalStep)
            if withTracing:
                tf.summary.trace_export(
                    name=f'{self.model.get_name()}{self.globalStep}',
                    step=self.globalStep,
                    profiler_outdir=f'{self.tensorboardPath}/trainGraph'
                )
        self.globalStep += 1
        return loss

    def evaluate(self, withTracing):
        """runs an evaluation step for the model

        Parameters
        ----------
        withMetadata: bool
            log tensorflow graph metadata for step
        """
        inputs, targets = next(self.batchProcessor)
        if withTracing:
            tf.summary.trace_on(graph=True, profiler=False)
        loss = self.model.get_loss(targets=targets, training=False, **inputs)
        outputs = self.model.get_evaluation_outputs(**inputs)
        with self.evaluationSummaryWriter.as_default():
            tf.summary.scalar(name='Loss', data=loss, step=self.globalStep)
            self.model.produce_metrics(targets=targets, training=False, globalStep=self.globalStep, **inputs)
            if withTracing:
                tf.summary.trace_export(
                    name=f'{self.model.get_name()}{self.globalStep}',
                    step=self.globalStep,
                    profiler_outdir=f'{self.tensorboardPath}/evaluateGraph'
                )
        self.batchProcessor.save_batch(inputs=inputs, targets=targets, outputs=outputs)
        return loss

    def start(self):
        self.trainingSummaryWriter = tf.summary.create_file_writer(logdir=f'{self.tensorboardPath}/train')
        self.evaluationSummaryWriter = tf.summary.create_file_writer(logdir=f'{self.tensorboardPath}/evaluate')
        if self.restoreWeightsPath is not None:
            self.evaluate(withTracing=False)  # model call needed to initialize layers/weights before reloading
            self.model.restore_model_weights(path=self.restoreWeightsPath)
        self.batchProcessor.start()

    def run(self, stepCount, evaluationSteps, tracingSteps):
        """runs a training schedule

        Parameters
        ----------
        stepCount: int
            num total steps in schedule
        evaluationSteps: List[int]
            which steps to produce metrics on an evaluation sample
        metadataSteps: List[int]
            which steps to log metadata to tensorboard
        """
        self.start()
        try:
            for k in tqdm(range(stepCount)):
                self.train(withTracing=k in tracingSteps)
                if k in evaluationSteps:
                    self.save_model()
                    self.evaluate(withTracing=k in tracingSteps)
            self.save_model()
        finally:
            self.finish()

    def finish(self):
        self.batchProcessor.finish()
