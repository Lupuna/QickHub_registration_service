from django.contrib.auth import authenticate
from rest_framework.exceptions import ValidationError, AuthenticationFailed
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from jwt_registration.serializers import UserSerializer


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