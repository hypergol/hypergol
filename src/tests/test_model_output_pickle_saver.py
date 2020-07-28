import pickle
import shutil
from pathlib import Path
from unittest import TestCase
from hypergol.model_output_pickle_saver import ModelOutputPickleSaver


TEST_SAVE_FILENAME = 'test_save_{globalStep}.pkl'


class TestModelOutputPickleSaver(TestCase):

    def __init__(self, methodName='runTest'):
        super(TestModelOutputPickleSaver, self).__init__(methodName=methodName)
        self.location = 'test_output_saver_location'
        self.saver = ModelOutputPickleSaver(savePath=self.location)
        self.saveData = {
            'batch': {
                'batchIds': list(range(1, 11))
            },
            'outputs': list(range(10))
        }
        self.expectedData = {
            'batchIds': list(range(1, 11)),
            'outputs': list(range(10))
        }

    def setUp(self):
        super().setUp()
        Path(self.location).mkdir()
        self.globalStep = 3
        self.saveDir = self.saver.get_file_save_path(globalStep=self.globalStep)
        self.fullSavePath = f'{self.saveDir}/outputs.pkl'

    def tearDown(self):
        super().tearDown()
        shutil.rmtree(self.location)

    def test_model_output_saver(self):
        self.saver.save_outputs(batch=self.saveData['batch'], outputs=self.saveData['outputs'], globalStep=self.globalStep)
        reloadedData = pickle.load(open(self.fullSavePath, 'rb'))
        self.assertEqual(reloadedData, self.expectedData)
