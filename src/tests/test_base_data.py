import json
from unittest import TestCase
from typing import List
from datetime import datetime
from datetime import date
from datetime import time
from hypergol.base_data import BaseData

COMPLEX_DATA_CLASS_STRING = '{"classId": 4, "smallDataClass": {"value": 1}, "valueList": ["a", "b"], "twoLevelDataClass": {"classId": 3, "smallDataClass": {"value": 2}}, "smallDataClassList": [{"value": 3}, {"value": 4}], "datetimeValue": "2020-01-01T12:12:12", "dateValue": "2020-01-01", "timeValue": "12:12:12"}'


class SmallDataClass(BaseData):

    def __init__(self, value: int):
        self.value = value


class DataClassWithoutToData(BaseData):

    def __init__(self, classId: int, smallDataClass: SmallDataClass):
        self.classId = classId
        self.smallDataClass = smallDataClass


class DataClassWithSelfChangingToData(BaseData):

    def __init__(self, classId: int, smallDataClass: SmallDataClass):
        self.classId = classId
        self.smallDataClass = smallDataClass

    def to_data(self):
        data = self.__dict__
        data['smallDataClass'] = data['smallDataClass'].to_data()
        return data


class TwoLevelDataClass(BaseData):

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


class ComplexDataClass(BaseData):

    def __init__(self, classId: int, smallDataClass: SmallDataClass, valueList: List[str], twoLevelDataClass: TwoLevelDataClass, smallDataClassList: List[SmallDataClass], datetimeValue, dateValue, timeValue):
        self.classId = classId
        self.smallDataClass = smallDataClass
        self.valueList = valueList
        self.twoLevelDataClass = twoLevelDataClass
        self.smallDataClassList = smallDataClassList
        self.datetimeValue = datetimeValue
        self.dateValue = dateValue
        self.timeValue = timeValue

    def to_data(self):
        data = self.__dict__.copy()
        data['smallDataClass'] = data['smallDataClass'].to_data()
        data['twoLevelDataClass'] = data['twoLevelDataClass'].to_data()
        data['smallDataClassList'] = [v.to_data() for v in data['smallDataClassList']]
        data['datetimeValue'] = data['datetimeValue'].isoformat()
        data['dateValue'] = data['dateValue'].isoformat()
        data['timeValue'] = data['timeValue'].isoformat()
        return data

    @classmethod
    def from_data(cls, data):
        data['smallDataClass'] = SmallDataClass.from_data(data['smallDataClass'])
        data['twoLevelDataClass'] = TwoLevelDataClass.from_data(data['twoLevelDataClass'])
        data['smallDataClassList'] = [SmallDataClass.from_data(v) for v in data['smallDataClassList']]
        data['datetimeValue'] = datetime.fromisoformat(data['datetimeValue'])
        data['dateValue'] = date.fromisoformat(data['dateValue'])
        data['timeValue'] = time.fromisoformat(data['timeValue'])
        return cls(**data)


class TestBaseData(TestCase):

    def setUp(self):
        super().setUp()
        self.datetimeValue = datetime(2020, 1, 1, 12, 12, 12)
        self.dataClassWithoutToData = DataClassWithoutToData(
            classId=3,
            smallDataClass=SmallDataClass(value=1)
        )
        self.dataClassWithSelfChangingToData = DataClassWithSelfChangingToData(
            classId=3,
            smallDataClass=SmallDataClass(value=2)
        )
        self.complexDataClass = ComplexDataClass(
            classId=4,
            smallDataClass=SmallDataClass(value=1),
            valueList=['a', 'b'],
            twoLevelDataClass=TwoLevelDataClass(
                classId=3,
                smallDataClass=SmallDataClass(value=2)
            ),
            smallDataClassList=[SmallDataClass(value=3), SmallDataClass(value=4)],
            datetimeValue=self.datetimeValue,
            dateValue=self.datetimeValue.date(),
            timeValue=self.datetimeValue.time()
        )
        self.dataClassWithSelfChangingToData.test()

    def test_given_when_then(self):
        self.assertEqual(1, 1)

    def test_self_test_throws_type_error(self):
        with self.assertRaises(TypeError):
            self.dataClassWithoutToData.test()

    def test_self_test_throws_error_if_data_changed_by_to_data(self):
        with self.assertRaises(AssertionError):
            self.dataClassWithSelfChangingToData.test()

    def test_doesnt_change_instance(self):
        data = self.complexDataClass.__dict__.copy()
        self.complexDataClass.to_data()
        self.assertDictEqual(self.complexDataClass.__dict__, data)

    def test_to_data_output_json_serializable(self):
        dataString = json.dumps(self.complexDataClass.to_data())
        self.assertEqual(dataString, COMPLEX_DATA_CLASS_STRING)

    def test_complex_data_class_passes_self_test(self):
        self.assertEqual(self.complexDataClass.test(), True)

    def test_from_data_creates_instance_from_data(self):
        complexDataClass = ComplexDataClass.from_data(json.loads(COMPLEX_DATA_CLASS_STRING))
        self.assertEqual(complexDataClass.classId, self.complexDataClass.classId)
        self.assertEqual(complexDataClass.smallDataClass, self.complexDataClass.smallDataClass)
        self.assertListEqual(complexDataClass.valueList, self.complexDataClass.valueList)
        self.assertEqual(complexDataClass.twoLevelDataClass, self.complexDataClass.twoLevelDataClass)
        self.assertListEqual(complexDataClass.smallDataClassList, self.complexDataClass.smallDataClassList)
        self.assertEqual(complexDataClass.datetimeValue, self.complexDataClass.datetimeValue)
        self.assertEqual(complexDataClass.dateValue, self.complexDataClass.dateValue)
        self.assertEqual(complexDataClass.timeValue, self.complexDataClass.timeValue)
