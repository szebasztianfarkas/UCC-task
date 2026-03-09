import pyotp

from django.core.exceptions import ValidationError
from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken

from apps.auth.models import PendingMFAToken, MFARecoveryCode


class MFAService:
    @staticmethod
    def _resolve_pending_token(mfa_token: str):
        try:
            pending = PendingMFAToken.objects.select_related('user').get(token=mfa_token)
        except PendingMFAToken.DoesNotExist:
            raise ValidationError('Invalid or expired MFA session.')

        if not pending.is_valid():
            pending.delete()
            raise ValidationError('MFA session has expired. Please sign in again.')

        user = pending.user
        pending.delete()
        return user

    @staticmethod
    def _issue_tokens(user) -> dict:
        refresh = RefreshToken.for_user(user)
        return {
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': user,
        }

    @staticmethod
    def verify_totp(mfa_token: str, code: str) -> dict:
        user = MFAService._resolve_pending_token(mfa_token)

        try:
            device = user.mfa_device
        except Exception:
            raise ValidationError('No MFA device found for this account.')

        totp = pyotp.TOTP(device.secret)
        if not totp.verify(code, valid_window=1):
            raise ValidationError('Invalid authentication code.')

        return MFAService._issue_tokens(user)

    @staticmethod
    def verify_recovery_code(mfa_token: str, code: str) -> dict:
        user = MFAService._resolve_pending_token(mfa_token)

        try:
            recovery = MFARecoveryCode.objects.get(
                device__user=user,
                code=code.upper().strip(),
                used=False,
            )
        except MFARecoveryCode.DoesNotExist:
            raise ValidationError('Invalid or already used recovery code.')

        recovery.used = True
        recovery.save(update_fields=['used'])

        return MFAService._issue_tokens(user)