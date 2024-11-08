import shutil
import tempfile
from io import BytesIO
from unittest.mock import patch

from PIL import Image

from django.conf import settings
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from user_profile.models import User
from .test_base import Settings, mock_upload_file


class ProfileAPIViewSetTestCase(Settings):

    def setUp(self):
        self.profile_url = reverse('user-detail', args=[self.user.id])
        self.refresh = RefreshToken.for_user(self.user)

    def user_login(self):
        client = APIClient()
        client.force_login(user=self.user)
        client.cookies['access_token'] = str(self.refresh.access_token)
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
        self.client.get(self.profile_url)
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
        client.force_login(user=self.user)
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


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
        self.user = User.objects.create_user(email='good_username@gmail.com', password='password_123', first_name='first', last_name='last')
        self.url = reverse('load_image')
        self.refresh = RefreshToken.for_user(self.user)
        self.data = {
            'image': self.create_test_image()
        }
        self.data_without_image = {}

    def user_login(self):
        client = APIClient()
        client.force_login(user=self.user)
        client.cookies['access_token'] = str(self.refresh.access_token)
        return client

    def test_successful_patch_request(self, mock_upload_file):
        client = self.user_login()
        response = client.post(self.url, self.data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {'response': 'ok'})

    def test_missing_data_to_update(self, mock_upload_file):
        client = self.user_login()
        response = client.post(self.url, self.data_without_image, format='multipart')
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

