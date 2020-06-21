from hypergol import BaseData


class Token(BaseData):

    def __init__(self,i: int, j: int, x: str):
        self.i = i
        self.j = j
        self.x = x

    @classmethod
    def from_data(cls, data):
        return cls(**data)