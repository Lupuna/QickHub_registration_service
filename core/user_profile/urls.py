from django.urls import path, include
from rest_framework.routers import DefaultRouter

from user_profile.views import ProfileAPIVewSet, ImageAPIView

router = DefaultRouter()
router.register(r'profile', ProfileAPIVewSet)

urlpatterns = [
    path('v1/', include(router.urls)),
    path('load-image/', ImageAPIView.as_view(), name='load_image')
]