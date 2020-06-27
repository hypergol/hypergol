from hypergol import BaseData


class LabelledArticle(BaseData):

    def __init__(self, labelledArticleId: int, articleId: int, labelId: int):
        self.labelledArticleId = labelledArticleId
        self.articleId = articleId
        self.labelId = labelId

    def get_id(self):
        return (self.labelledArticleId, )
