from unittest import mock

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from apps.profiles.models import Profile
from apps.inventories.models import Place
from common.utils import query_reverse
from .mock_rs_responses import mock_rs_responses


def recommend_recipes_url(place_id=None, need_all_ingredients=None):
    return query_reverse(
        'recommendations-recommend-me',
        query_kwargs={
            'place_id': place_id,
            'need_all_ingredients': need_all_ingredients,
        }
    )


def sample_user_1():
    return get_user_model().objects.get_or_create(
        email='test1@test.com',
        username='soyTest1',
        password='Test1pass123',
    )[0]


class RecommendationTest(APITestCase):
    fixtures = ['unit', 'product', 'recipes_for_recommendations']

    def setUp(self):
        self.u_1 = sample_user_1()
        self.mock_get_patcher = mock.patch('apps.recommendations.services.requests.get')
        self.mock_get = self.mock_get_patcher.start()

    def tearDown(self):
        Place.objects.all().delete()
        self.mock_get_patcher.stop()

    def _set_mock_rs_response(self, response, status_code=status.HTTP_200_OK):
        self.mock_get.return_value = mock.Mock()
        self.mock_get.return_value.status_code = status_code
        self.mock_get.return_value.json.return_value = response

    def test_get_sorted_recommendations(self):
        """Test should return recipes sorted by rating."""
        self._set_mock_rs_response(response=mock_rs_responses[1])
        self.client.force_authenticate(user=self.u_1)

        resp = self.client.get(
            recommend_recipes_url()
        )

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data.get('count'), 2)
        recommendations = resp.data.get('results')
        self.assertEqual(recommendations[0].get('recipe').get('id'), 2)
        self.assertEqual(float(recommendations[0].get('rating')), 3.7)
        self.assertEqual(recommendations[0].get('rating_is_real'), False)
        self.assertEqual(recommendations[1].get('recipe').get('id'), 1)
        self.assertEqual(float(recommendations[1].get('rating')), 3.4)
        self.assertEqual(recommendations[1].get('rating_is_real'), True)

    def test_getting_filtered_recommendations_without_place_fails(self):
        """
        Asking for filtered (need_all_ingredients) recommendations while
        not having a place should return 400.
        """
        self._set_mock_rs_response(response=mock_rs_responses[1])
        self.client.force_authenticate(user=self.u_1)

        resp = self.client.get(
            recommend_recipes_url(need_all_ingredients=True)
        )

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_filtered_recommendations_with_ingredients(self):
        """Should return only recipes the user can make with what's in their inventory."""
        Place.objects.first().members.add(Profile.objects.get_or_create(user=self.u_1)[0])
        self._set_mock_rs_response(response=mock_rs_responses[1])
        self.client.force_authenticate(user=self.u_1)

        resp = self.client.get(
            recommend_recipes_url(need_all_ingredients=True)
        )

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data.get('count'), 1)
        recommendations = resp.data.get('results')
        self.assertEqual(recommendations[0].get('recipe').get('id'), 1)
        self.assertEqual(float(recommendations[0].get('rating')), 3.4)
        self.assertEqual(recommendations[0].get('rating_is_real'), True)

    def test_get_filtered_recommendations_with_amounts(self):
        """Leave out recipes for which user has all ingredients but not enough of any."""
        Place.objects.first().members.add(Profile.objects.get_or_create(user=self.u_1)[0])
        self._set_mock_rs_response(response=mock_rs_responses[2])
        self.client.force_authenticate(user=self.u_1)

        resp = self.client.get(
            recommend_recipes_url(need_all_ingredients=True)
        )

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data.get('count'), 1)
        recommendations = resp.data.get('results')
        self.assertEqual(recommendations[0].get('recipe').get('id'), 1)
        self.assertEqual(float(recommendations[0].get('rating')), 3.4)
        self.assertEqual(recommendations[0].get('rating_is_real'), True)
