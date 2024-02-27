"""Tests for ingredients api"""

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingredient

from recipe.serializers import IngredientSerializer


INGR_URL = reverse('recipe:ingredient-list')


def detail_url(ingr_id):
    """create and return ingredient detail url"""
    return reverse('recipe:ingredient-detail', args=[ingr_id])


def create_user(email='user@example.com', password='testpas123'):
    """Utility to create user"""
    return get_user_model().objects.create(
        email=email,
        password=password
    )


class PublicIngredientsApiTests(TestCase):
    """Tests unauth Ingredients api"""

    def setUp(self) -> None:
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is required for retrieving ingredients"""
        res = self.client.get(INGR_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngrApiTest(TestCase):
    """Test authorized api requests"""

    def setUp(self) -> None:
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve(self):
        """Test ingr retrieval"""

        Ingredient.objects.create(user=self.user, name='Tulsi')
        Ingredient.objects.create(user=self.user, name='Rice')

        res = self.client.get(INGR_URL)

        ings = Ingredient.objects.all().order_by('-name')
        serializer = IngredientSerializer(ings, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_ingr_limited_to_user(self):
        """Test if list of ingredients is limited to auth user"""

        user1 = create_user(email='examp@exmap.com')
        Ingredient.objects.create(user=user1, name='Pepper')
        ingr = Ingredient.objects.create(user=self.user, name='Carrot')

        res = self.client.get(INGR_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], ingr.name)
        self.assertEqual(res.data[0]['id'], ingr.id)

    def test_update_ingredients(self):
        """Test if ingredients can be updated by user"""

        # create some ingredients to update
        ingr1 = Ingredient.objects.create(user=self.user, name='Coriander')

        pload = {'name': 'Cumin'}
        url = detail_url(ingr1.id)

        res = self.client.patch(url, pload)

        # self.user.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        ingr1.refresh_from_db()
        self.assertEqual(ingr1.name, pload['name'])

    def test_delete_ingredients(self):
        """Test if ingredients are removeable"""

        # create ingredient to remove
        ingr1 = Ingredient.objects.create(user=self.user, name='Mint')
        # test if ingredient was created
        ingrs = Ingredient.objects.filter(user=self.user)
        self.assertTrue(ingrs.exists())

        url = detail_url(ingr_id=ingr1.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

        ingrs = Ingredient.objects.filter(user=self.user)
        # test if the ingredients list is empty
        # and ingredient does not exist after delete
        self.assertFalse(ingrs.exists())
