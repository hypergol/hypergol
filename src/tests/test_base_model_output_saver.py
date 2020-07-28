import os
import json
from pathlib import Path
from unittest import TestCase
from hypergol.base_model_output_saver import BaseModelOutputSaver


TEST_SAVE_FILENAME = 'test_save_{globalStep}.json'


class ModelOutputSaverExample(BaseModelOutputSaver):

    def __init__(self, savePath):
        super(ModelOutputSaverExample, self).__init__(savePath=savePath)

    def save_outputs(self, batch, outputs, globalStep):
        saveData = {
            'batch': batch,
            'outputs': outputs,
            'globalStep': globalStep
        }
        fileName = TEST_SAVE_FILENAME.format(globalStep=globalStep)
        json.dump(saveData, open(f'{self.savePath}/{fileName}', 'w'))


class TestBaseModelOutputSaver(TestCase):

    def __init__(self, methodName='runTest'):
        super(TestBaseModelOutputSaver, self).__init__(methodName=methodName)
        self.location = 'test_output_saver_location'

    def setUp(self):
        super().setUp()
        Path(self.location).mkdir()
        self.saveData = {
            'batch': list(range(3)),
            'outputs': list(range(10)),
            'globalStep': 3
        }
        self.saveFilename = TEST_SAVE_FILENAME.format(globalStep=self.saveData["globalStep"])
        self.fullSavePath = f'{self.location}/{self.saveFilename}'

    def tearDown(self):
        super().tearDown()
        os.remove(self.fullSavePath)
        os.rmdir(self.location)

    def test_model_output_saver(self):
        outputSaver = ModelOutputSaverExample(savePath=self.location)
        outputSaver.save_outputs(batch=self.saveData['batch'], outputs=self.saveData['outputs'], globalStep=self.saveData['globalStep'])
        reloadedData = json.load(open(self.fullSavePath, 'r'))
        self.assertEqual(reloadedData, self.saveData)
