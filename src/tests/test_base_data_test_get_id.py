from unittest import TestCase

from hypergol.base_data import BaseData
from hypergol.base_data import NoIdException


class DataClassWithoutId(BaseData):

    def __init__(self, value: int):
        self.value = value


class DataClassWithId(BaseData):

    def __init__(self, classId: int, value: int):
        self.classId = classId
        self.value = value

    def get_id(self):
        return (self.classId, )


class DataClassWithBadGetId(BaseData):

    def __init__(self, classId: int, value: int):
        self.classId = classId
        self.value = value

    def get_id(self):
        return self.classId


class TestBaseDataTestGetHashId(TestCase):

    def setUp(self):
        super().setUp()
        self.dataClassWithoutId = DataClassWithoutId(value=1)
        self.dataClassWithId = DataClassWithId(classId=1, value=1)
        self.dataClassWithBadGetId = DataClassWithBadGetId(classId=1, value=1)

    def test_test_get_hash_id_passes_if_no_get_id(self):
        self.assertEqual(self.dataClassWithoutId.test_get_hash_id(), True)

    def test_test_get_hash_id_passes_if_get_id_returns_tuple(self):
        self.assertEqual(self.dataClassWithId.test_get_hash_id(), True)

    def test_test_get_hash_id_throws_error_if_get_id_does_not_returns_tuple(self):
        with self.assertRaises(ValueError):
            self.dataClassWithBadGetId.test_get_hash_id()

    def test_get_hash_id_throws_error(self):
        with self.assertRaises(NoIdException):
            self.dataClassWithoutId.get_hash_id()
