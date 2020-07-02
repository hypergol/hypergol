from unittest import TestCase
import mock
from hypergol.cli.create_data_model import create_data_model


TEST_CLASS = """
from hypergol import BaseData


class Test(BaseData):

    def __init__(self, testId: int):
        self.testId = testId

    def get_id(self):
        return (self.testId, )
""".lstrip()


TEST_CLASS_NO_ID = """
from hypergol import BaseData


class Test(BaseData):

    def __init__(self, testId: int):
        self.testId = testId
""".lstrip()

TEST_CLASS_WITH_CONVERTER = """
from datetime import datetime
from hypergol import BaseData


class Test(BaseData):

    def __init__(self, testId: int, dt: datetime):
        self.testId = testId
        self.dt = dt

    def to_data(self):
        data = self.__dict__.copy()
        data['dt'] = data['dt'].isoformat()
        return data

    @classmethod
    def from_data(cls, data):
        data['dt'] = datetime.fromisoformat(data['dt'])
        return cls(**data)
""".lstrip()

TEST_CLASS_WITH_LIST = """
from typing import List
from hypergol import BaseData


class Test(BaseData):

    def __init__(self, testId: int, values: List[int]):
        self.testId = testId
        self.values = values
""".lstrip()

TEST_CLASS_WITH_DATA_MODEL_DEPENDENCY = """
from typing import List
from hypergol import BaseData
from data_models.other_test import OtherTest


class Test(BaseData):

    def __init__(self, testId: int, values: List[OtherTest]):
        self.testId = testId
        self.values = values

    def to_data(self):
        data = self.__dict__.copy()
        data['values'] = [v.to_data() for v in data['values']]
        return data

    @classmethod
    def from_data(cls, data):
        data['values'] = [OtherTest.from_data(v) for v in data['values']]
        return cls(**data)
""".lstrip()


class TestCreateDataModel(TestCase):

    def test_create_data_model_simple(self):
        result = create_data_model('Test', 'testId:int:id', dryrun=True)
        self.assertEqual(result, TEST_CLASS)

    def test_create_data_model_no_id(self):
        result = create_data_model('Test', 'testId:int', dryrun=True)
        self.assertEqual(result, TEST_CLASS_NO_ID)

    def test_create_data_model_with_converter(self):
        result = create_data_model('Test', 'testId:int', 'dt:datetime', dryrun=True)
        self.assertEqual(result, TEST_CLASS_WITH_CONVERTER)

    def test_create_data_model_with_list(self):
        result = create_data_model('Test', 'testId:int', 'values:List[int]', dryrun=True)
        self.assertEqual(result, TEST_CLASS_WITH_LIST)

    @mock.patch('hypergol.cli.create_pipeline.HypergolProject.is_data_model_class', side_effect=lambda x: x.asClass == 'OtherTest')
    def test_create_data_model_with_data_model_type(self, is_data_model_class):
        result = create_data_model('Test', 'testId:int', 'values:List[OtherTest]', dryrun=True)
        self.assertEqual(result, TEST_CLASS_WITH_DATA_MODEL_DEPENDENCY)
