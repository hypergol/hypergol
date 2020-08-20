
MAX_MEMBER_REPR_LENGTH = 1000


class Repr:
    """Convencience class to automatically add standard ``__repr__()`` and ``__str__()`` functions to class.

    Uses ``__dict__`` property.
    """

    def __repr__(self):
        members = ', '.join(f'{k}={str(v)[:MAX_MEMBER_REPR_LENGTH]}' for k, v in self.__dict__.items())
        return f"{self.__class__.__name__}({members})"

    def __str__(self):
        return self.__repr__()
