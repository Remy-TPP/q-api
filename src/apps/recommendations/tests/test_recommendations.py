from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from common.utils import query_reverse

from apps.recommendations.models import Recommendation
from apps.recipes.models import Recipe
from apps.inventories.models import Place

MY_RECOMMENDATIONS = reverse('recommendations-my-recommendations')


def my_recommendations(place, all_ingredients):
    """Return recommendation url"""
    return query_reverse(
        'recommendations-my-recommendations',
        query_kwargs={
            'place': place,
            'all_ingredients': all_ingredients
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


class RecommendationTest(APITestCase):
    fixtures = ['unit', 'product', 'recipes_for_recommendations.json']
    highest_score_rec = {}
    lowest_score_rec = {}

    def setUp(self):
        u_1 = sample_user_1()
        place = Place.objects.get(id=1)
        place.members.add(u_1.profile.id)

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

    def test_recommendations_without_all_ingredients(self):
        """Test when get my recommendation should return in correct order."""
        u_1 = sample_user_1()

        self.client.force_authenticate(user=u_1)

        res = self.client.get(MY_RECOMMENDATIONS)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data.get('count'), 2)
        self.assertEqual(int(res.data.get('results')[0]['recipe_id']), self.highest_score_rec.recipe.id)
        self.assertEqual(int(res.data.get('results')[1]['recipe_id']), self.lowest_score_rec.recipe.id)

    def test_recommendations_with_all_ingredients(self):
        """Test when get my recommendation with all ingredients should return only one."""
        u_1 = sample_user_1()
        place = Place.objects.get(id=1)

        self.client.force_authenticate(user=u_1)

        res = self.client.get(
            my_recommendations(place.id, True)
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data.get('count'), 1)
        self.assertEqual(int(res.data.get('results')[0]['recipe_id']), self.highest_score_rec.recipe.id)
