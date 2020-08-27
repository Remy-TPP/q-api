from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .utils import get_data_in_qr_image, image_from_bytestring
from apps.inventories.models import Purchase


CREATE_PURCHASE_URL = reverse('purchase-create')


class PurchaseTests(APITestCase):
    fixtures = ['unit', 'product']

    def test_creating_purchase_with_no_items_fails(self):
        resp_1 = self.client.post(
            CREATE_PURCHASE_URL,
            format='json',
            data={}
        )
        resp_2 = self.client.post(
            CREATE_PURCHASE_URL,
            format='json',
            data={
                'items': []
            }
        )

        self.assertEqual(resp_1.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(resp_2.status_code, status.HTTP_400_BAD_REQUEST)

    # TODO: every so often (~20 attempts) OpenCV fails to identify data in QR image, and this test fails
    def test_qr_image_contains_url_to_created_purchase(self):
        resp = self.client.post(
            CREATE_PURCHASE_URL,
            format='json',
            data={
                'items': [
                    {'product': 'Leche Descremada', 'amount': {'quantity': 1, 'unit': 'liter'}},
                ]
            }
        )

        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(resp['Content-Type'], 'image/jpeg')
        # get data embedded in QR image from response and compare it to the URL of the new Purchase
        purchase_url = 'http://testserver' + reverse('purchase-detail', args=[Purchase.objects.last().id])
        qr_data = get_data_in_qr_image(image_from_bytestring(resp.content))
        self.assertEqual(qr_data, purchase_url)

    def test_creating_purchase_with_inexistent_products_fails(self):
        resp_1 = self.client.post(
            CREATE_PURCHASE_URL,
            format='json',
            data={
                'items': [
                    {'product': 'Leche cremada', 'amount': {'quantity': 1, 'unit': 'liter'}},
                ]
            }
        )
        resp_2 = self.client.post(
            CREATE_PURCHASE_URL,
            format='json',
            data={
                'items': [
                    {'product': 'Leche Descremada', 'amount': {'quantity': 1, 'unit': 'liter'}},
                    {'product': 'Café', 'amount': {'quantity': 250.0, 'unit': 'mL'}},
                    {'product': 'Producto inexistente', 'amount': {'quantity': 3, 'unit': 'cup'}},
                ]
            }
        )

        self.assertEqual(resp_1.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(resp_2.status_code, status.HTTP_400_BAD_REQUEST)

    def test_created_purchase_contains_correct_products_and_amounts(self):
        resp = self.client.post(
            CREATE_PURCHASE_URL,
            format='json',
            data={
                'items': [
                    {'product': 'Leche Descremada', 'amount': {'quantity': 1, 'unit': 'liter'}},
                    {'product': 'Café', 'amount': {'quantity': 250.0, 'unit': 'milliliter'}},
                    {'product': 'Harina 000', 'amount': {'quantity': 3, 'unit': 'cup'}},
                ]
            }
        )

        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Purchase.objects.last().items.count(), 3)
        items = Purchase.objects.last().items.all()
        self.assertEqual(items[0].product.name, 'Leche Descremada')
        self.assertEqual(items[0].amount.quantity, 1)
        self.assertEqual(items[0].amount.unit.short_name, 'L')
        self.assertEqual(items[1].product.name, 'Café')
        self.assertEqual(items[1].amount.quantity, 250.0)
        self.assertEqual(items[1].amount.unit.short_name, 'mL')
        self.assertEqual(items[2].product.name, 'Harina 000')
        self.assertEqual(items[2].amount.quantity, 3)
        self.assertEqual(items[2].amount.unit.name, 'cup')

    def test_creating_purchase_with_repeated_product_aggregates_it(self):
        resp_1 = self.client.post(
            CREATE_PURCHASE_URL,
            format='json',
            data={
                'items': [
                    {'product': 'Leche Descremada', 'amount': {'quantity': 1, 'unit': 'liter'}},
                    {'product': 'Café', 'amount': {'quantity': 250.0, 'unit': 'milliliter'}},
                    {'product': 'Leche Descremada', 'amount': {'quantity': 2, 'unit': 'liter'}},
                ]
            }
        )
        resp_2 = self.client.post(
            CREATE_PURCHASE_URL,
            format='json',
            data={
                'items': [
                    {'product': 'Leche Descremada', 'amount': {'quantity': 1, 'unit': 'liter'}},
                    {'product': 'Café', 'amount': {'quantity': 250.0, 'unit': 'milliliter'}},
                    {'product': 'Harina 000', 'amount': {'quantity': 2, 'unit': 'liter'}},
                    {'product': 'Café', 'amount': {'quantity': 10.0, 'unit': 'liter'}},
                    {'product': 'Leche Descremada', 'amount': {'quantity': 0.5, 'unit': 'liter'}},
                ]
            }
        )
        purchase_1, purchase_2 = Purchase.objects.all().order_by("created_at")

        self.assertEqual(resp_1.status_code, status.HTTP_201_CREATED)
        self.assertEqual(resp_2.status_code, status.HTTP_201_CREATED)
        self.assertEqual(purchase_1.items.count(), 2)
        items = purchase_1.items.all()
        self.assertEqual(items[0].product.name, 'Leche Descremada')
        self.assertEqual(items[0].amount.quantity, 3)
        self.assertEqual(items[0].amount.unit.short_name, 'L')
        self.assertEqual(items[1].product.name, 'Café')
        self.assertEqual(items[1].amount.quantity, 250.00)
        self.assertEqual(items[1].amount.unit.short_name, 'mL')
        self.assertEqual(purchase_2.items.count(), 3)
        items = purchase_2.items.all()
        self.assertEqual(items[0].product.name, 'Leche Descremada')
        self.assertEqual(items[0].amount.quantity, 1.5)
        self.assertEqual(items[0].amount.unit.short_name, 'L')
        self.assertEqual(items[1].product.name, 'Café')
        self.assertEqual(items[1].amount.quantity, 10250)
        self.assertEqual(items[1].amount.unit.short_name, 'mL')
        self.assertEqual(items[2].product.name, 'Harina 000')
        self.assertEqual(items[2].amount.quantity, 2)
        self.assertEqual(items[2].amount.unit.short_name, 'L')

    # TODO: not done yet
    # def test_purchase_creation_product_are_case_insensitive(self):
    #     resp = self.client.post(
    #         CREATE_PURCHASE_URL,
    #         format='json',
    #         data={
    #             'items': [
    #                 {'product': 'CAFÉ', 'amount': {'quantity': 250.0, 'unit': 'milliliter'}},
    #                 {'product': 'harina 000', 'amount': {'quantity': 3, 'unit': 'cup'}},
    #                 {'product': 'LECHE descremada', 'amount': {'quantity': 1, 'unit': 'liter'}},
    #             ]
    #         }
    #     )
    #
    #     self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
    #     self.assertEqual(Purchase.objects.last().items.count(), 3)
    #     items = Purchase.objects.last().items.all()
    #     self.assertEqual(items[0].product.name, 'Café')
    #     self.assertEqual(items[0].amount.quantity, 250.0)
    #     self.assertEqual(items[0].amount.unit.short_name, 'mL')
    #     self.assertEqual(items[1].product.name, 'Harina 000')
    #     self.assertEqual(items[1].amount.quantity, 3)
    #     self.assertEqual(items[1].amount.unit.name, 'cup')
    #     self.assertEqual(items[2].product.name, 'Leche Descremada')
    #     self.assertEqual(items[2].amount.quantity, 1)
    #     self.assertEqual(items[2].amount.unit.short_name, 'L')
