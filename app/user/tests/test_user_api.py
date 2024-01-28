"""
Tests for the user API
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status


CREATE_USER_URL = reverse('user:create')


def create_user(**params):
    """Create and return new user"""
    return get_user_model().objects.create_user(**params)


class PublicUserApiTests(TestCase):
    """Tests public api features"""

    def setUp(self):
        self.client = APIClient()

    def test_create_user_success(self):
        """Test if creating a user is happening"""

        payload = {
            'email': 'test@example.com',
            'password': 'testpass123',
            'name': 'Test user'
        }

        # Create user via api request
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        user = get_user_model().objects.get(email=payload['email'])
        self.assertTrue(user.check_password(payload['password']))
        # check if the password is not returned in response
        self.assertNotIn('password', res.data)

    def test_exists_user_error(self):
        """Tests if the api rejects creating dupes"""
        payload = {
            'email': 'test@example.com',
            'password': 'testpass123',
            'name': 'Test user'
        }

        create_user(**payload)
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_pwd_validations(self):
        payload = {
            'email': 'test@example.com',
            'password': '123',
            'name': 'Test user'
        }
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()

        self.assertFalse(user_exists)
