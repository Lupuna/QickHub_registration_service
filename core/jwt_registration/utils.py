from loguru import logger
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication


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


def put_token_on_blacklist(refresh_token):
    try:
        old_token = RefreshToken(refresh_token)
        old_token.blacklist()
    except TokenError as e:
        logger.critical(f"TokenError: {e}. It might be a potential security threat.")
        raise ValidationError({'error': 'Invalid refresh token'})
