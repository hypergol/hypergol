from enum import Enum
from hypergol import BaseData


class Label(BaseData, Enum):

    LENGTH_ODD = (1, 'odd')
    LENGTH_EVEN = (0, 'even')

    def __init__(self, code, value):
        self.code = code
        self.value = value

    def __repr__(self):
        return self.value

    def __reduce_ex__(self, protocol):
        return self.__class__, (self.value, )

    def to_data(self):
        return self.code

    @classmethod
    def from_data(cls, data):
        data['article'] = Article.to_data(data['article'])
        data['label'] = Label.to_data(data['label'])
        return cls(**data)
