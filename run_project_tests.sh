#!/bin/sh
# cd src
# pip3 install -e .
# cd ..
# python src/hypergol/cli/create_project.py alpha && \
# python src/hypergol/cli/create_data_model.py Article articleId:int url:str title:str text:str --projectDirectory=alpha && \
# python src/hypergol/cli/create_data_model.py Sentence startChar:int endChar:int articleId:int sentenceId:int --projectDirectory=alpha && \
# diff --suppress-common-lines --no-ignore-file-name-case --recursive alpha/ src/test_projects/alpha/

python src/hypergol/cli/create_project.py example && \
python src/hypergol/cli/create_data_model.py --projectDirectory=example Token i:int startChar:int endChar:int depType:str depHead:int depLeftEdge:int depRightEdge:int posType:str posFineType:str lemma:str text:str && \
python src/hypergol/cli/create_data_model.py --projectDirectory=example Sentence startChar:int endChar:int articleId:int sentenceId:int "tokens:List[Token]" && \
python src/hypergol/cli/create_data_model.py --projectDirectory=example Article articleId:int:id url:str title:str text:str publishDate:datetime "sentences:List[Sentence]" && \
python src/hypergol/cli/create_data_model.py --projectDirectory=example ArticlePage articlePageId:int:id url:str body:str && \
python src/hypergol/cli/create_data_model.py --projectDirectory=example ArticleText articleTextId:int publishDate:datetime title:str text:str url:str && \
python src/hypergol/cli/create_data_model.py --projectDirectory=example LabelledArticle labelledArticleId:int:id articleId:int labelId:int && \
python src/hypergol/cli/create_task.py --projectDirectory=example LoadHtmlPagesTask ArticlePage --source && \
python src/hypergol/cli/create_task.py --projectDirectory=example CreateArticleTextsTask ArticleText && \
python src/hypergol/cli/create_task.py --projectDirectory=example CreateArticlesTask Article Sentence Token && \
python src/hypergol/cli/create_pipeline.py --projectDirectory=example ProcessBlogposts LoadHtmlPagesTask CreateArticleTextsTask CreateArticlesTask Article ArticlePage LabelledArticle && \
diff --suppress-common-lines --no-ignore-file-name-case --recursive example/ src/test_projects/example/
