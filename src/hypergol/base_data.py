import json
import base64
import pickle

from hypergol.repr import Repr


class NoIdException(Exception):
    pass


class BaseData(Repr):
    """
    Base class for all domain objects.

    Extends the Repr convenience base class that provides printing facilities.

    Provides to_data and from_data serialisation interfaces.

    Provides get_id, get_hash_id interfaces.

    Provides test capabilities for all of the above so changes to the derived classes can be checked quickly.
    """

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
        """Returns the class's id if exists"""
        raise NoIdException(f"{self.__class__.__name__} doesn't have an id")

    def get_hash_id(self):
        """Returns the class's hash id if exists, defaults to get_id()"""
        return self.get_id()

    def to_data(self):
        """Converts class to a dictionary, usually overridden"""
        return self.__dict__.copy()

    @staticmethod
    def to_string(data):
        return base64.b64encode(pickle.dumps(data)).decode('utf-8')

    @staticmethod
    def from_string(data):
        return pickle.loads(base64.b64decode(data.encode('utf-8')))

    @classmethod
    def from_data(cls, data):
        """Creates a class from data, usually overridden

        Parameters
        ----------
        data : dictionary form of data representing the object
            Usually the result of a previous to_data() call.
        """
        return cls(**data)

    def test_get_hash_id(self):
        """Tests if the derived class correctly returns a tuple for an id"""
        try:
            classId = self.get_hash_id()  # pylint: disable=assignment-from-no-return
        except NoIdException:
            return True
        if not isinstance(classId, tuple):
            raise ValueError(f'Return of get_id must be a tuple instead of {type(classId)}')
        return True

    def test_to_data(self):
        """Tests if the output of the derived class's to_data() function can be converted to a string by ``json.dumps()``"""
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
        """Tests if a roundtrip of ``self.from_data(self.to_data())`` modifies the class"""
        selfCopy = self.from_data(self.to_data())
        if not isinstance(self, type(selfCopy)):
            raise AssertionError(f'{self.__class__.__name__}.from_data() does not return the correct type: {self.__class__.__name__} vs {selfCopy.__class__.__name__}, from_data() return value should be "cls(**data)"')
        for k, v in selfCopy.__dict__.items():
            if v != self.__dict__[k]:
                if str(k) == str(v):
                    raise AssertionError(f'{self.__class__.__name__}.from_data() returns keys as values: {k}: {v} != {self.__dict__[k]}, from_data() return value should be "cls(**data)"')
                raise AssertionError(f'{self.__class__.__name__}.from_data() does not deserialise: {k}: {v} != {self.__dict__[k]}')
        return True
