from unittest import TestCase
from hypergol.name_string import NameString


class TestNameString(TestCase):

    def test_name_string_has_correct_properties(self):
        ns = NameString(name='TestClass')
        self.assertEqual(ns.asSnake, 'test_class')
        self.assertEqual(ns.asClass, 'TestClass')
        self.assertEqual(ns.asVariable, 'testClass')
        self.assertEqual(ns.asPluralVariable, 'testClasses')

    def test_name_string_returns_correct_plural(self):
        ns = NameString(name='BigCity', plural='BigCities')
        self.assertEqual(ns.asPluralVariable, 'bigCities')
        self.assertEqual(ns.asPluralSnake, 'big_cities')
