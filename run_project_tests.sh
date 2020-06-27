#!/bin/sh
cd src
pip3 install -e .
cd ..
python src/hypergol/cli/create_project.py alpha && \
python src/hypergol/cli/create_data_model.py Article articleId:int url:str title:str text:str --projectDirectory=alpha && \
python src/hypergol/cli/create_data_model.py Sentence startChar:int endChar:int articleId:int sentenceId:int --projectDirectory=alpha && \
diff --suppress-common-lines --no-ignore-file-name-case --recursive alpha/ src/test_projects/alpha/
