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
from jwt_registration.serializers import UserImportantSerializer, UserEmailSerializer
from jwt_registration.utils import put_token_on_blacklist, HeadTwoCommitsPattern
from django.db import transaction
from django.core.mail import send_mail
from django.utils import timezone
from django.conf import settings
from django.urls import reverse
from user_profile.models import User
import datetime


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
                            'create': 'api/v1/company/registration/users/create/',
                            'confirm': 'api/v1/company/registration/users/confirm/',
                            'rollback': 'api/v1/company/registration/users/rollback/'
                        },
                    }
                )
                head.two_commits_operation()

            refresh = RefreshToken.for_user(user)
            refresh.payload.update({
                'user_id': user.id,
                'email': user.email,
            })
            return Response(
                {
                    'refresh_token': str(refresh),
                    'access_token': str(refresh.access_token)
                }, status=status.HTTP_201_CREATED)
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
            raise AuthenticationFailed(
                {'error': 'Incorrect username or password'})
        refresh = RefreshToken.for_user(user)
        refresh.payload.update({
            'user_id': user.id,
            'email': user.email
        })
        return Response(
            {
                'refresh_token': str(refresh),
                'access_token': str(refresh.access_token)
            }, status=status.HTTP_200_OK)


class LogoutAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    @extend_schema(request=None, responses=response_for_logout)
    def post(self, request):
        refresh_token = request.data.get('refresh_token')
        if not refresh_token:
            raise ValidationError({'error': 'Refresh token is required'})
        put_token_on_blacklist(refresh_token)
        return Response({'detail': 'Successfully logged out'}, status=status.HTTP_205_RESET_CONTENT)


class UpdateImportantDataAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    @extend_schema(request=request_for_important_info, responses=response_for_important_data)
    def patch(self, request):
        data_to_update = request.data.get('data_to_update')
        old_refresh_token = request.data.get("refresh_token")
        current_password = request.data.get('password')
        self._validate_update_request(
            current_password, data_to_update, old_refresh_token, request)
        serializer = UserImportantSerializer(
            instance=request.user, data=data_to_update, partial=True)
        if serializer.is_valid():
            put_token_on_blacklist(old_refresh_token)
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response(
                {
                    'refresh_token': str(refresh),
                    'access_token': str(refresh.access_token)
                }, status=status.HTTP_200_OK)

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


@extend_schema(
    tags=['EmailVerify']
)
class EmailVerifyView(APIView):
    @extend_schema(request=UserEmailSerializer, responses='200')
    def post(self, request):
        serializer = UserEmailSerializer(data=request.data)
        user_email = serializer.initial_data.get('email', None)
        user = User.objects.get(email=user_email)

        token = AccessToken.for_user(user)
        token.set_exp(lifetime=timezone.timedelta(seconds=60))

        verification_url = 'http://localhost:8000' + reverse('is_email_verified',
                                                             kwargs={'token': str(token)})
        send_mail(
            subject='Verify your email!',
            message=f'To verify your email on QuickHub follow the link:\n{
                verification_url}',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=['pridanov_ali@mail.ru'],  # [user_email],
            auth_user=settings.EMAIL_HOST_USER,
            auth_password=settings.EMAIL_HOST_PASSWORD
        )

        return Response({'detail': 'We send mail on your email to verification'}, status=status.HTTP_200_OK)


@extend_schema(
    tags=['IsEmailVerified']
)
class IsEmailVerifiedView(APIView):
    @extend_schema(request=['coded_user_id', 'token'], responses=[200])
    def get(self, request, token):
        decoded_token = AccessToken(token=token)

        user_id = decoded_token.payload['user_id']
        user = User.objects.get(id=user_id)

        if 'exp' in decoded_token.payload and timezone.now() > timezone.make_aware(datetime.datetime.fromtimestamp(decoded_token['exp'])):
            return Response({'error': 'token expired. Send new mail'}, status=status.HTTP_400_BAD_REQUEST)

        user.email_verified = True
        user.save()
        return Response({'detail': 'Email verified'}, status=status.HTTP_200_OK)
