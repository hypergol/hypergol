from unittest import TestCase

from hypergol.base_data import BaseData


class SmallDataClass(BaseData):

    def __init__(self, value: int):
        self.value = value


class DataClassWithGoodFromData(BaseData):

    def __init__(self, classId: int, smallDataClass: SmallDataClass):
        self.classId = classId
        self.smallDataClass = smallDataClass

    def to_data(self):
        data = self.__dict__.copy()
        data['smallDataClass'] = data['smallDataClass'].to_data()
        return data

    @classmethod
    def from_data(cls, data):
        data['smallDataClass'] = SmallDataClass.from_data(data['smallDataClass'])
        return cls(**data)


class DataClassWithBadFromData(BaseData):

    def __init__(self, classId: int, smallDataClass: SmallDataClass):
        self.classId = classId
        self.smallDataClass = smallDataClass

    def to_data(self):
        data = self.__dict__.copy()
        data['smallDataClass'] = data['smallDataClass'].to_data()
        return data

    @classmethod
    def from_data(cls, data):
        # This line should be here:
        # data['smallDataClass'] = SmallDataClass.from_data(data['smallDataClass'])
        return cls(**data)


class DataClassWithFromDataWrongReturn(BaseData):

    def __init__(self, classId: int, smallDataClass: SmallDataClass):
        self.classId = classId
        self.smallDataClass = smallDataClass

    def to_data(self):
        data = self.__dict__.copy()
        data['smallDataClass'] = data['smallDataClass'].to_data()
        return data

    @classmethod
    def from_data(cls, data):
        data['smallDataClass'] = SmallDataClass.from_data(data['smallDataClass'])
        # This should be: return cls(**data)
        return cls(*data)


class DataClassWithFromDataNoConstructor(BaseData):

    def __init__(self, classId: int, smallDataClass: SmallDataClass):
        self.classId = classId
        self.smallDataClass = smallDataClass

    def to_data(self):
        data = self.__dict__.copy()
        data['smallDataClass'] = data['smallDataClass'].to_data()
        return data

    @classmethod
    def from_data(cls, data):
        data['smallDataClass'] = SmallDataClass.from_data(data['smallDataClass'])
        # This should be: return cls(**data)
        return data


class TestBaseDataTestFromData(TestCase):

    def setUp(self):
        super().setUp()
        self.dataClassWithGoodFromData = DataClassWithGoodFromData(
            classId=1,
            smallDataClass=SmallDataClass(value=1)
        )
        self.dataClassWithBadFromData = DataClassWithBadFromData(
            classId=1,
            smallDataClass=SmallDataClass(value=1)
        )
        self.dataClassWithFromDataWrongReturn = DataClassWithFromDataWrongReturn(
            classId=1,
            smallDataClass=SmallDataClass(value=1)
        )
        self.dataClassWithFromDataNoConstructor = DataClassWithFromDataNoConstructor(
            classId=1,
            smallDataClass=SmallDataClass(value=1)
        )

    def test_test_from_data_returns_true(self):
        self.assertEqual(self.dataClassWithGoodFromData.test_from_data(), True)

    def test_test_from_data_throws_error_if_missing_conversion(self):
        with self.assertRaises(AssertionError):
            self.assertEqual(self.dataClassWithBadFromData.test_from_data(), True)

    def test_test_from_data_throw_error_if_bad_return_value(self):
        with self.assertRaises(AssertionError):
            self.assertEqual(self.dataClassWithFromDataWrongReturn.test_from_data(), True)

    def test_test_from_data_throw_error_if_no_constructor(self):
        with self.assertRaises(AssertionError):
            self.assertEqual(self.dataClassWithFromDataNoConstructor.test_from_data(), True)
