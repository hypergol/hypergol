import glob
import pickle
from hypergol import Source
from datamodel.article_page import ArticlePage


class LoadHtmlPagesTask(Source):

    def __init__(self, sourcePattern, *args, **kwargs):
        super(LoadHtmlPagesTask, self).__init__(*args, **kwargs)
        self.sourcePattern = sourcePattern

    def source_iterator(self):
        filenames = glob.glob(self.sourcePattern)
        pageId = 0
        for filename in filenames:
            pages = pickle.load(open(filename, 'rb'))
            for page in pages:
                page['pageId'] = pageId
                yield page
                pageId += 1

    def run(self, data):
        return ArticlePage(
            articlePageId=data['pageId'],
            url=data['link'],
            body=data['page']
        )
