from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from apps.auth.views import (
    LoginView,
    LogoutView,
    MFAVerifyView,
    MFARecoveryView,
    PasswordResetRequestView,
    PasswordResetConfirmView,
)

urlpatterns = [
    path('login/',         LoginView.as_view(),        name='auth-login'),
    path('logout/',        LogoutView.as_view(),        name='auth-logout'),
    path('token/refresh/', TokenRefreshView.as_view(),  name='auth-token-refresh'),

    path('mfa/verify/',    MFAVerifyView.as_view(),     name='auth-mfa-verify'),
    path('mfa/recovery/',  MFARecoveryView.as_view(),   name='auth-mfa-recovery'),

    path('password/reset/',         PasswordResetRequestView.as_view(), name='auth-password-reset'),
    path('password/reset/confirm/', PasswordResetConfirmView.as_view(), name='auth-password-reset-confirm'),
]