"""
Sample tests
"""

from django.test import SimpleTestCase

from app import cacl


class CalTest(SimpleTestCase):
    def test_addition(self):

        res = cacl.add(2, 5)
        self.assertEqual(res, 7)
    
    def test_sub(self):
        res = cacl.sub(4,2)

        self.assertEqual(res, 2)