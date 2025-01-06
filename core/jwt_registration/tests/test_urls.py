from django.test import SimpleTestCase
from django.urls import resolve, reverse
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView

from jwt_registration import views


class TestUrls(SimpleTestCase):

    def test_registration_url_is_resolve(self):
        url = reverse('registration')
        self.assertEqual(resolve(url).func.view_class,
                         views.RegistrationAPIView)

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

    def test_email_verify_is_resolve(self):
        url = reverse('to_email_verify')
        self.assertEqual(resolve(url).func.view_class, views.EmailVerifyView)

    def test_is_email_verified_is_resolve(self):
        url = reverse('is_email_verified', kwargs={'token': 'any'})
        self.assertEqual(resolve(url).func.view_class,
                         views.IsEmailVerifiedView)

    def test_password_recovery_mail(self):
        url = reverse('password_recovery')
        self.assertEqual(resolve(url).func.view_class,
                         views.PasswordRecoveryMailAPIView)

    def test_password_recovery_confirm(self):
        url = reverse('new_password_confirm', kwargs={'token': 'any'})
        self.assertEqual(resolve(url).func.view_class,
                         views.PasswordRecoveryConfirmAPIView)
