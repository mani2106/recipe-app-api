"""
Tests for models
"""
from decimal import Decimal

from django.test import TestCase
from django.contrib.auth import get_user_model

from core import models


class ModelTests(TestCase):
    """Test db models"""

    def test_create_user_success(self):
        """Test success case for creating user"""
        email = "test@example.com"
        pwd = "passwd@123"

        user = get_user_model().objects.create_user(
            email=email,
            password=pwd
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(pwd))

    def test_new_user_email_norm(self):
        """Test if a new user's email gets normalized"""

        sample_emails = [
            ['text1@EXAMPLE.com', 'text1@example.com'],
            ['Rext1@EXAMPLE.COM', 'Rext1@example.com'],
            ['texT2@EXAMPLE.COM', 'texT2@example.com'],
            ['texT3@example.COM', 'texT3@example.com'],
            ['test@example.COM', 'test@example.com'],
        ]

        for em, exp in sample_emails:
            user = get_user_model().objects.create_user(em, 'sample123')
            self.assertEqual(user.email, exp)

    def test_if_empty_email_raises_error_onreg(self):
        """Test if empty email on registration raises error"""

        with self.assertRaises(ValueError):
            get_user_model().objects.create_user('', 'passwd')

    def test_create_super_user(self):
        """Test creating super user"""

        user = get_user_model().objects.create_superuser(
            'test1@example.com',
            'passwd'
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_create_recipe(self):
        """Test creating a recipe"""

        email = 'test@example.com'
        pwd = 'passwd@123'

        user = get_user_model().objects.create_user(
            email=email,
            password=pwd
        )

        recipe = models.Recipe.objects.create(
            user=user,
            title='Sample recipe',
            time_min=5,
            price=Decimal('6.3'),
            desc='Sample recipe'
        )

        self.assertEqual(str(recipe), recipe.title)
