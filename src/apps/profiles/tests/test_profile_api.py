from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

REGISTER_USER = reverse('rest_register')
PROFILES = reverse('profile-list')

def detail_url(profile_id):
    """Return profile detail url"""
    return reverse('profile-detail', args=[profile_id])

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


class RegisterTests(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_create_user_successful(self):
        """Test when registrating an user correctly, must create a profile"""
        payload = {
            'email': users['user_1']['email'],
            'username': users['user_1']['username'],
            'password1': users['user_1']['password'],
            'password2': users['user_1']['password'],
        }

        res = self.client.post(REGISTER_USER, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        user = get_user_model().objects.get(
            email=users['user_1']['email'],
            username=users['user_1']['username']
        )
        self.assertTrue(user)

        profile = user.profile
        self.assertTrue(profile)


class ProfileTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_get_profiles(self):
        """Test when trying to access profiles endpoint not login, must return Profiles"""
        sample_user_1()
        sample_user_2()
        res = self.client.get(PROFILES)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(res.data)

    def test_get_profile(self):
        """Test when get a profile with id, should return the profile"""
        u_1 = sample_user_1()

        res = self.client.get(detail_url(u_1.id))
        self.assertTrue(res.data)
        self.assertEqual(u_1.id, res.data['user']['id'])
