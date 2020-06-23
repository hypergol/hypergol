class Delayed:

    def __init__(self, classType, *args, **kwargs):
        self.classType = classType
        self.args = args
        self.kwargs = kwargs

    @staticmethod
    def _make(v):
        if isinstance(v, Delayed):
            return v.make()
        return v

    def make(self):
        return self.classType(
            *[self._make(arg) for arg in self.args],
            **{k: self._make(v) for k, v in self.kwargs.items()}
        )
