import os
import fire
from git import Repo

from hypergol import DatasetFactory
from hypergol import RepoData
from hypergol import Pipeline
from tasks.create_article_texts_task import CreateArticleTextsTask
from tasks.create_articles_task import CreateArticlesTask
from tasks.load_html_pages_task import LoadHtmlPagesTask
from data_models.article import Article
from data_models.article_page import ArticlePage
from data_models.labelled_article import LabelledArticle


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
        chunks=16,
        repoData=repoData
    )
    articles = dsf.get(dataType=Article, name='articles')
    articlePages = dsf.get(dataType=ArticlePage, name='article_pages')
    labelledArticles = dsf.get(dataType=LabelledArticle, name='labelled_articles')
    createArticleTextsTask = CreateArticleTextsTask(
        inputDatasets=[exampleInputDataset1,  exampleInputDataset2],
        outputDataset=exampleOutputDataset,
    )
    createArticlesTask = CreateArticlesTask(
        inputDatasets=[exampleInputDataset1,  exampleInputDataset2],
        outputDataset=exampleOutputDataset,
    )
    loadHtmlPagesTask = LoadHtmlPagesTask(
        inputDatasets=[exampleInputDataset1,  exampleInputDataset2],
        outputDataset=exampleOutputDataset,
    )

    pipeline = Pipeline(
        tasks=[
            createArticleTextsTask,
            createArticlesTask,
            loadHtmlPagesTask,
        ]
    )
    pipeline.run(threads=threads)


if __name__ == '__main__':
    fire.Fire(process_blogposts)
