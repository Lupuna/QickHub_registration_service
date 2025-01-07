from loguru import logger
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings
from core.exeptions import TwoCommitsError
import requests
from typing import Literal


class TwoCommitsPatternBase:
    move = None

    def __init__(self, data: dict | None, service: str):
        self.data = data
        self.service = service

    def _post_request_to_external_api(self):
        url = settings.TWO_COMMITS_CONF['services'][self.service][self.move]
        response = requests.post(url, self.data)

        response_info = {
            self.service: response.status_code
        }

        return response_info

    def _rollback_operation(self):
        data = self.data
        data.update({'move': self.move})
        rollback_info = requests.post(
            url=settings.TWO_COMMITS_CONF['services'][self.service]['rollback'], data=data)

    def _get_error_object(self, response_info):
        if response_info[self.service] != 200:
            return TwoCommitsError({'error': f'{self.service} two commits {self.move} problem'})

    def _base_commit_operation(self):
        response_info = self._post_request_to_external_api()
        error = self._get_error_object(response_info)

        if error:
            self._rollback_operation()
            raise error

        return response_info


class TwoCommitsPattern(TwoCommitsPatternBase):
    def two_commits_operation(self):
        first_commit_info = self._base_commit_operation()
        confirm = ConfirmTwoCommitsPattern(self.data, self.service)
        second_commit_info = confirm._confirm_operation()


class ConfirmTwoCommitsPattern(TwoCommitsPatternBase):
    move = 'confirm'

    def _confirm_operation(self):
        return self._base_commit_operation()


class UpdateTwoCommitsPattern(TwoCommitsPattern):
    move = 'update'


class CreateTwoCommitsPattern(TwoCommitsPattern):
    move = 'create'


def put_token_on_blacklist(refresh_token):
    try:
        old_token = RefreshToken(refresh_token)
        old_token.blacklist()
    except TokenError as e:
        logger.critical(
            f"TokenError: {e}. It might be a potential security threat.")
        raise ValidationError({'error': 'Invalid refresh token'})
