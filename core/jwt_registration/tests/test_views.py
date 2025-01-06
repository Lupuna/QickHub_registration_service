from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from unittest.mock import patch
from user_profile.models import User
from rest_framework_simplejwt.exceptions import TokenError
from itsdangerous import BadSignature, SignatureExpired
from freezegun import freeze_time
from django.utils import timezone
from django.conf import settings


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

    @patch("jwt_registration.views.CreateTwoCommitsPattern.two_commits_operation")
    def test_registration(self, test):
        response = self.client.post(self.registration_url, self.user_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(
            email=self.user_data['email']).exists())

    def test_registration_invalid_data(self):
        response = self.client.post(
            self.registration_url, self.wrong_user_data)
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

    def test_login_invalid_data(self):
        with self.subTest('AuthenticationFailed'):
            login_data = {
                'email': 'wronguser',
                'password': 'wrongpass'
            }
            response = self.client.post(self.login_url, login_data)
            self.assertEqual(response.status_code,
                             status.HTTP_401_UNAUTHORIZED)
            self.assertIn('error', response.data)

        with self.subTest('ValidationError'):
            login_data = {}
            response = self.client.post(self.login_url, login_data)
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn('error', response.data)

    def test_logout(self):
        user = User.objects.create_user(
            email=self.user_data['email'],
            first_name=self.user_data['first_name'],
            last_name=self.user_data['last_name'],
        )
        refresh = RefreshToken.for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {
                                refresh.access_token}')
        response = self.client.post(
            self.logout_url, {'refresh_token': str(refresh)})
        self.assertEqual(response.status_code, status.HTTP_205_RESET_CONTENT)
        self.assertEqual(response.data.get('detail'),
                         'Successfully logged out')

    def test_logout_without_refresh_token(self):
        user = User.objects.create_user(
            email=self.user_data['email'],
            password=self.user_data['password'],
            first_name=self.user_data['first_name'],
            last_name=self.user_data['last_name'],
        )
        refresh = RefreshToken.for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {
                                refresh.access_token}')
        response = self.client.post(self.logout_url)
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
        self.client.cookies['refresh_token'] = 'invalidtoken'
        response = self.client.post(self.logout_url)
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


class EmailVerifyTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create(email='test@gmail.com')
        self.data_to_post = {
            'email': 'test@gmail.com',
            'password': 'test_password',
            'password2': 'test_password'
        }
        self.client = APIClient()
        self.url = settings.REGISTRATION_SERVICE_URL + \
            reverse('to_email_verify')

    @patch('jwt_registration.tasks.send_celery_mail.delay')
    def test_email_verify_successful(self, mock_send_mail):
        response = self.client.post(self.url, self.data_to_post)

        mock_send_mail.assert_called_once()
        args, kwargs = mock_send_mail.call_args

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data, {'detail': 'We sent mail on your email to verification'})

        verification_url = kwargs['message'].split()[-1]

        response = self.client.get(verification_url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data, {'detail': 'Email verified succesfully!'})
        self.user.refresh_from_db()
        self.assertTrue(self.user.email_verified)

    def test_user_already_verified(self):
        self.user.email_verified = True
        self.user.save()

        response = self.client.post(self.url, self.data_to_post)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            str(response.data['non_field_errors'][0]), 'Email is already verified')

    @patch('jwt_registration.tasks.send_celery_mail.delay')
    def test_invalid_token(self, mock_send_mail):
        response = self.client.post(self.url, self.data_to_post)

        args, kwargs = mock_send_mail.call_args

        verification_url = kwargs['message'].split()[-1]
        url_with_invalid_token = '/'.join(
            verification_url.split('/')[:-2]) + '/fasdfasd/'

        response = self.client.get(url_with_invalid_token)

        self.assertEqual(response.status_code, 406)
        self.assertEqual(response.data, {'error': 'Invalid token'})

    @patch('jwt_registration.tasks.send_celery_mail.delay')
    def test_token_expired(self, mock_send_mail):
        response = self.client.post(self.url, self.data_to_post)

        args, kwargs = mock_send_mail.call_args

        verification_url = kwargs['message'].split()[-1]

        with freeze_time(timezone.now() + timezone.timedelta(hours=2)):
            response = self.client.get(verification_url)

            self.assertEqual(response.status_code, 406)
            self.assertEqual(response.data, {'error': 'Token expired'})

    @patch('jwt_registration.tasks.send_celery_mail.delay')
    def test_user_does_not_exists(self, mock_send_mail):
        self.data_to_post.update({'email': 'asf@gmail.com'})
        response = self.client.post(self.url, self.data_to_post)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            str(response.data['non_field_errors'][0]), 'Email was not find')


class PasswordRecoveryTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create(email='test_email@gmail.com')
        self.user.set_password('test_password1')
        self.user.save()
        self.data_to_post = {'email': 'test_email@gmail.com'}
        self.password_to_post = {
            'pas1': 'test_new_pas', 'pas2': 'test_new_pas'}
        self.send_mail_url = settings.REGISTRATION_SERVICE_URL + \
            reverse('password_recovery')
        self.client = APIClient()

    @patch('jwt_registration.tasks.send_celery_mail.delay')
    def test_send_email(self, mock_send_mail):
        response = self.client.post(self.send_mail_url, self.data_to_post)

        mock_send_mail.assert_called_once()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {
                         'detail': 'We sent mail on your email to recovery your password'})

    @patch('jwt_registration.tasks.send_celery_mail.delay')
    def test_wrong_email(self, mock_send_mail):
        self.data_to_post.update({'email': 'sgsd@gmail.com'})
        response = self.client.post(self.send_mail_url, self.data_to_post)

        self.assertEqual(response.data, {'error': 'Incorrect email'})
        self.assertEqual(response.status_code, 400)

    @patch('jwt_registration.tasks.send_celery_mail.delay')
    def test_set_new_password_OK(self, mock_send_mail):
        response = self.client.post(self.send_mail_url, self.data_to_post)

        args, kwargs = mock_send_mail.call_args
        reset_pas_url = kwargs['message'].split()[-1]
        response = self.client.post(reset_pas_url, self.password_to_post)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data, {'detail': 'Password recovered successfully'})

        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(
            self.password_to_post['pas1']))

    @patch('jwt_registration.tasks.send_celery_mail.delay')
    def test_set_new_password_BAD(self, mock_send_mail):
        response = self.client.post(self.send_mail_url, self.data_to_post)

        args, kwargs = mock_send_mail.call_args
        reset_pas_url = kwargs['message'].split()[-1]
        self.password_to_post.update({'pas2': 'asaspdaf94'})
        response = self.client.post(reset_pas_url, self.password_to_post)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, {'error': 'Incorrect data'})

    @patch('jwt_registration.tasks.send_celery_mail.delay')
    def test_invalid_token(self, mock_send_mail):
        response = self.client.post(self.send_mail_url, self.data_to_post)

        args, kwargs = mock_send_mail.call_args
        reset_pas_url = kwargs['message'].split()[-1]
        url_with_invalid_token = '/'.join(
            reset_pas_url.split('/')[:-2]) + '/fasdfasd/'
        response = self.client.post(
            url_with_invalid_token, self.password_to_post)

        self.assertEqual(response.status_code, 406)
        self.assertEqual(response.data, {'error': 'Invalid token'})

    @patch('jwt_registration.tasks.send_celery_mail.delay')
    def test_token_expired(self, mock_send_mail):
        response = self.client.post(self.send_mail_url, self.data_to_post)

        args, kwargs = mock_send_mail.call_args
        reset_pas_url = kwargs['message'].split()[-1]

        with freeze_time(timezone.now()+timezone.timedelta(hours=2)):
            response = self.client.post(
                reset_pas_url, self.password_to_post)
            self.assertEqual(response.status_code, 406)
            self.assertEqual(response.data, {'error': 'Token expired'})
