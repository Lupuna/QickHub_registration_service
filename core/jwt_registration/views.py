from django.contrib.auth import authenticate
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.exceptions import ValidationError, AuthenticationFailed
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken

from core.swagger_info import *
from jwt_registration.serializers import UserImportantSerializer
from jwt_registration.utils import put_token_on_blacklist, HeadTwoCommitsPattern, generate_response_with_cookie_200
from django.db import transaction


class RegistrationAPIView(APIView):

    @extend_schema(request=UserImportantSerializer, responses=response_for_registration)
    def post(self, request):
        serializer = UserImportantSerializer(data=request.data)
        if serializer.is_valid():
            with transaction.atomic():
                user = serializer.save()
                head = HeadTwoCommitsPattern(
                    data={
                        'email': user.email,
                    },
                    self_package={
                        'company': {
                            'create': 'api/v1/company/registration/users/create',
                            'confirm': 'api/v1/company/registration/users/confirm',
                            'rollback': 'api/v1/company/registration/users/rollback'
                        },
                    }
                )
                head.two_commits_operation()

            refresh = RefreshToken.for_user(user)
            refresh.payload.update({
                'user_id': user.id,
                'email': user.email,
            })
            response = Response({}, status=status.HTTP_201_CREATED)
            response.set_cookie(
                key='refresh_token',
                value=str(refresh),
            )
            response.set_cookie(
                key='access_token',
                value=str(refresh.access_token),
            )
            return response
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginAPIView(APIView):

    @extend_schema(request=request_for_login, responses=response_for_login)
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        if email is None or password is None:
            raise ValidationError({'error': 'Email and password are required'})

        user = authenticate(email=email, password=password)
        if user is None:
            raise AuthenticationFailed({'error': 'Incorrect username or password'})
        refresh = RefreshToken.for_user(user)
        refresh.payload.update({
            'user_id': user.id,
            'email': user.email
        })
        return generate_response_with_cookie_200(str(refresh), str(refresh.access_token))


class LogoutAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    @extend_schema(request=None, responses=response_for_logout)
    def post(self, request):
        refresh_token = request.COOKIES.get('refresh_token')
        if not refresh_token: raise ValidationError({'error': 'Refresh token is required'})
        put_token_on_blacklist(refresh_token)
        response = Response({'detail': 'Successfully logged out'}, status=status.HTTP_205_RESET_CONTENT)
        response.delete_cookie('refresh_token')
        response.delete_cookie('access_token')
        return response


class UpdateImportantDataAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    @extend_schema(request=request_for_important_info, responses=response_for_important_data)
    def patch(self, request):
        data_to_update = request.data.get('data_to_update')
        old_refresh_token = request.COOKIES.get("refresh_token")
        current_password = request.data.get('password')
        self._validate_update_request(current_password, data_to_update, old_refresh_token, request)
        serializer = UserImportantSerializer(instance=request.user, data=data_to_update, partial=True)
        if serializer.is_valid():
            put_token_on_blacklist(old_refresh_token)
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return generate_response_with_cookie_200(str(refresh), str(refresh.access_token))

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def _validate_update_request(current_password, data_to_update, old_refresh_token, request):
        if not data_to_update:
            raise ValidationError({'error': 'data_to_update is required'})
        if not old_refresh_token:
            raise ValidationError({'error': 'Refresh token is required'})
        if not current_password:
            raise ValidationError({'error': 'Current password is required'})
        if not request.user.check_password(current_password):
            raise ValidationError({'error': 'Current password is incorrect'})


class TokenRefreshView(APIView):
    @extend_schema(request=None, responses=response_for_refresh_token)
    def post(self, request):
        refresh_token = request.COOKIES.get('refresh_token')
        if not refresh_token:
            return Response({'error': 'Refresh token is required in cookies'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            refresh = RefreshToken(refresh_token)
            return generate_response_with_cookie_200(str(refresh), str(refresh.access_token))
        except InvalidToken:
            return Response({'error': 'Invalid refresh token'}, status=status.HTTP_401_UNAUTHORIZED)


class TokenVerifyView(APIView):
    @extend_schema(request=None, responses=response_for_validate_token)
    def post(self, request):
        access_token = request.COOKIES.get('access_token')
        if not access_token:
            return Response({'error': 'Access token is required in cookies'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            AccessToken(access_token)
            return Response({'detail': 'Token is valid'}, status=status.HTTP_200_OK)
        except (InvalidToken, TokenError):
            return Response({'error': 'Invalid token'}, status=status.HTTP_401_UNAUTHORIZED)

