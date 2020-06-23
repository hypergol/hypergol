from datetime import datetime
from hypergol import Task
from bs4 import BeautifulSoup
from datamodel.article_text import ArticleText


class CreateArticleTextsTask(Task):

    def __init__(self, *args, **kwargs):
        super(CreateArticleTextsTask, self).__init__(*args, **kwargs)

    def run(self, articlePage):
        try:
            soup = BeautifulSoup(articlePage.body, features='html.parser')
            body = soup.find('div', class_='has-content-area')
            content = '\n'.join([v.text for v in body.children])
            meta = soup.find('meta', property="article:published_time")
            return ArticleText(
                articleTextId=articlePage.articlePageId,
                publishDate=datetime.fromisoformat(meta.attrs['content']),
                title=body['data-title'],
                text=content,
                url=articlePage.url
            )
        except AttributeError as ex:
            print(f'Error in {articlePage.articlePageId}: {ex}')
            return ArticleText(
                articleTextId=articlePage.articlePageId,
                publishDate=datetime.now(),
                title="Error while processing article",
                text=str(ex),
                url=articlePage.url
            )
