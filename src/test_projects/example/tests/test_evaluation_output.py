from datetime import time
from datetime import date
from datetime import datetime
from unittest import TestCase
from data_models.evaluation_output import EvaluationOutput


class TestEvaluationOutput(TestCase):

    def __init__(self, methodName):
        super(TestEvaluationOutput, self).__init__(methodName=methodName)
        self.evaluationOutput = EvaluationOutput(articleId=0, sentenceId=0, inputs={"sample": "sample"}, outputs={"sample": "sample"}, targets={"sample": "sample"})

    def setUp(self):
        super().setUp()

    def tearDown(self):
        super().tearDown()

    def test_evaluation_output_test_get_hash_id(self):
        self.assertEqual(self.evaluationOutput.test_get_hash_id(), True)

    def test_evaluation_output_test_to_data(self):
        self.assertEqual(self.evaluationOutput.test_to_data(), True)

    def test_evaluation_output_test_from_data(self):
        self.assertEqual(self.evaluationOutput.test_from_data(), True)
