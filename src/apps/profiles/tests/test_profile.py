from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

REGISTER_USER = reverse('rest_register')
PROFILES = reverse('profile-list')


def detail_url(profile_id):
    """Return profile detail url"""
    return reverse('profile-detail', args=[profile_id])


def detail_url_inactivate(profile_id):
    """Return profile inactivate detail url"""
    return reverse('profile-inactivate', args=[profile_id])


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


class RegisterTests(APITestCase):
    def test_create_user_successful(self):
        """Test when registrating an user correctly, must create a profile"""
        payload = {
            'email': users['user_1']['email'],
            'username': users['user_1']['username'],
            'password1': users['user_1']['password'],
            'password2': users['user_1']['password'],
        }

        res = self.client.post(
            REGISTER_USER,
            payload
        )

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        user = get_user_model().objects.get(
            email=users['user_1']['email'],
            username=users['user_1']['username']
        )
        self.assertTrue(user)

        profile = user.profile
        self.assertTrue(profile)


class ProfileTests(APITestCase):
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

        res = self.client.get(
            detail_url(u_1.profile.id)
        )
        self.assertTrue(res.data)
        self.assertEqual(u_1.id, res.data['user']['id'])

    def test_patch_profile_not_login(self):
        """Test when trying to patch a profile WITHOUT login, must return 403 Forbidden"""
        u_1 = sample_user_1()

        payload = {
            'biography': 'Test biography'
        }

        res = self.client.patch(
            detail_url(u_1.profile.id),
            payload
        )

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_patch_profile_login_diff_profile(self):
        """Test when trying to patch a profile WITH login but NOT OWN profile,
        must return 403 Forbidden"""
        u_1 = sample_user_1()
        u_2 = sample_user_2()

        self.client.force_authenticate(user=u_1)

        payload = {
            'biography': 'Test biography'
        }

        res = self.client.patch(
            detail_url(u_2.profile.id),
            payload
        )

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_patch_profile_login_own_profile(self):
        """Test when trying to patch OWN profile WITH login,
        must return the updated profile"""
        u_1 = sample_user_1()

        self.client.force_authenticate(user=u_1)

        self.assertEqual(u_1.profile.biography, '')

        payload = {
            'biography': 'Test biography'
        }

        res = self.client.patch(
            detail_url(u_1.profile.id),
            payload
        )

        self.assertTrue(res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['biography'], 'Test biography')

    def test_post_profile_inactivate_not_own_profile(self):
        """Test when trying to inactivate a profile WITH login but NOT OWN profile,
        must return 403 Forbidden"""
        u_1 = sample_user_1()
        u_2 = sample_user_2()

        self.client.force_authenticate(user=u_1)

        res = self.client.post(
            detail_url_inactivate(u_2.profile.id),
        )

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_post_profile_inactivate_own_profile(self):
        """Test when trying to inactivate OWN profile WITH login,
        must profile with inactivate user"""
        u_1 = sample_user_1()

        self.client.force_authenticate(user=u_1)

        self.assertTrue(u_1.is_active)

        res = self.client.post(
            detail_url_inactivate(u_1.profile.id),
        )

        self.assertTrue(res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertFalse(res.data['user']['is_active'])
