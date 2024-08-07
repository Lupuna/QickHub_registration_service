from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from user_profile.models import User
from rest_framework_simplejwt.tokens import RefreshToken


class RegistrationAPITestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.registration_url = reverse('registration')
        self.login_url = reverse('login')
        self.logout_url = reverse('logout')
        self.user_data = {
            'username': 'test_user',
            'email': 'test_user@example.com',
            'password': 'testpass_123',
            'password2': 'testpass_123',
        }

        self.wrong_user_data = {
            'username': 'test_user',
            'email': 'testuser@example.com',
            'password': 'test_pass123',
            'password2': 'wrong_test_pass123',
        }

    def test_registration(self):
        response = self.client.post(self.registration_url, self.user_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('refresh', response.data)
        self.assertIn('access', response.data)
        self.assertTrue(User.objects.filter(username=self.user_data['username']).exists())

    def test_registration_invalid_data(self):
        response = self.client.post(self.registration_url, self.wrong_user_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('non_field_errors', response.data)

    def test_login(self):
        User.objects.create_user(username=self.user_data['username'], password=self.user_data['password'])
        login_data = {
            'username': self.user_data['username'],
            'password': self.user_data['password']
        }
        response = self.client.post(self.login_url, login_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('refresh', response.data)
        self.assertIn('access', response.data)

    def test_login_invalid_data(self):
        with self.subTest('AuthenticationFailed'):
            login_data = {
                'username': 'wronguser',
                'password': 'wrongpass'
            }
            response = self.client.post(self.login_url, login_data)
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
            self.assertIn('error', response.data)

        with self.subTest('ValidationError'):
            login_data = {}
            response = self.client.post(self.login_url, login_data)
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn('error', response.data)

    def test_logout(self):
        user = User.objects.create_user(username=self.user_data['username'], password=self.user_data['password'])
        refresh = RefreshToken.for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        response = self.client.post(self.logout_url, {'refresh': str(refresh)})
        self.assertEqual(response.status_code, status.HTTP_205_RESET_CONTENT)

    def test_logout_without_refresh_token(self):
        user = User.objects.create_user(username=self.user_data['username'], password=self.user_data['password'])
        refresh = RefreshToken.for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        response = self.client.post(self.logout_url, {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def test_logout_with_invalid_token(self):
        User.objects.create_user(username=self.user_data['username'], password=self.user_data['password'])
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer invalidtoken')
        response = self.client.post(self.logout_url, {'refresh': 'invalidtoken'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_logout_without_access_token(self):
        user = User.objects.create_user(username=self.user_data['username'], password=self.user_data['password'])
        refresh = RefreshToken.for_user(user)
        response = self.client.post(self.logout_url, {'refresh': str(refresh)})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
