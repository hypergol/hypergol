from datetime import time
from datetime import date
from datetime import datetime
from unittest import TestCase

from data_models.article_text import ArticleText


class TestArticleText(TestCase):

    def __init__(self, methodName):
        super(TestArticleText, self).__init__(methodName=methodName)
        self.articleText = ArticleText(articleTextId=0, publishDate=datetime.now(), title='', text='', url='')

    def setUp(self):
        super().setUp()

    def tearDown(self):
        super().tearDown()

    def test_article_text_test_get_hash_id(self):
        self.assertEqual(self.articleText.test_get_hash_id(), True)

    def test_article_text_test_to_data(self):
        self.assertEqual(self.articleText.test_to_data(), True)

    def test_article_text_test_from_data(self):
        self.assertEqual(self.articleText.test_from_data(), True)
