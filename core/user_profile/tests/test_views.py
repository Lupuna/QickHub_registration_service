from django.urls import reverse
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .test_base import Settings
from rest_framework.test import APITestCase, APIClient


class ProfileAPIViewSetTestCase(Settings, APITestCase):

    def setUp(self):
        self.client = APIClient()
        self.profile_url = reverse('user-detail', args=[self.user.id])

    def test_login_user(self):
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_no_login_user(self):
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

