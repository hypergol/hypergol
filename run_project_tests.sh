#!/bin/sh
python src/hypergol.py create_project alpha
python src/hypergol.py create_datamodel alpha article articleId:int url:str title:str text:str
python src/hypergol.py create_datamodel alpha sentence startChar:int endChar:int articleId:int sentenceId:int
diff alpha/ src/hypergol/test_projects/alpha
