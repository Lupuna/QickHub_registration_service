from django.contrib.auth import authenticate
from rest_framework.exceptions import ValidationError, AuthenticationFailed
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from jwt_registration.serializers import UserSerializer
from jwt_registration.utils import put_token_on_blacklist


class RegistrationAPIView(APIView):

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            refresh.payload.update({
                'user_id': user.id,
                'username': user.username,
            })

            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token)
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginAPIView(APIView):

    def post(self, request):
        data = request.data
        username = data.get('username')
        password = data.get('password')

        if username is None or password is None:
            raise ValidationError({'error': 'Username and password are required'})

        user = authenticate(username=username, password=password)
        if user is None:
            raise AuthenticationFailed({'error': 'Incorrect username or password'})
        refresh = RefreshToken.for_user(user)
        refresh.payload.update({
            'user_id': user.id,
            'username': user.username
        })

        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_200_OK)


class LogoutAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        refresh_token = request.data.get('refresh')
        if not refresh_token: raise ValidationError({'error': 'Refresh token is required'})
        put_token_on_blacklist(refresh_token)
        return Response({'detail': 'Successfully logged out'}, status=status.HTTP_205_RESET_CONTENT)


class UpdateImportantDataAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def patch(self, request):
        data_to_update = request.data.get('data_to_update')
        old_refresh_token = request.data.get("refresh_token")
        current_password = request.data.get('password')
        self._validate_update_request(current_password, data_to_update, old_refresh_token, request)
        serializer = UserSerializer(instance=request.user, data=data_to_update, partial=True)
        if serializer.is_valid():
            put_token_on_blacklist(old_refresh_token)
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token)
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
