from datetime import time
from datetime import date
from datetime import datetime
from unittest import TestCase
from data_models.article import Article


class TestArticle(TestCase):

    def __init__(self, methodName):
        super(TestArticle, self).__init__(methodName=methodName)
        self.article = Article(articleId=0, url='', title='', text='')

    def setUp(self):
        super().setUp()

    def tearDown(self):
        super().tearDown()

    def test_article_test_get_hash_id(self):
        self.assertEqual(self.article.test_get_hash_id(), True)

    def test_article_test_to_data(self):
        self.assertEqual(self.article.test_to_data(), True)

    def test_article_test_from_data(self):
        self.assertEqual(self.article.test_from_data(), True)
