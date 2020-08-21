from datetime import time
from datetime import date
from datetime import datetime
from unittest import TestCase

from data_models.labelled_article import LabelledArticle


class TestLabelledArticle(TestCase):

    def __init__(self, methodName):
        super(TestLabelledArticle, self).__init__(methodName=methodName)
        self.labelledArticle = LabelledArticle(labelledArticleId=0, articleId=0, labelId=0)

    def setUp(self):
        super().setUp()

    def tearDown(self):
        super().tearDown()

    def test_labelled_article_test_get_hash_id(self):
        self.assertEqual(self.labelledArticle.test_get_hash_id(), True)

    def test_labelled_article_test_to_data(self):
        self.assertEqual(self.labelledArticle.test_to_data(), True)

    def test_labelled_article_test_from_data(self):
        self.assertEqual(self.labelledArticle.test_from_data(), True)
