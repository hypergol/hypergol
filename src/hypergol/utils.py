class Repr:

    def __repr__(self):
        members = ', '.join(f'{k}={v}' for k, v in self.__dict__.items())
        return f"{self.__class__.__name__}({members})"

    def __str__(self):
        return self.__repr__()
