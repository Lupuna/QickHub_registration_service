from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView

from jwt_registration.views import (
    LoginAPIView, RegistrationAPIView, LogoutAPIView, EmailVerifyView, IsEmailVerifiedView, PasswordRecoveryConfirmAPIView, PasswordRecoveryMailAPIView
)

urlpatterns = [
    path('v1/login/', LoginAPIView.as_view(), name='login'),
    path('v1/registration/', RegistrationAPIView.as_view(), name='registration'),
    path('v1/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('v1/token/validate/', TokenVerifyView.as_view(), name='token_verify'),
    path('v1/logout/', LogoutAPIView.as_view(), name='logout'),
    path('v1/email-verify/', EmailVerifyView.as_view(), name='to_email_verify'),
    path('v1/is-email-verified/<str:token>/',
         IsEmailVerifiedView.as_view(), name='is_email_verified'),
    path('v1/password-recovery/', PasswordRecoveryMailAPIView.as_view(),
         name='password_recovery'),
    path('v1/new-password-confirm/<str:token>/',
         PasswordRecoveryConfirmAPIView.as_view(), name='new_password_confirm'),
]
