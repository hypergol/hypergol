from hypergol import BaseData


class Sentence(BaseData):

    def __init__(self, startChar: int, endChar: int, articleId: int, sentenceId: int):
        self.startChar = startChar
        self.endChar = endChar
        self.articleId = articleId
        self.sentenceId = sentenceId
