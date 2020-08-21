from datetime import time
from datetime import date
from datetime import datetime
from unittest import TestCase

from data_models.model_output import ModelOutput


class TestModelOutput(TestCase):

    def __init__(self, methodName):
        super(TestModelOutput, self).__init__(methodName=methodName)
        self.modelOutput = ModelOutput(articleId=0, sentenceId=0, posTags=['', ''])

    def setUp(self):
        super().setUp()

    def tearDown(self):
        super().tearDown()

    def test_model_output_test_get_hash_id(self):
        self.assertEqual(self.modelOutput.test_get_hash_id(), True)

    def test_model_output_test_to_data(self):
        self.assertEqual(self.modelOutput.test_to_data(), True)

    def test_model_output_test_from_data(self):
        self.assertEqual(self.modelOutput.test_from_data(), True)
