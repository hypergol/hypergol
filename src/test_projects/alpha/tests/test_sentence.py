from datetime import time
from datetime import date
from datetime import datetime
from unittest import TestCase
from data_models.sentence import Sentence


class TestSentence(TestCase):

    def __init__(self, methodName):
        super(TestSentence, self).__init__(methodName=methodName)
        self.sentence = Sentence(startChar=0, endChar=0, articleId=0, sentenceId=0)

    def setUp(self):
        super().setUp()

    def tearDown(self):
        super().tearDown()

    def test_sentence_test_get_hash_id(self):
        self.assertEqual(self.sentence.test_get_hash_id(), True)

    def test_sentence_test_to_data(self):
        self.assertEqual(self.sentence.test_to_data(), True)

    def test_sentence_test_from_data(self):
        self.assertEqual(self.sentence.test_from_data(), True)
