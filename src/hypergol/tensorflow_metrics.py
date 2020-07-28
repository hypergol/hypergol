

class TensorflowMetrics:
    """
    Holder class for tensorflow metrics, used in the TensorflowModelManager as outputs for tensorboard

    Can use to add/retrieve scalar and histogram metrics
    """

    def __init__(self):
        self.scalarMetrics = {}
        self.histogramMetrics = {}

    def add_scalar_metric(self, data, name):
        """Adds a scalar metric to tensorboard

        Parameters
        ----------
        data : tf.Tensor
        name: str
        """
        self.scalarMetrics.update({name: data})

    def add_histogram_metric(self, data, name):
        """Adds a histogram metric to tensorboard

        Parameters
        ----------
        data : tf.Tensor
        name: str
        """
        self.histogramMetrics.update({name: data})

    def get_histogram_metrics(self):
        """Retrieves a dictionary of histogram metrics"""
        return self.histogramMetrics

    def get_scalar_metrics(self):
        """Retrieves a dictionary of scalar metrics"""
        return self.scalarMetrics
