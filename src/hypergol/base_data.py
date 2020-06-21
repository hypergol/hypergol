import json


class BaseData:

    def __repr__(self):
        members = ', '.join(f'{k}={str(v)[:100]}' for k, v in self.__dict__.items())
        return f"{self.__class__.__name__}({members})"

    def __str__(self):
        return self.__repr__()

    def __eq__(self, other):
        if not isinstance(self, type(other)):
            return False
        try:
            for k in set(self.__dict__.keys()) | set(self.__dict__.keys()):
                if not self.__dict__.__eq__(other.__dict__[k]):
                    return False
            return True
        except KeyError:
            return False

    def get_id(self):
        raise ValueError(f"{self.__class__.__name__} doesn't have an id")

    def to_data(self):
        return self.__dict__.copy()

    @classmethod
    def from_data(cls, data):
        return cls(**data)

    def test(self):
        try:
            originalData = self.__dict__.copy()
            data = self.to_data()
            for k, v in self.__dict__.items():
                if v != originalData[k]:
                    raise AssertionError(f'{self.__class__.__name__}.to_data() changes itself: {k}: {v} != {originalData[k]}')
            selfCopy = self.from_data(json.loads(json.dumps(data)))
            for k, v in selfCopy.__dict__.items():
                if v != self.__dict__[k]:
                    raise AssertionError(f'{self.__class__.__name__}.from_data() does not deserialise: {k}: {v} != {self.__dict__[k]}')
            if not isinstance(self, type(selfCopy)):
                raise AssertionError(f'{self.__class__.__name__}.from_data() does not return the correct type: {self.__class__.__name__} vs {selfCopy.__class__.__name__}')'
            return True
        except TypeError as ex:
            raise TypeError(f'{self.__class__.__name__} self test failed: {ex}')
