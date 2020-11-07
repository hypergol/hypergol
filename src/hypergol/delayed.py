class Delayed:
    """Enables delayed creation of classes so they can be declared in the main script and passed to a thread pickled."""

    def __init__(self, classType, *args, **kwargs):
        """
        Parameters
        ----------
        classType : Class
            type of the class to be created
        args, kwargs :
            parameters of the class's constructor. If they cannot be pickled, they should be turned into :class:`Delayed` as well.
        """
        self.classType = classType
        self.args = args
        self.kwargs = kwargs

    @staticmethod
    def _make(v):
        """Enables recursive creation of the delayed classes"""
        if isinstance(v, Delayed):
            return v.make()
        return v

    def make(self):
        """In a :func:`Task.initialise()`, each :class:`Delayed`'d classes :func:`make()` function is called that creates the class here:
        """
        return self.classType(
            *[self._make(arg) for arg in self.args],
            **{k: self._make(v) for k, v in self.kwargs.items()}
        )
