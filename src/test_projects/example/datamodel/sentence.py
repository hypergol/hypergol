from typing import List
from hypergol import BaseData
from datamodel.token import Token


class Sentence(BaseData):
    def __init__(self, startChar: int, endChar: int, articleId: int, sentenceId: int, tokens: List[Token] = None):
        self.startChar = startChar
        self.endChar = endChar
        self.articleId = articleId
        self.sentenceId = sentenceId
        self.tokens = tokens or []

    def get_id(self):
        return (self.articleId, self.sentenceId)

    def to_data(self):
        data = self.__dict__.copy()
        data['tokens'] = [token.to_data() for token in data['tokens']]
        return data

    @classmethod
    def from_data(cls, data):
        data['tokens'] = [Token.from_data(v) for v in data['tokens']]
        return cls(**data)
