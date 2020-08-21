from datetime import time
from datetime import date
from datetime import datetime
from unittest import TestCase

from data_models.article_page import ArticlePage


class TestArticlePage(TestCase):

    def __init__(self, methodName):
        super(TestArticlePage, self).__init__(methodName=methodName)
        self.articlePage = ArticlePage(articlePageId=0, url='', body='')

    def setUp(self):
        super().setUp()

    def tearDown(self):
        super().tearDown()

    def test_article_page_test_get_hash_id(self):
        self.assertEqual(self.articlePage.test_get_hash_id(), True)

    def test_article_page_test_to_data(self):
        self.assertEqual(self.articlePage.test_to_data(), True)

    def test_article_page_test_from_data(self):
        self.assertEqual(self.articlePage.test_from_data(), True)
