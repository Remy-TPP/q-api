from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


ITEM_URL = reverse('inventoryitems-list')
ITEMS_URL = reverse('inventoryitems-add-items')

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
    fixtures = ['unit', 'product']

    def test_adding_a_item_that_does_not_exist_should_create_it(self):
        u_1 = sample_user_1()
        self.client.force_authenticate(user=u_1)

        res = self.client.post(
            ITEM_URL,
            data={
                'product': 1,
                'amount': {
                    'quantity': 1,
                    'unit': 'liter'
                }
            },
            format='json'
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertIsNotNone(res.data)
        items = u_1.profile.places.first().inventory
        self.assertEqual(items.count(), 1)
        item = items.first()
        self.assertEqual(item.product.id, 1)
        self.assertEqual(item.amount.quantity, 1)
        self.assertEqual(item.amount.unit.short_name, 'L')

    def test_adding_a_item_that_exists_should_add_amount(self):
        u_1 = sample_user_1()
        self.client.force_authenticate(user=u_1)

        _ = self.client.post(
            ITEM_URL,
            data={
                'product': 1,
                'amount': {
                    'quantity': 1,
                    'unit': 'liter'
                }
            },
            format='json'
        )

        res = self.client.post(
            ITEM_URL,
            data={
                'product': 1,
                'amount': {
                    'quantity': 1000,
                    'unit': 'milliliter'
                }
            },
            format='json'
        )

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertIsNotNone(res.data)
        items = u_1.profile.places.first().inventory
        self.assertEqual(items.count(), 1)
        item = items.first()
        self.assertEqual(item.product.id, 1)
        self.assertEqual(item.amount.quantity, 2)
        self.assertEqual(item.amount.unit.short_name, 'L')

    def test_adding_multiple_items_should_create_them(self):
        u_1 = sample_user_1()
        self.client.force_authenticate(user=u_1)

        res = self.client.post(
            ITEMS_URL,
            data={
                "items": [
                    {
                        'product': 1,
                        'amount': {
                            'quantity': 1,
                            'unit': 'liter'
                        }
                    },
                    {
                        'product': 1,
                        'amount': {
                            'quantity': 2,
                            'unit': 'liter'
                        }
                    },
                    {
                        'product': 2,
                        'amount': {
                            'quantity': 1,
                            'unit': 'gram'
                        }
                    }
                ]
            },
            format='json'
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        items = u_1.profile.places.first().inventory
        self.assertEqual(items.count(), 2)
        item = items.first()
        self.assertEqual(item.product.id, 1)
        self.assertEqual(item.amount.quantity, 3)
        self.assertEqual(item.amount.unit.short_name, 'L')
        item = items.last()
        self.assertEqual(item.product.id, 2)
        self.assertEqual(item.amount.quantity, 1)
        self.assertEqual(item.amount.unit.short_name, 'g')

    def test_adding_multiple_items_with_one_wrong_should_not_create_them(self):
        u_1 = sample_user_1()
        self.client.force_authenticate(user=u_1)

        res = self.client.post(
            ITEMS_URL,
            data={
                "items": [
                    {
                        'product': 1,
                        'amount': {
                            'quantity': 1,
                            'unit': 'liter'
                        }
                    },
                    {
                        'product': 1,
                        'amount': {
                            'quantity': 2,
                            'unit': 'liter'
                        }
                    },
                    {
                        'product': 2,
                        'amount': {
                            'quantity': 1,
                            'unit': 'not real unit'
                        }
                    }
                ]
            },
            format='json'
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIsNotNone(res.data)
        self.assertEqual(u_1.profile.places.count(), 0)
