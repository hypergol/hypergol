from hypergol import BaseData


class Article(BaseData):

    def __init__(self,articleId: int, url: str, title: str, text: str):
        self.articleId = articleId
        self.url = url
        self.title = title
        self.text = text

    @classmethod
    def from_data(cls, data):
        return cls(**data)
