from hypergol import BaseData


class ArticlePage(BaseData):

    def __init__(self, articlePageId: int, url: str, body: str):
        self.articlePageId = articlePageId
        self.url = url
        self.body = body

    def get_id(self):
        return (self.articlePageId, )
