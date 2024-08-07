from django.urls import path
from jwt_registration.views import LoginAPIView, RegistrationAPIView, LogoutAPIView
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('v1/login/', LoginAPIView.as_view(), name='login'),
    path('v1/registration/', RegistrationAPIView.as_view(), name='registration'),
    path('v1/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('v1/token/logout/', LogoutAPIView.as_view(), name='logout'),
]
