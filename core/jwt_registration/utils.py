from loguru import logger
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.conf import settings
from core.exeptions import TwoCommitsError
import requests


class CookieJWTAuthentication(JWTAuthentication):

    def authenticate(self, request):
        raw_token = request.COOKIES.get('access_token')
        if raw_token is None: return None
        validated_token = self.get_validated_token(raw_token)
        return self.get_user(validated_token), validated_token

    @staticmethod
    def get_user_id_in_jwt_token(request):
        auth = CookieJWTAuthentication()
        raw_token = request.COOKIES.get('access_token')
        if raw_token is None:
            return None

        validated_token = auth.get_validated_token(raw_token)
        user_id = validated_token.get('user_id')
        return user_id


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


def generate_response_with_cookie_200(refresh, access):
    response = Response({}, status=status.HTTP_200_OK)
    response.set_cookie(
        key='refresh_token',
        value=refresh,
    )
    response.set_cookie(
        key='access_token',
        value=access,
    )
    return response
