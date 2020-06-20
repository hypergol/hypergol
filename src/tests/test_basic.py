from unittest import TestCase

from hypergol.example import Example


class HypergolTestCase(TestCase):

    # NOTE(Rhys): test setup goes here
    # NOTE(Rhys): Folder sturcturing of tests not yet in place
    def setUp(self):
        super().setUp()
        self.example = Example()


class ExampleTestCasse(HypergolTestCase):

    def test_basic(self):
        pass

    def test_example(self):
        self.assertEqual(self.example.add(7, 5), 12)
