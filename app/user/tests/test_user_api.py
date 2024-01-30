"""
Tests for the user API
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status


CREATE_USER_URL = reverse('user:create')
TOKEN_USER_URL = reverse('user:token')
ME_URL = reverse('user:me')


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

    def test_create_token_for_user(self):
        """Test generating token for valid credentials"""

        user_det = {
            'name': 'testuser',
            'email': 'test@example.com',
            'password': 'test-pwd123'
        }

        create_user(**user_det)

        payload = {
            'email': user_det['email'],
            'password': user_det['password']
        }

        res = self.client.post(TOKEN_USER_URL, payload)

        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        # change password to see if the generation returns error if the
        # credentials are invalid

        # wrong one
        payload['password'] = 'test123'

        res = self.client.post(TOKEN_USER_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        # test if a blank password works

        payload['password'] = ''

        res = self.client.post(TOKEN_USER_URL, payload)
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_user_unauth(self):
        """Test if authentication is prompted for users who aren't"""

        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserApiTests(TestCase):
    """Test api requests that use auth"""
    def setUp(self) -> None:
        self.user = create_user(
            email='test@example.com',
            password='test123',
            name='Test user'
        )

        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieval(self):
        """Test retrieving profile for loggedin user"""
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {
            'name': self.user.name,
            'email': self.user.email,
        })

    def test_post_not_allowed(self):
        """Test if POST methods are not allowed for me endpoint"""
        res = self.client.post(ME_URL, {})

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile(self):
        """Test updation of user profile"""

        payload = {'name': 'Updated name', 'password': 'test$123'}

        res = self.client.patch(ME_URL, payload)

        self.user.refresh_from_db()
        self.assertEqual(self.user.name, payload['name'])
        self.assertTrue(self.user.check_password(payload['password']))
        self.assertEqual(res.status_code, status.HTTP_200_OK)