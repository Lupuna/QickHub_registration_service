from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from user_profile.models import User


class RegistrationAPITestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.registration_url = reverse('registration')
        self.login_url = reverse('login')
        self.logout_url = reverse('logout')
        self.user_data = {
            'email': 'test_user@example.com',
            'password': 'testpass_123',
            'password2': 'testpass_123',
            'first_name': 'first',
            'last_name': 'last'
        }

        self.wrong_user_data = {
            'email': 'testuser@example.com',
            'password': 'test_pass123',
            'password2': 'wrong_test_pass123',
        }

    def test_registration(self):
        response = self.client.post(self.registration_url, self.user_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('refresh', response.data)
        self.assertIn('access', response.data)
        self.assertTrue(User.objects.filter(email=self.user_data['email']).exists())

    def test_registration_invalid_data(self):
        response = self.client.post(self.registration_url, self.wrong_user_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login(self):
        User.objects.create_user(
            email=self.user_data['email'],
            password=self.user_data['password'],
            first_name=self.user_data['first_name'],
            last_name=self.user_data['last_name'],
        )
        login_data = {
            'email': self.user_data['email'],
            'password': self.user_data['password']
        }
        response = self.client.post(self.login_url, login_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('refresh', response.data)
        self.assertIn('access', response.data)

    def test_login_invalid_data(self):
        with self.subTest('AuthenticationFailed'):
            login_data = {
                'email': 'wronguser',
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
        user = User.objects.create_user(
            email=self.user_data['email'],
            password=self.user_data['password'],
            first_name=self.user_data['first_name'],
            last_name=self.user_data['last_name'],
        )
        refresh = RefreshToken.for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        response = self.client.post(self.logout_url, {'refresh': str(refresh)})
        self.assertEqual(response.status_code, status.HTTP_205_RESET_CONTENT)

    def test_logout_without_refresh_token(self):
        user = User.objects.create_user(
            email=self.user_data['email'],
            password=self.user_data['password'],
            first_name=self.user_data['first_name'],
            last_name=self.user_data['last_name'],
        )
        refresh = RefreshToken.for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        response = self.client.post(self.logout_url, {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def test_logout_with_invalid_token(self):
        User.objects.create_user(
            email=self.user_data['email'],
            password=self.user_data['password'],
            first_name=self.user_data['first_name'],
            last_name=self.user_data['last_name'],
        )
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer invalidtoken')
        response = self.client.post(self.logout_url, {'refresh': 'invalidtoken'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_logout_without_access_token(self):
        user = User.objects.create_user(
            email=self.user_data['email'],
            password=self.user_data['password'],
            first_name=self.user_data['first_name'],
            last_name=self.user_data['last_name'],
        )
        refresh = RefreshToken.for_user(user)
        response = self.client.post(self.logout_url, {'refresh': str(refresh)})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class UpdateImportantDataAPIViewTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='good_email', password='password_123', first_name='first', last_name='last')
        self.url = reverse('update_important_data')
        self.refresh = RefreshToken.for_user(self.user)
        self.data = {
            'data_to_update': {
                'password': 'password_123',
                'password2': 'password_123',
                'email': 'newemail@gmail.com'
            },
            'refresh_token': str(self.refresh),
            'password': 'password_123'
        }

        self.data_without_data_to_update = {
            'refresh_token': str(self.refresh),
            'password': 'password_123'
        }

        self.data_without_refresh_token = {
            'data_to_update': {
                'password': 'password_123',
                'password2': 'password_123',
                'email': 'newemail@gmail.com'
            },
            'password': 'password_123'
        }

        self.data_without_password = {
            'data_to_update': {
                'password': 'password_123',
                'password2': 'password_123',
                'email': 'newemail@gmail.com'
            },
            'refresh_token': str(self.refresh),
        }

        self.data_with_invalid_password = {
            'data_to_update': {
                'password': 'password_123',
                'password2': 'password_123',
                'email': 'newemail@gmail.com'
            },
            'refresh_token': str(self.refresh),
            'password': 'wrong_password'
        }

    def test_successful_patch_request(self):
        client = APIClient()
        client.force_login(user=self.user)
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.refresh.access_token}')
        response = client.patch(self.url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, 'newemail@gmail.com')
        self.assertIn('refresh', response.data)
        self.assertIn('access', response.data)

    def test_missing_data_to_update(self):
        client = APIClient()
        client.force_login(user=self.user)
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.refresh.access_token}')
        response = client.patch(self.url, self.data_without_data_to_update, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'data_to_update is required')

    def test_missing_refresh_token(self):
        client = APIClient()
        client.force_login(user=self.user)
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.refresh.access_token}')
        response = client.patch(self.url, self.data_without_refresh_token, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'Refresh token is required')

    def test_missing_password(self):
        client = APIClient()
        client.force_login(user=self.user)
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.refresh.access_token}')
        response = client.patch(self.url, self.data_without_password, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'Current password is required')

    def test_invalid_password(self):
        client = APIClient()
        client.force_login(user=self.user)
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.refresh.access_token}')
        response = client.patch(self.url, self.data_with_invalid_password, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'Current password is incorrect')

    def test_not_authenticated(self):
        client = APIClient()
        response = client.patch(self.url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
