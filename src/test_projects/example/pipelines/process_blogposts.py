import fire
from hypergol import HypergolProject
from hypergol import Pipeline
from tasks.load_html_pages_task import LoadHtmlPagesTask
from tasks.create_article_texts_task import CreateArticleTextsTask
from tasks.create_articles_task import CreateArticlesTask
from tasks.create_sentences_task import CreateSentencesTask
from data_models.article import Article
from data_models.article_text import ArticleText
from data_models.article_page import ArticlePage
from data_models.sentence import Sentence


def process_blogposts(threads=1, force=False):
    project = HypergolProject(dataDirectory='.', force=force)
    
    articles = project.datasetFactory.get(dataType=Article, name='articles')
    articleTexts = project.datasetFactory.get(dataType=ArticleText, name='article_texts')
    articlePages = project.datasetFactory.get(dataType=ArticlePage, name='article_pages')
    sentences = project.datasetFactory.get(dataType=Sentence, name='sentences')
    loadHtmlPagesTask = LoadHtmlPagesTask(
        inputDatasets=[exampleInputDataset1,  exampleInputDataset2],
        outputDataset=exampleOutputDataset,
    )
    createArticleTextsTask = CreateArticleTextsTask(
        inputDatasets=[exampleInputDataset1,  exampleInputDataset2],
        outputDataset=exampleOutputDataset,
    )
    createArticlesTask = CreateArticlesTask(
        inputDatasets=[exampleInputDataset1,  exampleInputDataset2],
        outputDataset=exampleOutputDataset,
    )
    createSentencesTask = CreateSentencesTask(
        inputDatasets=[exampleInputDataset1,  exampleInputDataset2],
        outputDataset=exampleOutputDataset,
    )

    pipeline = Pipeline(
        tasks=[
            loadHtmlPagesTask,
            createArticleTextsTask,
            createArticlesTask,
            createSentencesTask,
        ]
    )
    pipeline.run(threads=threads)


if __name__ == '__main__':
    fire.Fire(process_blogposts)
