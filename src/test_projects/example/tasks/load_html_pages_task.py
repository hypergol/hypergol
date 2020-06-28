from hypergol import Source
from data_models.article_page import ArticlePage


class LoadHtmlPagesTask(Source):

    def __init__(self, exampleParameter, *args, **kwargs):
        super(LoadHtmlPagesTask, self).__init__(*args, **kwargs)
        # TODO: Source tasks are single threaded, no need for members to be pickle-able
        self.exampleParameter = exampleParameter

    def source_iterator(self):
        raise NotImplementedError(f'{self.__class__.__name__} must implement source_iterator()')
        # TODO: use yield in this function instead of return while your are consuming your source data
        yield exampleData

    def run(self, data):
        raise NotImplementedError(f'{self.__class__.__name__} must implement run()')
        return exampleOutputObject
