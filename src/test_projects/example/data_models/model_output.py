from typing import List

from hypergol import BaseData


class ModelOutput(BaseData):

    def __init__(self, articleId: int, sentenceId: int, posTags: List[str]):
        self.articleId = articleId
        self.sentenceId = sentenceId
        self.posTags = posTags

    def get_id(self):
        return (self.articleId, self.sentenceId, )
