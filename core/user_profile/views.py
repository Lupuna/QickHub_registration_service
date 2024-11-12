from django.conf import settings
from django.core.cache import cache
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import ListAPIView
from rest_framework.mixins import RetrieveModelMixin, UpdateModelMixin
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet, ReadOnlyModelViewSet
from jwt_registration.utils import CookieJWTAuthentication

from core.swagger_info import response_for_upload_image, request_for_upload_image
from user_profile.models import User
from user_profile.serializers import ProfileUserSerializer, ImageSerializer, ProfileUserForCompanySerializer


class ProfileAPIVewSet(GenericViewSet, RetrieveModelMixin, UpdateModelMixin):
    serializer_class = ProfileUserSerializer
    queryset = User.objects.all().select_related('customization').prefetch_related('links')
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        user = self.kwargs.get('pk')
        cache_key = settings.USER_PROFILE_CACHE_KEY.format(user=user)
        instance = cache.get(cache_key)
        if instance is None:
            instance = super().get_object()
            cache.set(cache_key, instance, timeout=settings.CACHE_LIVE_TIME)
        return instance

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        user = self.kwargs.get('pk')
        cache_key = settings.USER_PROFILE_CACHE_KEY.format(user=user)
        cache.delete(cache_key)
        return response


class ImageAPIView(APIView):
    permission_classes = (IsAuthenticated,)
    parser_classes = (MultiPartParser,)

    @extend_schema(request=request_for_upload_image, responses=response_for_upload_image)
    def post(self, request):
        user_id = CookieJWTAuthentication().get_user_id_in_jwt_token(request)
        image = request.data.get('image')
        self._validate_update_request(image)
        serializer = ImageSerializer(data={'image': image, 'user': user_id})
        if serializer.is_valid():
            serializer.save()
            return Response({'response': 'ok'}, status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def _validate_update_request(image):
        if not image:
            raise ValidationError({'error': 'image is required'})


@extend_schema(
    tags=["User for company"]
    )
class ProfileCompanyAPIView(ListAPIView):
    serializer_class = ProfileUserForCompanySerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        emails = self.request.data.get('emails', [])
        return User.objects.prefetch_related('links').filter(email__in=emails).only(
            'id', 'first_name', 'last_name',
            'phone', 'image_identifier', 'date_joined', 'links'
        )
