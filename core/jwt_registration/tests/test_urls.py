from django.test import SimpleTestCase
from django.urls import resolve, reverse
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView

from jwt_registration import views


class TestUrls(SimpleTestCase):

    def test_registration_url_is_resolve(self):
        url = reverse('registration')
        self.assertEqual(resolve(url).func.view_class, views.RegistrationAPIView)

    def test_login_url_is_resolve(self):
        url = reverse('login')
        self.assertEqual(resolve(url).func.view_class, views.LoginAPIView)

    def test_logout_url_is_resolve(self):
        url = reverse('logout')
        self.assertEqual(resolve(url).func.view_class, views.LogoutAPIView)

    def test_refresh_token_url_is_resolve(self):
        url = reverse('token_refresh')
        self.assertEqual(resolve(url).func.view_class, TokenRefreshView)

    def test_refresh_token_verify_is_resolve(self):
        url = reverse('token_verify')
        self.assertEqual(resolve(url).func.view_class, TokenVerifyView)

    def test_update_important_data_url_is_resolve(self):
        url = reverse('update_important_data')
        self.assertEqual(resolve(url).func.view_class, views.UpdateImportantDataAPIView)
