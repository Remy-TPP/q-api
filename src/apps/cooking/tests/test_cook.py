from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from common.utils import query_reverse
from apps.inventories.models import Place, Inventory
from apps.recipes.models import Recipe


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

        place = Place.objects.create(
            id=1,
            name="Mi casa",
            inventory=Inventory.objects.first()  # there is only one
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
        items = place.inventory.items.all()

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
        items = place.inventory.items.all()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(items), 2)
        self.assertEqual(items.get(id=1).amount.quantity, 1)
        self.assertEqual(items.get(id=1).amount.unit.name, 'liter')
        self.assertEqual(items.get(id=2).amount.quantity, 0.5)
        self.assertEqual(items.get(id=2).amount.unit.name, 'kilogram')
