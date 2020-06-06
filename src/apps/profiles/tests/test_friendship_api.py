from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.profiles.models import FriendshipRequest, FriendshipStatus

FRIENDSHIP = reverse('friendshiprequest-list')

def detail_url_accept(id):
    """Return friendship detail accept url"""
    return reverse('friendship-accept', args=[id])

def detail_url_reject(id):
    """Return friendship detail reject url"""
    return reverse('friendship-reject', args=[id])

users = {
    'user_1': {
        'email': 'test@test.com',
        'username': 'soyTest',
        'password': 'Testpass123',
    },
    'user_2': {
        'email': 'test2@test2.com',
        'username': 'soyTest2',
        'password': 'Test2pass123'
    }
}

def sample_user_1():
    return get_user_model().objects.create_user(
        username=users['user_1']['username'],
        email=users['user_1']['email'],
        password=users['user_1']['password'],
    )

def sample_user_2():
    return get_user_model().objects.create_user(
        username=users['user_2']['username'],
        email=users['user_2']['email'],
        password=users['user_2']['password'],
    )


class FriendshipTests(TestCase):
    fixtures = ['friendshipstatus_data.json']

    def setUp(self):
        self.client = APIClient()

        # create a sample friendship request
        FriendshipRequest.objects.create(
            profile_requesting=sample_user_1().profile,
            profile_requested=sample_user_2().profile,
            status=FriendshipStatus.objects.get(name='REQUESTED')
        )

    def test_post_friendship(self):
        """Test when """
        #u_1 = sample_user_1()