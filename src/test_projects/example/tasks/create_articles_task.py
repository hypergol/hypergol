from hypergol import SimpleTask
from data_models.article import Article
from data_models.sentence import Sentence
from data_models.token import Token


class CreateArticlesTask(SimpleTask):

    def __init__(self, exampleParameter, *args, **kwargs):
        super(CreateArticlesTask, self).__init__(*args, **kwargs)
        # TODO: all member variables must be pickle-able, otherwise use the "Delayed" methodology
        # TODO: (e.g. for a DB connection), see the documentation <add link here>
        self.exampleParameter = exampleParameter

    def init(self):
        # TODO: initialise members that are NOT "Delayed" here (e.g. load spacy model)
        pass

    def run(self, exampleInputObject1, exampleInputObject2):
        raise NotImplementedError(f'{self.__class__.__name__} must implement run()')
        return exampleOutputObject
