from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from common.utils import query_reverse

from apps.recipes.models import Recipe
from apps.inventories.models import Place

ITEM_URL = reverse('cart-list')


def cart_recipe(place, recipe, only_missing=False):
    """Return friendship detail accept url"""
    return query_reverse(
        'cart-add-recipe',
        query_kwargs={
            'place': place,
            'recipe': recipe,
            'only_missing': only_missing
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


class InventoryItemTests(APITestCase):
    fixtures = ['unit', 'product', 'dishes_dataset']

    def test_adding_an_item_that_does_not_exist_should_create_it(self):
        u_1 = sample_user_1()
        self.client.force_authenticate(user=u_1)

        res = self.client.post(
            ITEM_URL,
            data={
                'product': 'Leche',
                'quantity': 1,
                'unit': 'liter'
            },
            format='json'
        )

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertIsNotNone(res.data)
        items = u_1.profile.places.first().cart
        self.assertEqual(items.count(), 1)
        item = items.first()
        self.assertEqual(item.product.id, 1)
        self.assertEqual(item.quantity, 1)
        self.assertEqual(item.unit.short_name, 'L')

    def test_adding_a_item_that_exists_should_create_it(self):
        u_1 = sample_user_1()
        self.client.force_authenticate(user=u_1)

        _ = self.client.post(
            ITEM_URL,
            data={
                'product': 'Leche',
                'quantity': 1,
                'unit': 'liter'
            },
            format='json'
        )

        res = self.client.post(
            ITEM_URL,
            data={
                'product': 'Leche',
                'quantity': 1000,
                'unit': 'milliliter'
            },
            format='json'
        )

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertIsNotNone(res.data)
        items = u_1.profile.places.first().cart
        self.assertEqual(items.count(), 2)

    def test_adding_multiple_items_to_cart_should_create_them(self):
        u_1 = sample_user_1()
        self.client.force_authenticate(user=u_1)

        recipe = Recipe.objects.first()

        res = self.client.post(
            cart_recipe(1, recipe.id),
            format='json'
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        items = u_1.profile.places.first().cart
        self.assertEqual(items.count(), recipe.ingredients.count())

    def test_adding_multiple_items_to_cart_with_wrong_recipe_should_not_create_them(self):
        u_1 = sample_user_1()
        self.client.force_authenticate(user=u_1)

        res = self.client.post(
            cart_recipe(1, 2321321),
            format='json'
        )
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIsNotNone(res.data)
        self.assertEqual(u_1.profile.places.count(), 0)

