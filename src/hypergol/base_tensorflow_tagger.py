import tensorflow as tf


class BaseTensorflowTagger:

    def __init__(self, modelDirectory, useGPU, threads=None):
        self.modelDirectory = modelDirectory
        self.useGPU = useGPU
        if not self.useGPU:
            tf.config.experimental.set_visible_devices([], 'GPU')
        self.threads = threads
        if threads is not None:
            tf.config.threading.set_inter_op_parallelism_threads(self.threads)
            tf.config.threading.set_intra_op_parallelism_threads(self.threads)
        self.model = tf.saved_model.load(export_dir=f'{modelDirectory}/')

    def get_prediction(self, **kwargs):
        """ Should call the `get_outputs` function of the model, for consistent interface with TF serve """
        raise NotImplementedError
