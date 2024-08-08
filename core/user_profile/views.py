from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import RetrieveModelMixin, UpdateModelMixin
from user_profile.serializers import ProfileUserSerializer
from user_profile.models import User


class ProfileAPIVewSet(GenericViewSet, RetrieveModelMixin, UpdateModelMixin):
    serializer_class = ProfileUserSerializer
    queryset = User.objects.all().select_related('customization').prefetch_related('links')
    permission_classes = (IsAuthenticated, )
