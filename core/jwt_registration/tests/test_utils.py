from unittest.mock import patch, MagicMock

from django.test import TestCase
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from core.exeptions import TwoCommitsError
from jwt_registration.utils import HeadTwoCommitsPattern, generate_response_with_cookie_200
from jwt_registration.utils import put_token_on_blacklist
from user_profile.models import User


class UserTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpassword',
            first_name='first',
            last_name='last'
        )
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


class HeadTwoCommitsPatternTestCase(TestCase):

    def setUp(self):

        self.data = {
            'email': 'test_email@gmail.com'
        }
        self.self_package = {
            'company': {
                'create': 'fake_path_create',
                'confirm': 'fake_path_confirm',
                'rollback': 'fake_path_rollback'
            },
        }
        self.head = HeadTwoCommitsPattern(
            data=self.data,
            self_package=self.self_package
        )

    def test__create_object(self):
        result = self.head._create_object()
        expected_keys = ['company']
        for key in expected_keys:
            self.assertIn(key, result)

    def test__confirm_object(self):
        result = self.head._confirm_object()
        expected_keys = ['company']
        for key in expected_keys:
            self.assertIn(key, result)

    def test_two_commits_operation_with_create_object_errors(self):
        self.head._create_object = MagicMock(return_value={'company': 500})
        self.head._rollback_object = MagicMock()
        try:
            self.head.two_commits_operation()
            self.fail("two_commits_operation не вызвал исключений")
        except Exception:
            self.head._rollback_object.assert_called_once()

    def test_two_commits_operation_with_confirm_object_errors(self):
        self.head._create_object = MagicMock(return_value={'company': 200})
        self.head._confirm_object = MagicMock(return_value={'company': 500})
        self.head._rollback_object = MagicMock()

        try:
            self.head.two_commits_operation()
            self.fail("two_commits_operation не вызвал исключений")
        except Exception:
            self.head._rollback_object.assert_called_once()

        self.head._rollback_object.assert_called_once()

    def test_two_commits_operation_success(self):
        self.head._create_object = MagicMock(return_value={'company': 200})
        self.head._confirm_object = MagicMock(return_value={'company': 200})

        try:
            self.head.two_commits_operation()
        except Exception as e:
            self.fail(f"two_commits_operation вызвал исключение: {e}")


class GenerateResponseWithCookie200TestCase(TestCase):

    def test_generate_response_with_cookie_200(self):
        response = generate_response_with_cookie_200('test', 'test')
        self.assertTrue(response.cookies.get('refresh_token') is not None)
        self.assertTrue(response.cookies.get('access_token') is not None)


