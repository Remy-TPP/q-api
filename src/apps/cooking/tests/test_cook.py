from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from common.utils import query_reverse
from apps.inventories.models import Place
from apps.profiles.models import RecipeCooked
from apps.recipes.models import Recipe

COOKEDRECIPES = reverse('profile-my-recipes')

def recipecooked_url(recipecooked_id):
    """Return recipecooked detail url"""
    return reverse('recipecooked-detail', args=[recipecooked_id])


def cook_recipe(recipe_id, place_id):
    """Return friendship detail accept url"""
    return query_reverse(
        'cook-recipe',
        query_kwargs={
            'recipe_id': recipe_id,
            'place_id': place_id
        }
    )


users = {
    'user_1': {
        'email': 'test1@test.com',
        'username': 'soyTest1',
        'password': 'Test1pass123',
    }
}


def sample_user_1():
    return get_user_model().objects.get_or_create(
        username=users['user_1']['username'],
        email=users['user_1']['email'],
        password=users['user_1']['password'],
    )[0]


class CookingTest(APITestCase):
    fixtures = ['unit.json', 'product.json', 'cooking_tests.json']

    def setUp(self):
        # create a sample profile with a place
        u_1 = sample_user_1()

        place = Place.objects.get(
            id=1
        )

        place.members.add(u_1.profile.id)

    def test_cook_without_recipe_id(self):
        """Test when cook without passing recipe_id must return 400 Bad Request."""
        u_1 = sample_user_1()
        place = Place.objects.get(id=1)

        self.client.force_authenticate(user=u_1)

        res = self.client.post(
            query_reverse(
                'cook-recipe',
                query_kwargs={
                    'place_id': place.id
                }
            )
        )

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cook_with_big_inventory(self):
        """Test when cook a recipe with more inventoryitems' amount
        than ingredients' amount, must reduce the amount and maintain the inventoryitems."""
        u_1 = sample_user_1()
        recipe = Recipe.objects.get(id=1)
        place = Place.objects.get(id=1)

        self.client.force_authenticate(user=u_1)

        res = self.client.post(
            cook_recipe(recipe.id, place.id)
        )

        # id=1: 1 L leche - 500 mL leche = 0.5 L leche
        # id=2: 1 kg cafe - 500 g cafe = 0.5 kg cafe
        # id=3: 500 mL leche descremada - 0 = 500 mL leche descremada
        items = place.inventory.all()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(items.get(id=1).amount.quantity, 0.5)
        self.assertEqual(items.get(id=1).amount.unit.name, 'liter')
        self.assertEqual(items.get(id=2).amount.quantity, 0.5)
        self.assertEqual(items.get(id=2).amount.unit.name, 'kilogram')
        self.assertEqual(items.get(id=3).amount.quantity, 500)
        self.assertEqual(items.get(id=3).amount.unit.name, 'milliliter')

    def test_cook_with_small_inventory(self):
        """Test when cook a recipe with equal inventoryitems' amount
        than ingredients' amount, must delete the inventoryitems."""
        u_1 = sample_user_1()
        recipe = Recipe.objects.get(id=2)
        place = Place.objects.get(id=1)

        self.client.force_authenticate(user=u_1)

        res = self.client.post(
            cook_recipe(recipe.id, place.id)
        )

        # id=1: 1l leche - 0 = 1l leche
        # id=2: 1kg cafe - 500g cafe = 0.5kg cafe
        # id=3: 500ml leche descremada - 0.5l leche descremada = 500ml leche descremada
        items = place.inventory.all()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(items), 2)
        self.assertEqual(items.get(id=1).amount.quantity, 1)
        self.assertEqual(items.get(id=1).amount.unit.name, 'liter')
        self.assertEqual(items.get(id=2).amount.quantity, 0.5)
        self.assertEqual(items.get(id=2).amount.unit.name, 'kilogram')

    def test_cook_with_valid_score(self):
        """Test when cook a recipe passing a valid score, must return 200."""
        u_1 = sample_user_1()
        recipe = Recipe.objects.get(id=1)
        place = Place.objects.get(id=1)

        self.client.force_authenticate(user=u_1)

        res = self.client.post(
            cook_recipe(recipe.id, place.id),
            data={
                'score': 10,
            }
        )

        recipe_cooked = RecipeCooked.objects.get(profile=u_1.profile, recipe=recipe)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(recipe_cooked.score, 10)
        self.assertIsNotNone(recipe_cooked.cooked_at)

    def test_cook_with_invalid_score(self):
        """Test when cook a recipe passing an invalid score, must return 400 Bad Request."""
        u_1 = sample_user_1()
        recipe = Recipe.objects.get(id=1)
        place = Place.objects.get(id=1)

        self.client.force_authenticate(user=u_1)

        res = self.client.post(
            cook_recipe(recipe.id, place.id),
            data={
                'score': 11,
            }
        )

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        with self.assertRaises(RecipeCooked.DoesNotExist):
            RecipeCooked.objects.get(profile=u_1.profile, recipe=recipe)

    def test_cook_can_update_score_later(self):
        """Test when cook a recipe without passing score, must return the id so can update later."""
        u_1 = sample_user_1()
        recipe = Recipe.objects.get(id=1)
        place = Place.objects.get(id=1)

        self.client.force_authenticate(user=u_1)

        res = self.client.post(
            cook_recipe(recipe.id, place.id)
        )

        recipe_cooked = RecipeCooked.objects.get(id=res.data.get('id'))

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIsNone(recipe_cooked.score)

        res = self.client.put(
            recipecooked_url(res.data.get('id')),
            data={
                'score': 9
            }
        )

        recipe_cooked = RecipeCooked.objects.get(id=res.data.get('id'))

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data.get('score'), 9)
        self.assertEqual(recipe_cooked.score, 9)

    def test_cook_can_get_my_recipes(self):
        """Test when having cooked a recipe, must return the recipes when asked."""
        u_1 = sample_user_1()
        recipe = Recipe.objects.get(id=1)
        place = Place.objects.get(id=1)

        self.client.force_authenticate(user=u_1)

        _ = self.client.post(
            cook_recipe(recipe.id, place.id),
            data={
                'score': 8
            }
        )

        res = self.client.get(
            COOKEDRECIPES,
        )

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
