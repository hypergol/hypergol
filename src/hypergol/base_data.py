class BaseData:

    def __repr__(self):
        members = ', '.join(f'{k}={str(v)[:100]}' for k, v in self.__dict__.items())
        return f"{self.__class__.__name__}({members})"

    def __str__(self):
        return self.__repr__()

    def get_id(self):
        raise ValueError(f"{self.__class__.__name__} doesn't have an id")

    def to_data(self):
        return self.__dict__

    @classmethod
    def from_data(cls, data):
        return cls(**data)
