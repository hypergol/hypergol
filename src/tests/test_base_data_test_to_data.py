from unittest import TestCase

from hypergol.base_data import BaseData


class SmallDataClass(BaseData):

    def __init__(self, value: int):
        self.value = value


class DataClassWithGoodToData(BaseData):

    def __init__(self, classId: int, smallDataClass: SmallDataClass):
        self.classId = classId
        self.smallDataClass = smallDataClass

    def to_data(self):
        data = self.__dict__.copy()
        data['smallDataClass'] = data['smallDataClass'].to_data()
        return data


class DataClassWithNoDictCopyToData(BaseData):

    def __init__(self, classId: int, smallDataClass: SmallDataClass):
        self.classId = classId
        self.smallDataClass = smallDataClass

    def to_data(self):
        # This should be: data = self.__dict__.copy()
        data = self.__dict__
        data['smallDataClass'] = data['smallDataClass'].to_data()
        return data


class DataClassWithBadCopyToData(BaseData):

    def __init__(self, classId: int, smallDataClass: SmallDataClass):
        self.classId = classId
        self.smallDataClass = smallDataClass

    def to_data(self):
        data = self.__dict__.copy()
        # This line should be here:
        # data['smallDataClass'] = smallDataClass.to_data()
        return data


class TestBaseDataTestToData(TestCase):

    def setUp(self):
        super().setUp()
        self.dataClassWithGoodToData = DataClassWithGoodToData(
            classId=1,
            smallDataClass=SmallDataClass(value=1)
        )
        self.dataClassWithNoDictCopyToData = DataClassWithNoDictCopyToData(
            classId=1,
            smallDataClass=SmallDataClass(value=1)
        )
        self.dataClassWithBadCopyToData = DataClassWithBadCopyToData(
            classId=1,
            smallDataClass=SmallDataClass(value=1)
        )

    def test_test_to_data_returns_true(self):
        self.assertEqual(self.dataClassWithGoodToData.test_to_data(), True)

    def test_test_to_data_throws_error_if_self_change(self):
        with self.assertRaises(AssertionError):
            self.dataClassWithNoDictCopyToData.test_to_data()

    def test_test_to_data_throws_error_if_self_not_serializable(self):
        with self.assertRaises(TypeError):
            self.dataClassWithBadCopyToData.test_to_data()
