import shutil
import tempfile
from io import BytesIO
from unittest.mock import patch, MagicMock
import requests

from PIL import Image

from django.conf import settings
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient, APIRequestFactory
from rest_framework_simplejwt.tokens import RefreshToken

from user_profile.serializers import ProfileUserForCompanySerializer
from user_profile.models import User
from .test_base import Settings, mock_upload_file
from ..views import ProfileCompanyAPIView


class ProfileAPIViewSetTestCase(Settings):
    def setUp(self):
        self.profile_url = reverse('user-detail', args=[self.user.id])
        self.refresh = RefreshToken.for_user(self.user)

    def user_login(self):
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {
                           self.refresh.access_token}')
        return client

    def test_retrieve_with_cache(self):
        cache_key = settings.USER_PROFILE_CACHE_KEY.format(user=self.user.pk)
        cache.delete(cache_key)
        client = self.user_login()
        client.get(self.profile_url)
        self.assertIsNotNone(cache.get(cache_key))

    def test_update_invalidate_cache(self):
        client = self.user_login()
        cache_key = settings.USER_PROFILE_CACHE_KEY.format(user=self.user.pk)
        client.get(self.profile_url)
        self.assertIsNotNone(cache.get(cache_key))
        update_data = {'email': 'updateduser@gmail.com'}
        response = client.patch(self.profile_url, update_data, format='json')
        self.assertIsNone(cache.get(cache_key))

    def test_authenticated_user(self):
        client = self.user_login()
        response = client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_not_authenticated_user(self):
        client = APIClient()
        response = client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @patch('user_profile.views.requests.get')
    def test_get_users_info_by_company(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                'id': 2,
                "email": "us@example.com",
                "positions": [
                    {
                        "id": 4,
                        "title": "Водолаз",
                        "description": "string",
                        "access_weight": "Owner",
                        "company": 1,
                    }
                ],
                "departments": []
            }
        ]
        mock_get.return_value = mock_response
        client = self.user_login()
        users_expected = [
            {
                "id": 2,
                "email": "us@example.com",
                "first_name": "zhumshut",
                "last_name": "",
                'otchestwo': '',
                "phone": 'null',
                'business_phone': None,
                'city': None,
                "image_identifier": "c3f1b16c-8102-45b7-b8b5-666f268982fc",
                "date_joined": "2024-11-25T04:57:29Z",
                "links": [],
                "positions": [
                    {
                        "id": 4,
                        "title": "Водолаз",
                        "description": "string",
                        "access_weight": "Owner",
                        "company": 1
                    }
                ],
                "departments": []
            }
        ]

        with self.assertNumQueries(3):
            response = client.get(settings.REGISTRATION_SERVICE_URL + reverse(
                'user-get_users_by_company', kwargs={"company_pk": 1}), HTTP_HOST='127.0.0.1')
            self.assertEqual(users_expected, response.data)

    @patch('user_profile.views.requests.get')
    def test_get_users_by_dep(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": 1,
            "company": 1,
            "title": "dep 1",
            "description": "",
            "parent": 0,
            "users": [
                {
                    "id": 2,
                    "email": "us@example.com"
                }
            ],
            "color": "rgb(177,171,233)"
        }
        mock_get.return_value = mock_response
        client = self.user_login()
        data_expected = {
            'id': 1,
            'company': 1,
            'title': 'dep 1',
            'description': '',
            'parent': 0,
            'users': [
                {
                    'email': 'us@example.com',
                    'phone': 'null',
                    'business_phone': None,
                    'city': None,
                    'birthday': None,
                    'first_name': 'zhumshut',
                    'last_name': '',
                    'otchestwo': '',
                    'date_joined': '2024-11-25T04:57:29Z'
                }
            ],
            'color': 'rgb(177,171,233)'
        }

        response = client.get(settings.REGISTRATION_SERVICE_URL + reverse('user-get_users_by_dep',
                              kwargs={"company_pk": 1, 'dep_pk': 1}), HTTP_HOST='127.0.0.1')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, data_expected)

    @patch('user_profile.views.requests.get')
    def test_get_users_by_deps(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                "id": 1,
                "company": 1,
                "title": "dep 1",
                "description": "",
                "parent": 0,
                "users": [
                    {
                        "id": 2,
                        "email": "us@example.com"
                    }
                ],
                "color": "rgb(177,171,233)"
            }
        ]
        mock_get.return_value = mock_response
        client = self.user_login()
        data_expected = [
            {
                'id': 1,
                'company': 1,
                'title': 'dep 1',
                'description': '',
                'parent': 0,
                'users': [
                    {
                        'email': 'us@example.com',
                        'phone': 'null',
                        'business_phone': None,
                        'city': None,
                        'birthday': None,
                        'first_name': 'zhumshut',
                        'last_name': '',
                        'otchestwo': '',
                        'date_joined': '2024-11-25T04:57:29Z'
                    }
                ],
                'color': 'rgb(177,171,233)'
            }
        ]

        response = client.get(settings.REGISTRATION_SERVICE_URL + reverse('user-get_users_by_deps',
                              kwargs={"company_pk": 1}), HTTP_HOST='127.0.0.1')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, data_expected)


@patch('user_profile.serializers.upload_file', side_effect=mock_upload_file)
class UpdateImportantDataAPIViewTestCase(APITestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.user = User.objects.create_user(
            email='good_username@gmail.com', password='password_123', first_name='first', last_name='last')
        self.url = reverse('load_image')
        self.refresh = RefreshToken.for_user(self.user)
        self.data = {
            'image': self.create_test_image()
        }
        self.data_without_image = {}

    def user_login(self):
        client = APIClient()
        client.force_login(self.user)
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {
                           self.refresh.access_token}')
        return client

    def test_successful_post_request(self, mock_upload_file):
        client = self.user_login()
        response = client.post(self.url, self.data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {'response': 'ok'})

    def test_missing_data_to_update(self, mock_upload_file):
        client = self.user_login()
        response = client.post(
            self.url, self.data_without_image, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'image is required')

    def test_not_authenticated(self, mock_upload_file):
        client = APIClient()
        response = client.post(self.url, self.data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @staticmethod
    def create_test_image():
        file = BytesIO()
        image = Image.new('RGB', (100, 100))
        image.save(file, 'JPEG')
        file.name = 'test.jpeg'
        file.seek(0)
        return SimpleUploadedFile('test.jpeg', file.getvalue(), content_type='image/jpeg')


class UserCompanyAPIViewSetTestCase(Settings):

    def setUp(self):
        self.factory = APIRequestFactory()
        self.url = reverse('company_profile')
        self.view = ProfileCompanyAPIView()

    def test_get_queryset(self):
        request = self.factory.post(self.url)
        request.data = {
            'emails': [self.user.email]
        }
        self.view.setup(request)
        queryset = self.view.get_queryset()
        correct_meaning = User.objects.prefetch_related('links').filter(email__in=[self.user.email]).only(
            'id', 'first_name', 'last_name',
            'phone', 'image_identifier', 'date_joined', 'links'
        )
        self.assertQuerySetEqual(queryset, correct_meaning)
