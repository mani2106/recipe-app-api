"""Test for recipe api"""

from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe, Tag

from recipe.serializers import RecipeSerializer, RecipeDetailSerializer


RECIPES_URL = reverse('recipe:recipe-list')


def detail_url(recipe_id):
    """Create and return recipe detail url"""
    return reverse('recipe:recipe-detail', args=[recipe_id])


def create_user(**params):
    """Create and return a new user"""
    return get_user_model().objects.create_user(**params)


def create_recipe(user, **params):
    """Create test recipes"""

    defaults = dict(
        title='Sample title',
        time_minutes=21,
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
        self.user = create_user(email='user@example.com', password='testpass')
        self.client.force_authenticate(self.user)

    def test_retrieve_recipes(self):
        """Test retrieving a list of recipes"""

        create_recipe(user=self.user)
        create_recipe(user=self.user)

        res = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.all().order_by('-id')
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_recipelist_limited_to_user(self):
        """Test if listed recipes by user belong to them"""
        # create a second user to test if their recipe is not returned
        ouser = create_user(
            email='user1@example.com',
            password='testpas12'
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

    def test_create_recipe(self):
        """Test creating a recipe via api"""
        payload = dict(
            title='Sample recipe',
            time_minutes=20,
            price=Decimal('2.55'),
            desc='Sample Recipe to test',
            link='link'
        )

        res = self.client.post(RECIPES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        rec = Recipe.objects.get(id=res.data['id'])

        for k, v in payload.items():
            self.assertEqual(getattr(rec, k), v)

        self.assertEqual(rec.user, self.user)

    def test_partial_update(self):
        """Test partial update of a recipe"""
        original_link = 'https://recipe.com/recipe.pdf'
        recipe = create_recipe(
            user=self.user,
            title='Sample recipe',
            link=original_link
        )

        payload = dict(title='New title')
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()
        self.assertEqual(recipe.title, payload['title'])
        self.assertEqual(recipe.link, original_link)
        self.assertEqual(recipe.user, self.user)

    def test_full_update(self):
        """Test full update for a recipe"""
        original_link = 'https://recipe.com/recipe.pdf'
        recipe = create_recipe(
            user=self.user,
            title='Sample recipe',
            link=original_link,
            desc='Sample desc'
        )

        payload = dict(
            title='New sample title',
            link='https://recipe-site.com/recipe.pdf',
            time_minutes=100,
            desc='Sample_desc',
            price=Decimal('200.2')
        )
        url = detail_url(recipe.id)
        res = self.client.put(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()

        for k, v in payload.items():
            self.assertEqual(getattr(recipe, k), v)
        self.assertEqual(recipe.user, self.user)

    def test_update_user_returns_err(self):
        """Test changing the recipe user results in an error"""
        new_user = create_user(email='user2@example.com', password='test123')
        recipe = create_recipe(user=self.user)

        payload = dict(user=new_user.id)
        url = detail_url(recipe.id)
        self.client.patch(url, payload)

        recipe.refresh_from_db()
        self.assertEqual(recipe.user, self.user)

    def test_delete_recipe(self):
        """Test deleting recipe"""

        recipe = create_recipe(user=self.user)

        url = detail_url(recipe.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Recipe.objects.filter(id=recipe.id).exists())

    def test_mod_other_user_recipe(self):
        """Test trying to delete another users recipes"""
        new_user = create_user(email='user23@example.com', password='test1233')
        recipe = create_recipe(user=new_user)

        url = detail_url(recipe.id)

        # deleting new_user's recipe with self.user id
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Recipe.objects.filter(id=recipe.id).exists())

    def test_create_recipe_with_tags(self):
        """Test if we can create recipe with tags"""
        payload = dict(
            title='Prawn curry',
            time_minutes=21,
            price=Decimal('23.4'),
            desc='Sample description',
            tags=[dict(name='Thai'), dict(name='Dinner')]
        )

        res = self.client.post(RECIPES_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)
        recipe = recipes[0]
        self.assertEqual(recipe.tags.count(), 2)

        for tag in payload['tags']:
            exists = recipe.tags.filter(
                name=tag['name'],
                user=self.user
            ).exists()
            self.assertTrue(exists)

    def test_create_recipe_with_tags_existing(self):
        tag_ind = Tag.objects.create(user=self.user, name='Indian')
        payload = dict(
            title='Pongal',
            time_minutes=20,
            price=Decimal('44.2'),
            tags=[dict(name='Indian'), dict(name='Breakfast')]
        )

        res = self.client.post(RECIPES_URL, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)
        recipe = recipes[0]
        self.assertEqual(recipe.tags.count(), 2)

        self.assertIn(tag_ind, recipe.tags.all())

        for tag in payload['tags']:
            exists = recipe.tags.filter(
                name=tag['name'],
                user=self.user
            ).exists()
            self.assertTrue(exists)
