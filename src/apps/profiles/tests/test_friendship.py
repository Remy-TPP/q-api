from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.profiles.models import FriendshipRequest, FriendshipStatus

FRIENDSHIP = reverse('friendshiprequest-list')


def detail_url_accept(id):
    """Return friendship detail accept url"""
    return reverse('friendshiprequest-accept', args=[id])


def detail_url_reject(id):
    """Return friendship detail reject url"""
    return reverse('friendshiprequest-reject', args=[id])


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
    },
    'user_3': {
        'email': 'test3@test3.com',
        'username': 'soyTest3',
        'password': 'Test3pass123'
    },

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


class FriendshipTests(APITestCase):
    fixtures = ['friendshipstatus.json']

    def setUp(self):
        # create a sample friendship request with pk=1 for tests
        u_1 = sample_user_1()
        u_2 = sample_user_2()

        FriendshipRequest.objects.create(
            id=1,
            profile_requesting=u_1.profile,
            profile_requested=u_2.profile,
            status=FriendshipStatus.objects.get(name='REQUESTED')
        )

    def test_post_friendship(self):
        """Test when post a friendshiprequest authenticated must create the request with
        status REQUESTED"""
        u_1 = sample_user_1()
        u_2 = sample_user_2()

        self.client.force_authenticate(user=u_1)

        payload = {
            'profile_requested': u_2.profile.id
        }

        res = self.client.post(
            FRIENDSHIP,
            payload
        )

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(res.data)
        self.assertEqual(res.data['profile_requesting'], u_1.profile.id)
        self.assertEqual(res.data['profile_requested'], u_2.profile.id)
        self.assertEqual(res.data['status'], 'REQUESTED')

    def test_get_friendship_u_3(self):
        """Test when get my friendshiprequests authenticated must return all friendshiprequests
        where the requesting or requested is me"""
        u_3 = sample_user_3()

        self.client.force_authenticate(user=u_3)

        res = self.client.get(
            FRIENDSHIP
        )

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(res.data)
        self.assertEqual(res.data['count'], 0)

    def test_get_friendship_requesting_u_1(self):
        """Test when get my friendshiprequests authenticated must return all friendshiprequests
        where the requesting or requested is me"""
        u_1 = sample_user_1()

        self.client.force_authenticate(user=u_1)

        res = self.client.get(
            FRIENDSHIP
        )

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(res.data)
        self.assertEqual(res.data['count'], 1)
        self.assertEqual(res.data['results'][0]['profile_requesting'], u_1.profile.id)
        self.assertEqual(res.data['results'][0]['status'], 'REQUESTED')

    def test_get_friendship_requested_u_2(self):
        """Test when get my friendshiprequests authenticated must return all friendshiprequests
        where the requesting or requested is me"""
        u_2 = sample_user_2()

        self.client.force_authenticate(user=u_2)

        res = self.client.get(
            FRIENDSHIP
        )

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(res.data)
        self.assertEqual(res.data['count'], 1)
        self.assertEqual(res.data['results'][0]['profile_requested'], u_2.profile.id)
        self.assertEqual(res.data['results'][0]['status'], 'REQUESTED')

    def test_reject_u_2(self):
        """Test when post a reject to a friendshiprequest where the requested is me
        must return the friendshiprequest with status 'REJECTED'"""
        u_1 = sample_user_1()
        u_2 = sample_user_2()

        self.client.force_authenticate(user=u_2)

        res = self.client.post(
            detail_url_reject(1)
        )

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(res.data)
        self.assertEqual(res.data['profile_requesting'], u_1.profile.id)
        self.assertEqual(res.data['profile_requested'], u_2.profile.id)
        self.assertEqual(res.data['status'], 'REJECTED')

    def test_reject_u_1(self):
        """Test when post a reject to a friendshiprequest where the requested is NOT me
        must return the friendshiprequest with status 'REJECTED'"""
        u_1 = sample_user_1()
        u_2 = sample_user_2()

        self.client.force_authenticate(user=u_1)

        res = self.client.post(
            detail_url_reject(1)
        )

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(res.data)
        self.assertEqual(res.data['profile_requesting'], u_1.profile.id)
        self.assertEqual(res.data['profile_requested'], u_2.profile.id)
        self.assertEqual(res.data['status'], 'REJECTED')

    def test_post_after_reject(self):
        """Test when post a friendshiprequest after rejected
        must return the friendshiprequest with status 'REQUESTED' again"""
        u_1 = sample_user_1()
        u_2 = sample_user_2()

        self.client.force_authenticate(user=u_2)

        self.client.post(
            detail_url_reject(1)
        )

        self.client.force_authenticate(user=u_1)

        payload = {
            'profile_requested': u_2.profile.id
        }

        res = self.client.post(
            FRIENDSHIP,
            payload
        )

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(res.data)
        self.assertEqual(res.data['profile_requesting'], u_1.profile.id)
        self.assertEqual(res.data['profile_requested'], u_2.profile.id)
        self.assertEqual(res.data['status'], 'REQUESTED')

    def test_reject_after_reject(self):
        """Test when post a reject after rejected
        must return status_code=400 and error message"""
        u_1 = sample_user_1()
        u_2 = sample_user_2()

        self.client.force_authenticate(user=u_2)

        self.client.post(
            detail_url_reject(1)
        )

        res = self.client.post(
            detail_url_reject(1)
        )

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(res.data, 'Cannot delete frienship request!')

    def test_accept_u_1(self):
        """Test when post an accept to a friendshiprequest where the requested is NOT me
        must return status_code=400 and error message"""
        u_1 = sample_user_1()
        u_2 = sample_user_2()

        self.client.force_authenticate(user=u_1)

        res = self.client.post(
            detail_url_accept(1)
        )

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(res.data, 'Cannot add friend!')

    def test_accept_u_2(self):
        """Test when post an accept to a friendshiprequest where the requested is me
        must return the friendshiprequest with status 'ACCEPTED' and create friends"""
        u_1 = sample_user_1()
        u_2 = sample_user_2()

        self.client.force_authenticate(user=u_2)

        res = self.client.post(
            detail_url_accept(1)
        )

        self.assertEqual(res.status_code, status.HTTP_202_ACCEPTED)
        self.assertTrue(res.data)
        self.assertEqual(res.data['id'], 1)
        self.assertEqual(res.data['profile_requesting'], u_1.profile.id)
        self.assertEqual(res.data['profile_requested'], u_2.profile.id)
        self.assertEqual(res.data['status'], 'ACCEPTED')
        self.assertTrue(u_1.profile in u_2.profile.friends.all())
        self.assertTrue(u_2.profile in u_1.profile.friends.all())