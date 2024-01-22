"""
Sample tests
"""

from django.test import SimpleTestCase

from app import calc


class CalTest(SimpleTestCase):
    def test_addition(self):

        res = calc.add(2, 5)
        self.assertEqual(res, 7)

    def test_sub(self):
        res = calc.sub(4, 2)

        self.assertEqual(res, 2)
