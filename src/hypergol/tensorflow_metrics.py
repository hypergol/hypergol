

class TensorflowMetrics:

    def __init__(self):
        self.scalarMetrics = {}
        self.histogramMetrics = {}

    def add_scalar_metric(self, data, name):
        self.scalarMetrics.update({name: data})

    def add_histogram_metric(self, data, name):
        self.histogramMetrics.update({name: data})

    def get_histogram_metrics(self):
        return self.histogramMetrics

    def get_scalar_metrics(self):
        return self.scalarMetrics
