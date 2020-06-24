import json


from hypergol.utils import Repr


class NoIdException(Exception):
    pass


class BaseData(Repr):

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
        raise NoIdException(f"{self.__class__.__name__} doesn't have an id")

    def get_hash_id(self):
        return self.get_id()

    def to_data(self):
        return self.__dict__.copy()

    @classmethod
    def from_data(cls, data):
        return cls(**data)

    def test_get_hash_id(self):
        try:
            classId = self.get_hash_id()  # pylint: disable=assignment-from-no-return
        except NoIdException:
            return True
        if not isinstance(classId, tuple):
            raise ValueError(f'Return of get_id must be a tuple instead of f{type(classId)}')
        return True

    def test_to_data(self):
        originalData = self.__dict__.copy()
        data = self.to_data()
        for k, v in self.__dict__.items():
            if v != originalData[k]:
                raise AssertionError(f'{self.__class__.__name__}.to_data() changes the instance itself: {k}: {v} != {originalData[k]}')
        try:
            _ = json.dumps(data)
        except TypeError as ex:
            raise TypeError(f'{self.__class__.__name__} JSON serde test failed: {ex}')
        return True

    def test_from_data(self):
        selfCopy = self.from_data(self.to_data())
        if not isinstance(self, type(selfCopy)):
            raise AssertionError(f'{self.__class__.__name__}.from_data() does not return the correct type: {self.__class__.__name__} vs {selfCopy.__class__.__name__}, from_data() return value should be "cls(**data)"')
        for k, v in selfCopy.__dict__.items():
            if v != self.__dict__[k]:
                if str(k) == str(v):
                    raise AssertionError(f'{self.__class__.__name__}.from_data() returns keys as values: {k}: {v} != {self.__dict__[k]}, from_data() return value should be "cls(**data)"')
                raise AssertionError(f'{self.__class__.__name__}.from_data() does not deserialise: {k}: {v} != {self.__dict__[k]}')
        return True
