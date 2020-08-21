from datetime import datetime, timedelta
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.inventories.utils import get_place_or_default
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
    },
    'user_3': {
        'email': 'test3@test3.com',
        'username': 'soyTest3',
        'password': 'Test3pass123'
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


def sample_user_3():
    return get_user_model().objects.get_or_create(
        username=users['user_3']['username'],
        email=users['user_3']['email'],
        password=users['user_3']['password'],
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
            'attendees_id': [sample_user_2().id],
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

    def test_create_event_with_default_place(self):
        """Test when creating an event not sending a place, must create event with default place"""
        p_1 = sample_user_1().profile
        p_2 = sample_user_2().profile

        Place.objects.create().members.add(p_1)

        payload = {
            'attendees_id': [p_2.id],
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
        self.assertEqual(p_2.events.count(), 1)
        self.assertEqual(p_2.hosted_events.count(), 0)
        self.assertEqual(res.data.get('place'), get_place_or_default(p_1).id)
        self.assertEqual(res.data.get('host'), str(p_1))
        self.assertFalse(res.data.get('only_host_inventory'))

    def test_create_event_with_place_and_only_host_inventory(self):
        """Test when creating an event not sending a place, must create event with default place"""
        p_1 = sample_user_1().profile
        p_2 = sample_user_2().profile

        Place.objects.create().members.add(p_1)  # default place
        place = Place.objects.create()  # another non default place
        place.members.add(p_1)

        payload = {
            'attendees_id': [p_2.id],
            'name': 'Test name',
            'starting_datetime': self.tomorrow,
            'finishing_datetime': self.day_after_tomorrow,
            'place': place.id,
            'only_host_inventory': True
        }

        res = self.client.post(
            EVENT_URL,
            payload
        )

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(p_1.events.count(), 0)
        self.assertEqual(p_1.hosted_events.count(), 1)
        self.assertEqual(p_2.events.count(), 1)
        self.assertEqual(p_2.hosted_events.count(), 0)
        self.assertEqual(res.data.get('place'), place.id)
        self.assertEqual(res.data.get('host'), str(p_1))
        self.assertTrue(res.data.get('only_host_inventory'))

    def test_create_event_with_not_friend(self):
        """Test when creating an event with an attendee that is not your friend, must return error"""
        p_1 = sample_user_1().profile
        p_3 = sample_user_3().profile

        Place.objects.create().members.add(p_1)

        payload = {
            'attendees_id': [p_3.id],
            'name': 'Test name',
            'starting_datetime': self.tomorrow,
            'finishing_datetime': self.day_after_tomorrow,
        }

        res = self.client.post(
            EVENT_URL,
            payload
        )

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(p_1.events.count(), 0)
        self.assertEqual(p_1.hosted_events.count(), 0)
        self.assertEqual(p_3.events.count(), 0)
        self.assertEqual(p_3.hosted_events.count(), 0)
