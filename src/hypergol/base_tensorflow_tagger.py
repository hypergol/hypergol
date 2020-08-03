import tensorflow as tf


class BaseTensorflowTagger:

    def __init__(self, modelDirectory, useGPU, threads=None):
        if not useGPU:
            tf.config.experimental.set_visible_devices([], 'GPU')
        if threads is not None:
            tf.config.threading.set_inter_op_parallelism_threads(threads)
            tf.config.threading.set_intra_op_parallelism_threads(threads)
        self.model = tf.saved_model.load(export_dir=f'{modelDirectory}/')

    def get_prediction(self, **kwargs):
        raise NotImplementedError(f'{self.__class__.__name__} must implement `get_prediction` function')
