"""
Tests for tags api
"""
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient as ApiClient

from core.models import Tag

from recipe.serializers import TagSerializer

TAGS_URL = reverse('recipe:tag-list')


def detail_url(tag_id):
    """create and return tag detail url"""
    return reverse('recipe:tag-detail', args=[tag_id])


def create_user(email='user@example.com', password='testpas123'):
    """Utility to create user"""
    return get_user_model().objects.create(
        email=email,
        password=password
    )


class PublicTagsApiTests(TestCase):
    """Test unauthenticated tags api requests"""

    def setUp(self) -> None:
        self.client = ApiClient()

    def test_auth_required(self):
        """Test auth is required to retrieve tags"""
        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsApiTests(TestCase):
    """Test Authenticated api requests for tags"""

    def setUp(self) -> None:
        self.user = create_user()
        self.client = ApiClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_tags(self):
        """Test retreiving list of tags"""

        Tag.objects.create(user=self.user, name='Chinese')
        Tag.objects.create(user=self.user, name='Vegan')

        res = self.client.get(TAGS_URL)

        tags = Tag.objects.all().order_by('-name')
        szer = TagSerializer(tags, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, szer.data)

    def test_tags_limited_to_user(self):
        """Test if displayed tags were created by corresponding user"""

        user2 = create_user('user2@exapds.com', password='apsdf123')
        Tag.objects.create(user=user2, name='Fruity')
        tag = Tag.objects.create(user=self.user, name='Chinese')

        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], tag.name)
        self.assertEqual(res.data[0]['id'], tag.id)

    def test_update_tags(self):
        """Test if tags can be updated by user"""

        # create some tags to update
        tag1 = Tag.objects.create(user=self.user, name='Chinese')

        pload = {'name': 'Japanese'}
        url = detail_url(tag1.id)

        res = self.client.patch(url, pload)

        # self.user.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        tag1.refresh_from_db()
        self.assertEqual(tag1.name, pload['name'])

    def test_delete_tags(self):
        """Test if tags are removeable"""

        # create tag to remove
        tag1 = Tag.objects.create(user=self.user, name='Chinese')
        # test if tag was created
        tags = Tag.objects.filter(user=self.user)
        self.assertTrue(tags.exists())

        url = detail_url(tag_id=tag1.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

        tags = Tag.objects.filter(user=self.user)
        # test if the tags list is empty and tag does not exist after delete
        self.assertFalse(tags.exists())
