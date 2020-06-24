import os
import fire
from git import Repo

from hypergol import DatasetFactory
from hypergol import RepoData
from hypergol import Pipeline
from tasks.load_html_pages_task import LoadHtmlPagesTask
from tasks.create_article_texts_task import CreateArticleTextsTask
from tasks.create_articles_task import CreateArticlesTask
from datamodel.article_page import ArticlePage
from datamodel.article_text import ArticleText
from datamodel.article import Article


LOCATION = f'{os.environ["BASE_DIR"]}/tempdata'
PROJECT = 'test'
BRANCH = 'test1'
SOURCE_PATTERN = f'{os.environ["BASE_DIR"]}/data/blogposts/pages_*.pkl'
GIT_REPO_DIRECTORY = f'{os.environ["BASE_DIR"]}/org/hypergol/.git'


def process_blogposts(threads=1, force=False):
    repo = Repo(path=GIT_REPO_DIRECTORY)
    if repo.is_dirty():
        if force:
            print('Warning! Current git repo is dirty, will result in incorrect commit hash in datasets')
        else:
            raise ValueError("git repo is dirty, please commit your work befour you run your pipeline")

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

    articlePages = dsf.get(dataType=ArticlePage, name='article_pages')
    articleTexts = dsf.get(dataType=ArticleText, name='article_texts')
    articles = dsf.get(dataType=Article, name='articles')

    loadHtmlPagesTask = LoadHtmlPagesTask(
        outputDataset=articlePages,
        sourcePattern=SOURCE_PATTERN
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
