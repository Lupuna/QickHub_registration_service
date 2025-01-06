from unittest.mock import patch, MagicMock

from django.test import TestCase
from django.conf import settings
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from core.exeptions import TwoCommitsError

from jwt_registration.utils import TwoCommitsPatternBase, TwoCommitsPatternMixin, UpdateTwoCommitsPattern, CreateTwoCommitsPattern, ConfirmTwoCommitsPattern
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
            self.assertEqual(
                e.exception.detail['error'], 'Invalid refresh token')


class TwoCommitsPatternBaseTestCase(TestCase):
    def setUp(self):
        self.data = {
            'email': 'test_email@gmail.com'
        }
        self.service = 'company'

    @patch('jwt_registration.utils.requests.post')
    def test_external_request(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        create_head = CreateTwoCommitsPattern(self.data, self.service)
        response_info = create_head._post_request_to_external_api()

        self.assertEqual({self.service: 200}, response_info)

    @patch('jwt_registration.utils.CreateTwoCommitsPattern._rollback_operation')
    @patch('jwt_registration.utils.CreateTwoCommitsPattern._post_request_to_external_api')
    def test_rollback_operation(self, mock_post, mock_rollback):
        mock_post.return_value = {self.service: 500}

        with self.assertRaises(TwoCommitsError):
            create_head = CreateTwoCommitsPattern(self.data, self.service)
            create_head._base_commit_operation()

        mock_rollback.assert_called_once()

    def test_get_err_obj(self):
        create_head = CreateTwoCommitsPattern(self.data, self.service)
        response1 = {self.service: 500}
        response2 = {self.service: 200}
        error1 = create_head._get_error_object(response_info=response1)
        error2 = create_head._get_error_object(response_info=response2)

        self.assertTrue(isinstance(error1, TwoCommitsError))
        self.assertFalse(error2)

    @patch('jwt_registration.utils.CreateTwoCommitsPattern._rollback_operation')
    @patch('jwt_registration.utils.CreateTwoCommitsPattern._post_request_to_external_api')
    def test_base_commit_operation(self, mock_post, mock_rollback):
        mock_post.return_value = {self.service: 200}

        create_head = CreateTwoCommitsPattern(self.data, self.service)
        response1 = create_head._base_commit_operation()

        self.assertEqual({self.service: 200}, response1)

        mock_post.return_value = {self.service: 500}

        with self.assertRaises(TwoCommitsError):
            response2 = create_head._base_commit_operation()
        mock_rollback.assert_called_once()


class TwoCommitsOperationTestCase(TestCase):
    def setUp(self):
        self.data = {
            'email': 'test_email@gmail.com'
        }
        self.service = 'company'

    @patch('jwt_registration.utils.CreateTwoCommitsPattern._base_commit_operation')
    @patch('jwt_registration.utils.ConfirmTwoCommitsPattern._confirm_operation')
    def test_two_commits_operation_ok(self, mock_confirm, mock_base_commit):
        create_head = CreateTwoCommitsPattern(self.data, self.service)
        create_head.two_commits_operation()

        mock_base_commit.assert_called_once()
        mock_confirm.assert_called_once()

    @patch('jwt_registration.utils.TwoCommitsPatternBase._post_request_to_external_api')
    def test_two_commits_operation_not_ok(self, mock_post):
        mock_post.return_value = {self.service: 500}
        create_head = CreateTwoCommitsPattern(self.data, self.service)

        with self.assertRaises(TwoCommitsError):
            create_head.two_commits_operation()
