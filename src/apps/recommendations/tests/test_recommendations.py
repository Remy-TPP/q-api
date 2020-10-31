from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.recommendations.models import Recommendation
from apps.recipes.models import Recipe

MY_RECOMMENDATIONS = reverse('recommendations-my-recommendations')

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
    fixtures = ['recipes_for_recommendations.json']
    highest_score_rec = {}
    lowest_score_rec = {}

    def setUp(self):
        u_1 = sample_user_1()

        self.highest_score_rec = Recommendation.objects.create(
            profile=u_1.profile,
            recipe=Recipe.objects.get(id=1),
            score=4.12345
        )

        self.lowest_score_rec = Recommendation.objects.create(
            profile=u_1.profile,
            recipe=Recipe.objects.get(id=2),
            score=4.12344
        )

    def test_recommendations(self):
        """Test when get my recommendation should return in correct order."""
        u_1 = sample_user_1()

        self.client.force_authenticate(user=u_1)

        res = self.client.get(MY_RECOMMENDATIONS)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data.get('count'), 2)
        self.assertEqual(res.data.get('results')[0]['recipe']['id'], self.highest_score_rec.id)
        self.assertEqual(res.data.get('results')[1]['recipe']['id'], self.lowest_score_rec.id)
