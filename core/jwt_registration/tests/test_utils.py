from unittest.mock import patch

from django.test import TestCase
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from jwt_registration.utils import put_token_on_blacklist
from user_profile.models import User


class UserTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='test@example.com', password='testpassword')
        self.refresh_token = RefreshToken.for_user(self.user)

    def test_put_token_on_blacklist_success(self):
        with patch('jwt_registration.utils.RefreshToken') as MockRefreshToken:
            mock_token = MockRefreshToken.return_value
            mock_token.blacklist.return_value = None
            put_token_on_blacklist(str(self.refresh_token))

    def test_put_token_on_blacklist_invalid_token(self):
        with patch('jwt_registration.utils.RefreshToken') as MockRefreshToken:
            MockRefreshToken.side_effect = TokenError('Invalid token')
            with self.assertRaises(ValidationError) as e:
                put_token_on_blacklist('invalid_refresh_token')
            self.assertEqual(e.exception.detail['error'], 'Invalid refresh token')