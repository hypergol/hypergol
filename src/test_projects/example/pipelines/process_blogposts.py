import fire
from hypergol import DatasetFactory
from hypergol import Dataset
from hypergol import Pipeline
from tasks.load_html_pages_task import LoadHtmlPagesTask
from tasks.create_article_texts_task import CreateArticleTextsTask
from tasks.create_articles_task import CreateArticlesTask
from datamodel.article_page import ArticlePage
from datamodel.article_text import ArticleText
from datamodel.article import Article


def process_blogposts(location, project, branch, sourcePattern, threads):
    dsf = DatasetFactory(
        location=location,
        project=project,
        branch=branch,
        chunks=16
    )

    articlePages = dsf.get(dataType=ArticlePage, name='article_pages')
    articleTexts = dsf.get(dataType=ArticleText, name='article_texts')
    articles = dsf.get(dataType=Article, name='articles')

    loadHtmlPagesTask = LoadHtmlPagesTask(
        outputDataset=articlePages,
        sourcePattern=sourcePattern
    )

    createArticleTextsTask = CreateArticleTextsTask(
        inputDatasets=[articlePages],
        outputDataset=articleTexts,
    )

    createArticlesTask = CreateArticlesTask(
        inputDatasets=[articleTexts],
        outputDataset=articles,
        spacyModelName='en_core_web_sm',
        threads=2
    )

    pipeline1 = Pipeline(
        tasks=[
            loadHtmlPagesTask,
            createArticleTextsTask,
            createArticlesTask
        ]
    )
    pipeline1.run(threads=threads)


if __name__ == '__main__':
    fire.Fire(process_blogposts)
