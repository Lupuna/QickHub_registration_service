import requests
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
from jwt_registration.serializers import RegistrationSerializer, EmailVerifySerializer, SetNewPasswordSerializer, EmailUpdateSerializer
from jwt_registration.utils import put_token_on_blacklist, CreateTwoCommitsPattern, UpdateTwoCommitsPattern
from django.db import transaction
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from django.shortcuts import redirect
from user_profile.models import User
from jwt_registration.tasks import send_celery_mail
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature


class RegistrationAPIView(APIView):
    @extend_schema(request=RegistrationSerializer, responses=response_for_registration)
    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            with transaction.atomic():
                user = serializer.save()
                create = CreateTwoCommitsPattern(
                    data={
                        'email': user.email,
                    },
                    service='company'
                )
                create.two_commits_operation()

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

    @extend_schema(request=request_for_logout, responses=response_for_logout)
    def post(self, request):
        refresh_token = request.data.get('refresh_token')
        if not refresh_token:
            raise ValidationError({'error': 'Refresh token is required'})
        put_token_on_blacklist(refresh_token)
        return Response({'detail': 'Successfully logged out'}, status=status.HTTP_205_RESET_CONTENT)


class PasswordRecoveryMailAPIView(APIView):
    @extend_schema(request=request_for_password_recovery_mail, responses=response_for_password_recovery_mail)
    def post(self, request):
        user_email = request.data.get('email')
        if not user_email:
            return Response({'error': 'Provide email adress for sending mail with password recovery instructions'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=user_email)
        except User.DoesNotExist:
            return Response({'error': 'Incorrect email'}, status=status.HTTP_400_BAD_REQUEST)

        token_ser = URLSafeTimedSerializer(
            secret_key=settings.SECRET_KEY)
        token = token_ser.dumps(
            {'user_email': user.email}, salt='password-recovery')

        recovery_url = settings.REGISTRATION_SERVICE_URL + \
            reverse('new_password_confirm', kwargs={'token': token})
        send_celery_mail.delay(
            subject='Password recovery',
            message=f'You can recovery uor password following this link\n{
                recovery_url}',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user_email],
            auth_user=settings.EMAIL_HOST_USER,
            auth_password=settings.EMAIL_HOST_PASSWORD
        )

        return Response({'detail': 'We sent mail on your email to recovery your password'}, status=status.HTTP_200_OK)


class PasswordRecoveryConfirmAPIView(APIView):
    @extend_schema(request=SetNewPasswordSerializer, responses=response_for_password_recovery_confirm)
    def post(self, request, token):
        try:
            decoded_token_ser = URLSafeTimedSerializer(
                secret_key=settings.SECRET_KEY)
            decoded_token = decoded_token_ser.loads(
                token, salt='password-recovery', max_age=60)
        except SignatureExpired:
            return Response({'error': 'Token expired'}, status=status.HTTP_406_NOT_ACCEPTABLE)
        except BadSignature:
            return Response({'error': 'Invalid token'}, status=status.HTTP_406_NOT_ACCEPTABLE)

        user_email = decoded_token['user_email']
        data = {
            'email': user_email,
            'password': request.data.get('pas1', None),
            'password2': request.data.get('pas2', None),
        }
        serializer = SetNewPasswordSerializer(data=data)
        if serializer.is_valid():
            new_password = serializer.validated_data['password']
            user = User.objects.get(email=user_email)
            user.set_password(new_password)
            user.save()
            return Response({'detail': 'Password recovered successfully'}, status=status.HTTP_200_OK)

        return Response({'error': 'Incorrect data'}, status=status.HTTP_400_BAD_REQUEST)


class EmailVerifyView(APIView):
    # permission_classes = (IsAuthenticated, )

    @extend_schema(request=EmailVerifySerializer, responses=response_for_email_verify)
    def post(self, request):
        serializer = EmailVerifySerializer(data=request.data)
        if serializer.is_valid():
            user_email = serializer.validated_data['email']
            token_ser = URLSafeTimedSerializer(
                secret_key=settings.SECRET_KEY)
            token = token_ser.dumps(
                {'user_email': user_email}, salt='email-verify')

            verification_url = settings.REGISTRATION_SERVICE_URL + \
                reverse('is_email_verified', kwargs={'token': token})
            send_celery_mail.delay(
                subject='Verify your email!',
                message=f'To verify your email on QuickHub follow the link:\n{
                    verification_url}',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user_email],
                auth_user=settings.EMAIL_HOST_USER,
                auth_password=settings.EMAIL_HOST_PASSWORD
            )

            return Response({'detail': 'We sent mail on your email to verification'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class IsEmailVerifiedView(APIView):
    # permission_classes = (IsAuthenticated, )

    @extend_schema(request=request_for_is_email_verified, responses=response_for_is_email_verified)
    def get(self, request, token):
        try:
            decoded_token_ser = URLSafeTimedSerializer(
                secret_key=settings.SECRET_KEY)
            decoded_token = decoded_token_ser.loads(
                token, salt='email-verify', max_age=60*60)
        except SignatureExpired:
            return Response({'error': 'Token expired'}, status=status.HTTP_406_NOT_ACCEPTABLE)
        except BadSignature:
            return Response({'error': 'Invalid token'}, status=status.HTTP_406_NOT_ACCEPTABLE)

        user_email = decoded_token['user_email']
        user = User.objects.get(email=user_email)

        user.email_verified = True
        user.save()

        return Response({'detail': 'Email verified succesfully!'}, status=status.HTTP_200_OK)


class EmailUpdateAPIView(APIView):
    permission_classes = (IsAuthenticated, )

    @extend_schema(request=EmailUpdateSerializer, responses=response_for_email_update)
    def post(self, request):
        serializer = EmailUpdateSerializer(
            instance=request.user, data=request.data)
        if serializer.is_valid():
            with transaction.atomic():
                old_email = request.user.email
                user = serializer.save()
                update = UpdateTwoCommitsPattern(
                    data={'email': old_email, 'new_email': user.email}, service='company')
                update.two_commits_operation()
            return Response({'detail': 'Email updated successfully'}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
