from loguru import logger
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings
from core.exeptions import TwoCommitsError
import requests
from typing import Literal


class TwoCommitsPatternBase:

    def __init__(self, data: dict | None, service: str):
        self.data = data
        self.service = service

    def _create_object(self):
        response = requests.post(
            url=settings.TWO_COMMITS_CONF['services'][self.service]['create'], data=self.data)
        statuses_codes = {
            self.service: response.status_code
        }
        create_errors = self._get_errors(statuses_codes=statuses_codes, move='create') 

        if create_errors:
            self._rollback_object('create')
            raise create_errors
        return statuses_codes

    def _update_object(self):
        response = requests.post(
            url=settings.TWO_COMMITS_CONF['services'][self.service]['update'], data=self.data)
        statuses_codes = {
            self.service: response.status_code
        }
        update_errors = self._get_errors(statuses_codes=statuses_codes, move='update')

        if update_errors:
            self._rollback_object('update')
            raise update_errors
        return statuses_codes

    def _confirm_object(self):
        response = requests.post(
            url=settings.TWO_COMMITS_CONF['services'][self.service]['confirm'], data=self.data)
        statuses_codes = {
            self.service: response.status_code
        }
        confirm_errors = self._get_errors(statuses_codes=statuses_codes, move='confirm')

        if confirm_errors:
            self._rollback_object('confirm')
            raise confirm_errors
        return statuses_codes

    def _rollback_object(self, move):
        data = self.data
        data.update({'move': move})
        requests.post(url=settings.TWO_COMMITS_CONF['services'][self.service]['rollback'], data=data) 

    def _get_errors(self, statuses_codes, move):
        return [TwoCommitsError({'error': f'{service} two commits {move} problem'}) for
                           service, status_code in statuses_codes.items() if status_code != 200]


class UpdateTwoCommitsPattern(TwoCommitsPatternBase):

    def two_commits_operation(self):
        self._update_object()
        self._confirm_object()


class CreateTwoCommitsPattern(TwoCommitsPatternBase):

    def two_commits_operation(self):
        self._create_object()
        self._confirm_object()


def put_token_on_blacklist(refresh_token):
    try:
        old_token = RefreshToken(refresh_token)
        old_token.blacklist()
    except TokenError as e:
        logger.critical(f"TokenError: {e}. It might be a potential security threat.")
        raise ValidationError({'error': 'Invalid refresh token'})

