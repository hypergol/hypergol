import json
from pathlib import Path
import tensorflow as tf
from tqdm.auto import tqdm


class TensorflowModelManager:
    """
    Class for managing tensorflow model training.
    """

    def __init__(self, model, optimizer, batchProcessor, project, modelName, restoreWeightsPath=None):
        """
        Parameters
        ----------
        model: BaseModel
            model subclassed from BaseModel that is to be trained
        optimizer: tensorflow optimizer
            optimizer from tensorflow package to use for training
        batchProcessor: Dataset
            Hypergol dataset to use for training
        project: HypergolProject
            Hypergol project to handle directories
        modelName: string
            Name of the model
        restoreWeightsPath: path
            path to restore variables from previously trained model
        """
        self.model = model
        self.optimizer = optimizer
        self.batchProcessor = batchProcessor
        self.project = project
        self.modelName = modelName or self.model.get_name()
        self.restoreWeightsPath = restoreWeightsPath
        self.globalStep = 0
        self.trainingSummaryWriter = None
        self.evaluationSummaryWriter = None

    def save_model(self):
        """Saves Tensorflow model, block definitions, and weights """
        modelDirectory = Path(self.project.modelDataPath, self.modelName, str(self.globalStep))
        modelDirectory.mkdir(parents=True, exist_ok=True)
        tf.saved_model.save(self.model, export_dir=str(modelDirectory), signatures={'signature_default': self.model.get_outputs})
        for modelBlock in self.model.get_model_blocks():
            json.dump(modelBlock.get_config(), open(f'{modelDirectory}/{modelBlock.get_name()}.json', 'w'))
        self.model.save_weights(f'{modelDirectory}/{self.model.get_name()}.h5', save_format='h5')

    def restore_model_weights(self):
        """Restores Tensorflow model weights """
        self.model.load_weights(f'{self.restoreWeightsPath}/{self.model.get_name()}.h5')

    def train(self, withTracing):
        """Runs a single training step for the model

        Parameters
        ----------
        withTracing: bool
            log tensorflow graph metadata for the step
        """
        inputs, targets = next(self.batchProcessor)
        if withTracing:
            tf.summary.trace_on(graph=True, profiler=False)

        with tf.GradientTape() as tape:
            loss = self.model.get_loss(targets=targets, training=True, **inputs)
        grads = tape.gradient(loss, self.model.trainable_variables)
        self.optimizer.apply_gradients(zip(grads, self.model.trainable_variables))

        # Watch this issue: https://github.com/PyCQA/pylint/issues/3596
        with self.trainingSummaryWriter.as_default():  # pylint: disable=not-context-manager
            tf.summary.scalar(name='Loss', data=loss, step=self.globalStep)
            if withTracing:
                tf.summary.trace_export(
                    name=f'{self.model.get_name()}{self.globalStep}',
                    step=self.globalStep,
                    profiler_outdir=str(Path(self.project.tensorboardPath, self.modelName, 'trainGraph'))
                )
        self.globalStep += 1
        return loss

    def evaluate(self, withTracing):
        """Runs a single evaluation step for the model

        Parameters
        ----------
        withTracing: bool
            log tensorflow graph metadata for step
        """
        inputs, targets = next(self.batchProcessor)
        if withTracing:
            tf.summary.trace_on(graph=True, profiler=False)
        loss = self.model.get_loss(targets=targets, training=False, **inputs)
        outputs = self.model.get_evaluation_outputs(**inputs)
        with self.evaluationSummaryWriter.as_default():  # pylint: disable=not-context-manager
            tf.summary.scalar(name='Loss', data=loss, step=self.globalStep)
            self.model.produce_metrics(targets=targets, training=False, globalStep=self.globalStep, **inputs)
            if withTracing:
                tf.summary.trace_export(
                    name=f'{self.model.get_name()}{self.globalStep}',
                    step=self.globalStep,
                    profiler_outdir=str(Path(self.project.tensorboardPath, self.modelName, 'evaluateGraph'))
                )
        self.batchProcessor.save_batch(inputs=inputs, targets=targets, outputs=outputs)
        return loss

    def start(self):
        """Prepares to run the training cycle by creating the model data directories, create the ``SummaryWriters`` for Tensorboard for training and evaluation, initialises the batchprocessor (opens the output dataset for writing) and reloads the weights if ``restoreWeightsPath`` is specified.
        """
        Path(self.project.tensorboardPath, self.modelName).mkdir(parents=True, exist_ok=True)
        self.trainingSummaryWriter = tf.summary.create_file_writer(logdir=str(Path(self.project.tensorboardPath, self.modelName, 'train')))
        self.evaluationSummaryWriter = tf.summary.create_file_writer(logdir=str(Path(self.project.tensorboardPath, self.modelName, 'evaluate')))
        self.batchProcessor.start()
        if self.restoreWeightsPath is not None:
            self.evaluate(withTracing=False)  # model call needed to initialize layers/weights before reloading
            self.restore_model_weights()

    def run(self, stepCount, evaluationSteps, tracingSteps):
        """Runs a training schedule

        Model is saved in every evaluation step and at the very last step.

        Parameters
        ----------
        stepCount: int
            num total steps in schedule
        evaluationSteps: List[int]
            which steps to produce metrics on an evaluation sample
        tracingSteps: List[int]
            which steps to log graph metadata (components, memory consumption, etc) to Tensorboard
        """
        self.start()
        try:
            for step in tqdm(range(stepCount)):
                self.train(withTracing=step in tracingSteps)
                if step in evaluationSteps:
                    self.save_model()
                    self.evaluate(withTracing=step in tracingSteps)
            self.save_model()
        finally:
            self.finish()

    def finish(self):
        """Finishes training run by closing the output dataset.

        Runs even if the training was interrupted by an exception (e.g. Ctrl-C)
        """
        self.batchProcessor.finish()
