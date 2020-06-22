import os
from unittest import TestCase

from hypergol.base_data import BaseData
from hypergol.dataset import Dataset


class DataClass(BaseData):

    def __init__(self, id_: int, value: int):
        self.id_ = id_
        self.value = value

    def get_id(self):
        return (self.id_, )


class TestDataset(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        dataset = Dataset(
            dataType=DataClass,
            location='.',
            project='test_x',
            branch='branch',
            name='data_class',
            chunks=16
        )
        if not dataset.exists():
            with dataset.open('w') as ds:
                for k in range(100):
                    ds.append(DataClass(id_=1, value=k))

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        dataset = Dataset(
            dataType=DataClass,
            location='.',
            project='test_x',
            branch='branch',
            name='data_class',
            chunks=16
        )
        if dataset.exists():
            dataset.delete()
        os.rmdir(f'{dataset.location}/{dataset.project}/{dataset.branch}')
        os.rmdir(f'{dataset.location}/{dataset.project}')

    def test_hello_world(self):
        self.assertEqual(True, True)

    def test_open_returns_the_correct_objects(self):
        pass

    def test_init_in_read_mode_fails_if_dataset_does_not_exist(self):
        pass

    def test_init_in_read_mode_fails_if_existing_dataset_def_does_not_match(self):
        pass

    def test_get_chunks_returns_the_right_chunks(self):
        pass

    def test_init_in_write_mode_fails_if_dataset_already_exist(self):
        pass

    def test_delete_fails_if_dataset_does_not_exist(self):
        pass

    def test_get_object_chunk_id_returns_the_correct_hash(self):
        pass
