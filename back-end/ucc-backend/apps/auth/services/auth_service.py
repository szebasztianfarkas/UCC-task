import secrets
from datetime import timedelta

from django.contrib.auth import authenticate, get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken

from apps.auth.models import MFADevice, PendingMFAToken

User = get_user_model()

MFA_TOKEN_TTL = timedelta(minutes=10)


class AuthService:
    @staticmethod
    def login(username: str, password: str) -> dict:
        user = authenticate(username=username, password=password)
        if user is None:
            raise ValidationError('Invalid credentials.')
        if not user.is_active:
            raise ValidationError('This account is disabled.')

        try:
            device = user.mfa_device
            if device.is_active:
                pending = PendingMFAToken.objects.create(
                    user=user,
                    expires_at=timezone.now() + MFA_TOKEN_TTL,
                )
                return {'mfa_required': True, 'mfa_token': pending.token}
        except MFADevice.DoesNotExist:
            pass

        return AuthService._issue_tokens(user)

    @staticmethod
    def logout(refresh_token: str) -> None:
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except Exception:
            pass

    @staticmethod
    def _issue_tokens(user) -> dict:
        refresh = RefreshToken.for_user(user)
        return {
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': user,
        }