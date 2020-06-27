from datetime import datetime
from hypergol import BaseData


class ArticleText(BaseData):

    def __init__(self, articleTextId: int, publishDate: datetime, title: str, text: str, url: str):
        self.articleTextId = articleTextId
        self.publishDate = publishDate
        self.title = title
        self.text = text
        self.url = url

    def to_data(self):
        data = self.__dict__.copy()
        data['publishDate'] = data['publishDate'].isoformat()
        return data

    @classmethod
    def from_data(self, data):
        data['publishDate'] = datetime.fromisoformat(data['publishDate'])
        return cls(**data)
