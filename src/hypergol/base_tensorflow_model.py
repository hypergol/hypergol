# pylint: disable=E0611, W0235

import inspect
from tensorflow.python import keras
from hypergol.base_tensorflow_model_block import BaseTensorflowModelBlock


class BaseTensorflowModel(keras.Model):
    """Main Tensorflow model class, responsible for implementing the interface of the model and the connection between the model blocks.

    It is recommended to avoid overwriting ``keras``'s ``call()`` and ``build()`` functions because of their sideeffects. Model blocks should be initialised at construction and if additional tensors are needed in this model they should be initialised in the ``__init__()`` function as well.

    Inputs for the three (``get_loss()``, ``produce_metrics()`` and ``get_outputs()``) implemented functions must match and match with the return value of the model's batchprocessr's process_input_batch() function. The output of get_outputs()
    """

    def __init__(self, **kwargs):
        """
        Parameters
        ----------
        block1 : BaseTensorFlowBlock
            pass in block instances rather than construct them here
        other parameters :

        """
        super(BaseTensorflowModel, self).__init__(**kwargs)

    def get_model_blocks(self):
        """Returns blocks that are both member variables and arguments of the constructor for serialisation"""
        constructorParameters = inspect.signature(self.__class__.__init__).parameters.keys()
        return [v for k, v in self.__dict__.items() if k in constructorParameters and isinstance(v, BaseTensorflowModelBlock)]

    def get_name(self):
        return self.__class__.__name__

    def call(self, inputs, training=None, mask=None):
        """This function is obsolete"""
        raise Exception(f'keras.Model.call() was called in Hypergol model {self.name}')

    def get_loss(self, targets, training, **kwargs):
        """Must return a single value as the loss between targets and the inputs passed in through ``**kwargs``

        Parameters
        ----------
        targets :
            Expected output values
        training : bool
            True if the loss is calculated during training, False otherwise
        **kwargs :
            Input values as keyword arguments
        """
        raise NotImplementedError('Must implement `get_loss` function')

    def produce_metrics(self, targets, training, globalStep, **kwargs):
        """This function records values for TensorBoard, it runs in the context of a ``tf.summary.SummaryWriter`` so the implementation just need to call ``tf.summary.scalar`` or any other summary functions to record data to TensorBoard. See `https://www.tensorflow.org/api_docs/python/tf/summary <https://www.tensorflow.org/api_docs/python/tf/summary>`__ for further documentation on this.

        It should not return anything as it will be discarded.

        Parameters
        ----------
        targets :
            Expected output values
        training : bool
            True if the loss is calculated during training, False otherwise
        globalStep : int
            The training/evaluation global step to be used as ``step`` in the summary functions
        **kwargs :
            Input values as keyword arguments
        """
        raise NotImplementedError('Must implement `produce_metrics` function')

    def get_outputs(self, **kwargs):
        """This function returns the models response for an input, when the model deployed this is the interface to the calculations.

        The ``get_outputs()`` function must specify the signiture with the ``@tf.function`` decorator because this enables the model to be packaged and to be deployed as a standalone model. See the Tutorial for example.

        Must return a single value that will be converted to the output datamodel class by the model's batch processor.

        Parameters
        ----------
        **kwargs :
            Input values as keyword arguments
        """
        raise NotImplementedError('Must implement `get_outputs` function')

    def get_evaluation_outputs(self, **kwargs):
        """If evaluation is different from training that can be implemented here as during evaluation :class:`.TensorflowModelManager` actually calls this and this calls ``self.get_outputs``. Same rules apply as for that.
        """
        return self.get_outputs(**kwargs)
