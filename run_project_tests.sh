#!/bin/sh
python src/hypergol.py create_project alpha && \
python src/hypergol.py create_datamodel alpha article articleId:int url:str title:str text:str && \
python src/hypergol.py create_datamodel alpha sentence startChar:int endChar:int articleId:int sentenceId:int && \
diff --suppress-common-lines --no-ignore-file-name-case --recursive alpha/ src/test_projects/alpha
