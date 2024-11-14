from loguru import logger
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings
from core.exeptions import TwoCommitsError
import requests


class HeadTwoCommitsPattern:

    def __init__(self, data: dict | None, self_package: dict[str]):
        self.data = data
        self.self_package = self_package

    def two_commits_operation(self):
        creation_statuses_codes = self._create_object()
        creation_errors = [TwoCommitsError({'error': f'{service} two commits creation problem'}) for
                           service, status_code in creation_statuses_codes.items() if status_code != 200]
        if creation_errors:
            self._rollback_object()
            raise creation_errors

        confirm_statuses_codes = self._confirm_object()
        confirm_errors = [TwoCommitsError({'error': f'{service} two commits creation problem'}) for
                          service, status_code in confirm_statuses_codes.items() if status_code != 200]
        if confirm_errors:
            self._rollback_object()
            raise confirm_errors

    def _create_object(self):
        company_response = requests.post(
            url=settings.COMPANY_SERVICE_URL.format(self.self_package['company']['create']))
        statuses_codes = {
            'company': company_response.status_code
        }
        return statuses_codes

    def _confirm_object(self):
        company_response = requests.post(
            url=settings.COMPANY_SERVICE_URL.format(self.self_package['company']['confirm']))
        statuses_codes = {
            'company': company_response.status_code
        }
        return statuses_codes

    def _rollback_object(self):
        requests.post(url=settings.COMPANY_SERVICE_URL.format(self.self_package['company']['rollback']))


def put_token_on_blacklist(refresh_token):
    try:
        old_token = RefreshToken(refresh_token)
        old_token.blacklist()
    except TokenError as e:
        logger.critical(f"TokenError: {e}. It might be a potential security threat.")
        raise ValidationError({'error': 'Invalid refresh token'})
