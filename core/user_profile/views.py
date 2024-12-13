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
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.decorators import action

import requests
from django.forms.models import model_to_dict
from core.swagger_info import response_for_upload_image, request_for_upload_image
from user_profile.models import User
from user_profile.serializers import ProfileUserSerializer, ImageSerializer, ProfileUserForCompanySerializer, ProfileUserForDepSerializer, DepartmentInfoSerializer


class ProfileAPIVewSet(GenericViewSet, RetrieveModelMixin, UpdateModelMixin):
    serializer_class = ProfileUserSerializer
    queryset = User.objects.all().select_related('customization', 'reminder',
                                                 'notification').prefetch_related('links')
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

    @action(methods=['get'], detail=False, url_path='users-info-by-company/(?P<company_pk>\d+)', url_name='get_users_by_company')
    def get_users_by_company(self, request, company_pk):
        url = settings.COMPANY_SERVICE_URL.format(
            f'api/v1/company/companies/{company_pk}/users-emails/')
        response = requests.get(url=url)
        if response.status_code != 200:
            return Response({'detail': "company info wasn't get"}, status=response.status_code)
        response_data = response.json()

        users_pos_deps = [(user.get('positions', None), user.get(
            'departments', None)) for user in response_data]
        emails = [user.get('email', None) for user in response_data]

        users = User.objects.filter(email__in=emails).prefetch_related('links')
        context = {'emails': emails, 'pos_deps': users_pos_deps}
        users_info = ProfileUserForCompanySerializer(
            users, many=True, context=context)

        return Response(users_info.data, status=status.HTTP_200_OK)

    @action(methods=['get'], detail=False, url_path='company/(?P<company_pk>\d+)/dep/(?P<dep_pk>\d+)', url_name='get_users_by_dep')
    def get_users_by_dep(self, request, company_pk, dep_pk):
        url = settings.COMPANY_SERVICE_URL.format(
            f'/api/v1/company/companies/{company_pk}/departments/{dep_pk}/')
        response = requests.get(url=url, )
        if response.status_code != 200:
            return Response({"error": "info wasn't get"}, status=response.status_code)
        department_data = response.json()

        users_emails = [user['email'] for user in department_data['users']]
        users = User.objects.filter(email__in=users_emails)
        users_info = [model_to_dict(
            user, fields=ProfileUserForDepSerializer.Meta.fields) for user in users]

        for user in department_data['users']:
            for user_info in users_info:
                if user_info['email'] == user['email']:
                    user.update(user_info)
                    break

        department_ser = DepartmentInfoSerializer(department_data)

        return Response(department_ser.data, status=status.HTTP_200_OK)

    @action(methods=['get'], detail=False, url_path='company/(?P<company_pk>\d+)/deps', url_name='get_users_by_deps')
    def get_users_by_deps(self, request, company_pk):
        url = settings.COMPANY_SERVICE_URL.format(
            f'/api/v1/company/companies/{company_pk}/departments/')
        response = requests.get(url=url, )
        if response.status_code != 200:
            return Response({"error": "info wasn't get"}, status=response.status_code)
        departments_data = response.json()

        users_emails = []
        for department in departments_data:
            for user in department['users']:
                users_emails.append(user['email'])
        users = User.objects.filter(email__in=users_emails)
        users_info = [model_to_dict(
            user, fields=ProfileUserForDepSerializer.Meta.fields) for user in users]

        for department in departments_data:
            for user in department['users']:
                for user_info in users_info:
                    if user['email'] == user_info['email']:
                        user.update(user_info)
                        break

        departments_ser = DepartmentInfoSerializer(departments_data, many=True)

        return Response(departments_ser.data, status=status.HTTP_200_OK)


class ImageAPIView(APIView):
    permission_classes = (IsAuthenticated,)
    parser_classes = (MultiPartParser,)

    @extend_schema(request=request_for_upload_image, responses=response_for_upload_image)
    def post(self, request):
        user_id = self._get_user_id_in_jwt_token(request)
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

    @staticmethod
    def _get_user_id_in_jwt_token(request):
        auth = JWTAuthentication()
        header = auth.get_header(request)
        validated_token = auth.get_validated_token(auth.get_raw_token(header))
        user_id = validated_token.get('user_id')
        return user_id


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
