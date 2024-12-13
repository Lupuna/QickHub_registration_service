from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView

from jwt_registration.views import (
    LoginAPIView, RegistrationAPIView, LogoutAPIView, UpdateImportantDataAPIView, EmailVerifyView, IsEmailVerifiedView
)

urlpatterns = [
    path('v1/login/', LoginAPIView.as_view(), name='login'),
    path('v1/registration/', RegistrationAPIView.as_view(), name='registration'),
    path('v1/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('v1/token/validate/', TokenVerifyView.as_view(), name='token_verify'),
    path('v1/logout/', LogoutAPIView.as_view(), name='logout'),
    path('v1/update-important-data/',
         UpdateImportantDataAPIView.as_view(), name='update_important_data'),
    path('v1/email-verify/', EmailVerifyView.as_view(), name='to_email_verify'),
    path('v1/is-email-verified/<str:token>/',
         IsEmailVerifiedView.as_view(), name='is_email_verified'),
]
