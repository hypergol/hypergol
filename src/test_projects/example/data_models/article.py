from typing import List
from datetime import datetime
from hypergol import BaseData
from data_models.sentence import Sentence


class Article(BaseData):

    def __init__(self, articleId: int, url: str, title: str, text: str, publishDate: datetime, sentences: List[Sentence]):
        self.articleId = articleId
        self.url = url
        self.title = title
        self.text = text
        self.publishDate = publishDate
        self.sentences = sentences

    def get_id(self):
        return (self.articleId, )

    def to_data(self):
        data = self.__dict__.copy()
        data['publishDate'] = data['publishDate'].isoformat()
        data['sentences'] = [v.to_data() for v in data['sentences']]
        return data

    @classmethod
    def from_data(self, data):
        data['publishDate'] = datetime.fromisoformat(data['publishDate'])
        data['sentences'] = [Sentence.from_data(v) for v in data['sentences']]
        return cls(**data)
