from typing import List
from hypergol import BaseData
from datamodel.article import Article
from datamodel.label import Label


class LabelledArticle(BaseData):

    def __init__(self, labelledArticleId, article, label):
        self.labelledArticleId = labelledArticleId
        self.article = article
        self.label = label

    def get_id(self):
        return (self.labelledArticleId)

    def to_data(self):
        data = self.__dict__.copy()
        data['article'] = data['article'].to_data()
        data['label'] = data['label'].to_data()
        return data

    @classmethod
    def from_data(cls, data):
        data['article'] = Article.to_data(data['article'])
        data['label'] = Label.to_data(data['label'])
        return cls(**data)
