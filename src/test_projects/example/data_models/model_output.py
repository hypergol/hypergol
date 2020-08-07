from hypergol import BaseData


class ModelOutput(BaseData):

    def __init__(self, articleId: int, sentenceId: int, inputs: object, outputs: object, targets: object):
        self.articleId = articleId
        self.sentenceId = sentenceId
        self.inputs = inputs
        self.outputs = outputs
        self.targets = targets

    def get_id(self):
        return (self.articleId, self.sentenceId, )

    def to_data(self):
        data = self.__dict__.copy()
        data['inputs'] = BaseData.to_string(data['inputs'])
        data['outputs'] = BaseData.to_string(data['outputs'])
        data['targets'] = BaseData.to_string(data['targets'])
        return data

    @classmethod
    def from_data(cls, data):
        data['inputs'] = BaseData.from_string(data['inputs'])
        data['outputs'] = BaseData.from_string(data['outputs'])
        data['targets'] = BaseData.from_string(data['targets'])
        return cls(**data)
