"""Test for recipe api"""

from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe

from recipe.serializers import RecipeSerializer, RecipeDetailSerializer


RECIPES_URL = reverse('recipe:recipe-list')


def detail_url(recipe_id):
    """Create and return recipe detail url"""
    return reverse('recipe:recipe-detail', args=[recipe_id])


def create_recipe(user, **params):
    """Create test recipes"""

    defaults = dict(
        title='Sample title',
        time_min=21,
        price=Decimal('23.4'),
        desc='Sample description',
        link='http://test-recipe.com'
    )

    defaults.update(params)

    rec = Recipe.objects.create(user=user, **defaults)
    return rec


class PublicRecipeAPITests(TestCase):
    """Test requests without auth"""

    def setUp(self) -> None:
        self.client = APIClient()

    def test_auth_req(self):

        self.assertEqual(
            self.client.get(RECIPES_URL).status_code,
            status.HTTP_401_UNAUTHORIZED
        )


class PrivateRecipeAPITests(TestCase):
    """Test requests with AUth"""

    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'yser@example.com',
            'testpas12'
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_recipes(self):
        """Test retrieving a list of recipes"""

        create_recipe(self.user)
        create_recipe(self.user)

        res = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.all().order_by('-id')
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_recipelist_limited_to_user(self):
        """Test if listed recipes by user belong to them"""
        # create a second user to test if their recipe is not returned
        ouser = get_user_model().objects.create_user(
            'user@example.com',
            'testpas12'
        )

        create_recipe(ouser)
        create_recipe(self.user)

        res = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_get_recipe_detail(self):
        """Test get recipe detail"""
        recipe = create_recipe(user=self.user)

        url = detail_url(recipe.id)
        res = self.client.get(url)

        serializer = RecipeDetailSerializer(recipe)
        self.assertEqual(res.data, serializer.data)
