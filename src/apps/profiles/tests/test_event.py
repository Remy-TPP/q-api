from datetime import datetime, timedelta
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.inventories.models import Place

EVENT_URL = reverse('event-list')


users = {
    'user_1': {
        'email': 'test1@test.com',
        'username': 'soyTest1',
        'password': 'Test1pass123',
    },
    'user_2': {
        'email': 'test2@test2.com',
        'username': 'soyTest2',
        'password': 'Test2pass123'
    }
}


def sample_user_1():
    return get_user_model().objects.get_or_create(
        username=users['user_1']['username'],
        email=users['user_1']['email'],
        password=users['user_1']['password'],
    )[0]


def sample_user_2():
    return get_user_model().objects.get_or_create(
        username=users['user_2']['username'],
        email=users['user_2']['email'],
        password=users['user_2']['password'],
    )[0]


class EventTests(APITestCase):
    tomorrow = datetime.now() + timedelta(days=1)
    day_after_tomorrow = tomorrow + timedelta(days=1)

    def setUp(self):
        u_1 = sample_user_1()
        u_2 = sample_user_2()
        u_1.profile.friends.add(u_2.profile)

        self.client.force_authenticate(user=u_1)

    def test_create_event_without_place(self):
        """Test when creating an event without having a place, must return error and dont create event"""
        payload = {
            'attendees': [sample_user_2().id],
            'name': 'Test name',
            'starting_datetime': self.tomorrow,
            'finishing_datetime': self.day_after_tomorrow,
        }

        res = self.client.post(
            EVENT_URL,
            payload
        )

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        p_1 = sample_user_1().profile
        self.assertEqual(p_1.events.count(), 0)
        self.assertEqual(p_1.hosted_events.count(), 0)

    def test_create_event_with_place(self):
        """Test when creating an event having a place, must create event"""
        p_1 = sample_user_1().profile

        Place.objects.create().members.add(p_1)

        payload = {
            'attendees': [sample_user_2().id],
            'name': 'Test name',
            'starting_datetime': self.tomorrow,
            'finishing_datetime': self.day_after_tomorrow,
        }

        res = self.client.post(
            EVENT_URL,
            payload
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(p_1.events.count(), 0)
        self.assertEqual(p_1.hosted_events.count(), 1)
