#!/bin/sh
cd src
pip3 install --upgrade -e .
cd ..
python -m hypergol.cli.create_project alpha && \
python -m hypergol.cli.create_data_model Article articleId:int url:str title:str text:str --projectDirectory=alpha && \
python -m hypergol.cli.create_data_model Sentence startChar:int endChar:int articleId:int sentenceId:int --projectDirectory=alpha && \
diff --suppress-common-lines --no-ignore-file-name-case --recursive alpha/ src/test_projects/alpha/

python -m hypergol.cli.create_project example && \
python -m hypergol.cli.create_data_model --projectDirectory=example Token i:int startChar:int endChar:int depType:str depHead:int depLeftEdge:int depRightEdge:int posType:str posFineType:str lemma:str text:str && \
python -m hypergol.cli.create_data_model --projectDirectory=example Sentence startChar:int endChar:int articleId:int:id sentenceId:int:id "tokens:List[Token]" && \
python -m hypergol.cli.create_data_model --projectDirectory=example Article articleId:int:id url:str title:str text:str publishDate:datetime "sentences:List[Sentence]" && \
python -m hypergol.cli.create_data_model --projectDirectory=example ArticlePage articlePageId:int:id url:str body:str && \
python -m hypergol.cli.create_data_model --projectDirectory=example ArticleText articleTextId:int:id publishDate:datetime title:str text:str url:str && \
python -m hypergol.cli.create_data_model --projectDirectory=example LabelledArticle labelledArticleId:int:id articleId:int labelId:int && \
python -m hypergol.cli.create_task --projectDirectory=example LoadHtmlPagesTask ArticlePage --source && \
python -m hypergol.cli.create_task --projectDirectory=example CreateArticleTextsTask ArticleText --simple && \
python -m hypergol.cli.create_task --projectDirectory=example CreateArticlesTask Article Sentence Token --simple && \
python -m hypergol.cli.create_task --projectDirectory=example CreateSentencesTask Article Sentence && \
python -m hypergol.cli.create_pipeline --projectDirectory=example ProcessBlogposts LoadHtmlPagesTask CreateArticleTextsTask CreateArticlesTask CreateSentencesTask Article ArticleText ArticlePage Sentence && \
diff --suppress-common-lines --no-ignore-file-name-case --recursive example/ src/test_projects/example/
