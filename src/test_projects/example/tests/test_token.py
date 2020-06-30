from datetime import time
from datetime import date
from datetime import datetime
from unittest import TestCase
from data_models.token import Token


class TestToken(TestCase):

    def __init__(self, methodName):
        super(TestToken, self).__init__(methodName=methodName)
        self.token = Token(i=0, startChar=0, endChar=0, depType='', depHead=0, depLeftEdge=0, depRightEdge=0, posType='', posFineType='', lemma='', text='')

    def setUp(self):
        super().setUp()

    def tearDown(self):
        super().tearDown()

    def test_token_test_get_hash_id(self):
        self.assertEqual(self.token.test_get_hash_id(), True)

    def test_token_test_to_data(self):
        self.assertEqual(self.token.test_to_data(), True)

    def test_token_test_from_data(self):
        self.assertEqual(self.token.test_from_data(), True)
