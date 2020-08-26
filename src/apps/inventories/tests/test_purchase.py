from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from common.utils import get_data_in_qr_image, image_from_bytestring
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
        purchase_url = 'http://testserver' + reverse('purchase-detail', args=[Purchase.objects.last().id])

        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(resp['Content-Type'], 'image/jpeg')
        # get data embedded in QR image from response and compare it to the URL of the new Purchase
        qr_data = get_data_in_qr_image(image_from_bytestring(resp.content))
        self.assertEqual(qr_data, purchase_url)
