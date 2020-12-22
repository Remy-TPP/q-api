import json

from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from common.utils import query_reverse
from apps.inventories.models import Place
from apps.recipes.models import Recipe, Interaction


def cook_recipe_url(recipe_id, place_id):
    """Return cook recipe url"""
    return query_reverse(
        'cook-recipe',
        query_kwargs={
            'recipe_id': recipe_id,
            'place_id': place_id
        }
    )


def sample_user_1():
    return get_user_model().objects.get_or_create(
        email='test1@test.com',
        username='soyTest1',
        password='Test1pass123',
    )[0]


class CookingTest(APITestCase):
    fixtures = ['unit', 'product', 'cooking_tests']

    def setUp(self):
        self.u_1 = sample_user_1()
        self.place = Place.objects.get(id=1)
        self.place.members.add(self.u_1.profile.id)

    def test_cooking_without_recipe_id_fails(self):
        """Trying to cook without passing recipe_id returns error 400."""
        self.client.force_authenticate(user=self.u_1)

        resp = self.client.post(
            query_reverse(
                'cook-recipe',
                query_kwargs={
                    'place_id': self.place.id,
                }
            )
        )

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cooking_with_surplus_inventory(self):
        """
        Cooking a recipe with more inventoryitems amounts than ingredient amounts,
        should reduce the inventoryitems amounts.
        """
        recipe_1 = Recipe.objects.get(id=1)
        self.client.force_authenticate(user=self.u_1)

        resp = self.client.post(
            cook_recipe_url(recipe_id=recipe_1.id, place_id=self.place.id)
        )

        # id=1: 1 L leche - 500 mL leche = 0.5 L leche
        # id=2: 1 kg cafe - 500 g cafe = 0.5 kg cafe
        # id=3: 500 mL leche descremada - 0 = 500 mL leche descremada
        items = self.place.inventory.all()
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(items.get(id=1).quantity, 0.5)
        self.assertEqual(items.get(id=1).unit.name, 'liter')
        self.assertEqual(items.get(id=2).quantity, 0.5)
        self.assertEqual(items.get(id=2).unit.name, 'kilogram')
        self.assertEqual(items.get(id=3).quantity, 500)
        self.assertEqual(items.get(id=3).unit.name, 'milliliter')

    def test_cooking_with_exact_inventory_for_ingredient(self):
        """
        Cooking a recipe where an ingredient's amount is the same
        as the amount of that inventoryitem should remove the inventoryitem.
        """
        recipe_2 = Recipe.objects.get(id=2)
        self.client.force_authenticate(user=self.u_1)

        resp = self.client.post(
            cook_recipe_url(recipe_id=recipe_2.id, place_id=self.place.id)
        )

        # id=1: 1l leche - 0 = 1l leche
        # id=2: 1kg cafe - 500g cafe = 0.5kg cafe
        # id=3: 500ml leche descremada - 0.5l leche descremada = 0
        items = self.place.inventory.all()
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(items), 2)
        self.assertEqual(items.get(id=1).quantity, 1)
        self.assertEqual(items.get(id=1).unit.name, 'liter')
        self.assertEqual(items.get(id=2).quantity, 0.5)
        self.assertEqual(items.get(id=2).unit.name, 'kilogram')

    def test_cooking_with_valid_rating(self):
        """Cooking a recipe and passing a valid rating should return 200."""
        recipe_1 = Recipe.objects.get(id=1)
        self.client.force_authenticate(user=self.u_1)

        resp = self.client.post(
            cook_recipe_url(recipe_id=recipe_1.id, place_id=self.place.id),
            data=json.dumps({'rating': 10}),
            content_type='application/json',
        )

        interaction = Interaction.objects.get(profile=self.u_1.profile, recipe=recipe_1)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(interaction.rating, 10)
        self.assertEqual(len(interaction.cooked_at), 1)

    def test_cooking_with_score_too_big(self):
        """
        Trying to cook while passing an too-large score
        should return 400 and not cook.
        """
        recipe_1 = Recipe.objects.get(id=1)
        self.client.force_authenticate(user=self.u_1)

        resp = self.client.post(
            cook_recipe_url(recipe_id=recipe_1.id, place_id=self.place.id),
            data=json.dumps({'rating': 11}),
            content_type='application/json',
        )

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        with self.assertRaises(Interaction.DoesNotExist):
            Interaction.objects.get(profile=self.u_1.profile, recipe=recipe_1)

    def test_cooking_without_rating(self):
        """
        Cooking a recipe without rating should leave no rating and return 200.
        Rating can be added after.
        """
        recipe_1 = Recipe.objects.get(id=1)
        self.client.force_authenticate(user=self.u_1)

        resp1 = self.client.post(
            cook_recipe_url(recipe_id=recipe_1.id, place_id=self.place.id)
        )

        interaction1 = Interaction.objects.get(id=resp1.data.get('id'))
        self.assertEqual(resp1.status_code, status.HTTP_200_OK)
        self.assertIsNone(interaction1.rating)

        resp2 = self.client.put(
            reverse('rate-recipe'),
            data={
                'recipe': recipe_1.id,
                'rating': 9,
            },
        )

        interaction2 = Interaction.objects.get(id=resp2.data.get('id'))
        self.assertEqual(resp2.status_code, status.HTTP_200_OK)
        self.assertEqual(float(resp2.data.get('rating')), 9)
        self.assertEqual(interaction2.rating, 9)

    def test_can_get_recipes_cooked_by_user(self):
        """Cooking recipe means it will be included when asking for cooked recipes by user."""
        recipe_1 = Recipe.objects.get(id=1)
        self.client.force_authenticate(user=self.u_1)

        self.client.post(
            cook_recipe_url(recipe_id=recipe_1.id, place_id=self.place.id),
            data={'score': 8}
        )

        resp = self.client.get(reverse('profile-cooked-recipes'))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data.get('count'), 1)
        self.assertEqual(len(resp.data.get('results')), 1)
