#!/bin/sh
py src/hypergol.py create_project alpha && \
py src/hypergol.py create_datamodel alpha article articleId:int url:str title:str text:str && \
py src/hypergol.py create_datamodel alpha sentence startChar:int endChar:int articleId:int sentenceId:int && \
diff alpha/ src/test_projects/alpha
