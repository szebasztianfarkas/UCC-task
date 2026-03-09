import secrets
from django.db import models
from django.conf import settings
from django.utils import timezone


class MFADevice(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='mfa_device',
    )
    secret = models.CharField(max_length=64)
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'MFA Device'

    def __str__(self):
        return f'MFA device for {self.user}'


class MFARecoveryCode(models.Model):
    device = models.ForeignKey(
        MFADevice,
        on_delete=models.CASCADE,
        related_name='recovery_codes',
    )
    code = models.CharField(max_length=32, unique=True)
    used = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'MFA Recovery Code'

    def __str__(self):
        return f'Recovery code for {self.device.user} (used={self.used})'


class PendingMFAToken(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='pending_mfa_tokens',
    )
    token = models.CharField(max_length=64, unique=True, default=secrets.token_urlsafe)
    expires_at = models.DateTimeField()

    class Meta:
        verbose_name = 'Pending MFA Token'

    def is_valid(self):
        return timezone.now() < self.expires_at

    def __str__(self):
        return f'Pending MFA token for {self.user}'


class PasswordResetToken(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='password_reset_tokens',
    )
    token = models.CharField(max_length=64, unique=True, default=secrets.token_urlsafe)
    expires_at = models.DateTimeField()
    used = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Password Reset Token'

    def is_valid(self):
        return not self.used and timezone.now() < self.expires_at

    def __str__(self):
        return f'Password reset token for {self.user}'