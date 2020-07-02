import os
import fire
from git import Repo

from hypergol import DatasetFactory
from hypergol import RepoData
from hypergol import Pipeline
from tasks.load_html_pages_task import LoadHtmlPagesTask
from tasks.create_article_texts_task import CreateArticleTextsTask
from tasks.create_articles_task import CreateArticlesTask
from tasks.create_sentences_task import CreateSentencesTask
from data_models.article import Article
from data_models.article_text import ArticleText
from data_models.article_page import ArticlePage
from data_models.sentence import Sentence


LOCATION = '.'
PROJECT = 'example_project'
BRANCH = 'example_branch'


def process_blogposts(threads=1, force=False):
    repo = Repo(path='.')
    if repo.is_dirty():
        if force:
            print('Warning! Current git repo is dirty, this will result in incorrect commit hash in datasets')
        else:
            raise ValueError("Current git repo is dirty, please commit your work befour you run the pipeline")

    commit = repo.commit()
    repoData = RepoData(
        branchName=repo.active_branch.name,
        commitHash=commit.hexsha,
        commitMessage=commit.message,
        comitterName=commit.committer.name,
        comitterEmail=commit.committer.email
    )

    dsf = DatasetFactory(
        location=LOCATION,
        project=PROJECT,
        branch=BRANCH,
        chunkCount=16,
        repoData=repoData
    )
    articles = dsf.get(dataType=Article, name='articles')
    articleTexts = dsf.get(dataType=ArticleText, name='article_texts')
    articlePages = dsf.get(dataType=ArticlePage, name='article_pages')
    sentences = dsf.get(dataType=Sentence, name='sentences')
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
