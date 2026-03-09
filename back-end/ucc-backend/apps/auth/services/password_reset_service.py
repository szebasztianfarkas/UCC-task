from datetime import timedelta

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone

from apps.auth.models import PasswordResetToken

User = get_user_model()

RESET_TOKEN_TTL = timedelta(hours=1)


class PasswordResetService:
    @staticmethod
    def request_reset(email: str) -> None:
        try:
            user = User.objects.get(email__iexact=email, is_active=True)
        except User.DoesNotExist:
            return

        PasswordResetToken.objects.filter(user=user, used=False).delete()

        reset_token = PasswordResetToken.objects.create(
            user=user,
            expires_at=timezone.now() + RESET_TOKEN_TTL,
        )

        reset_url = f"{settings.FRONTEND_URL}/reset-password?token={reset_token.token}"

        if (settings.DEBUG):
            print(f'Password reset link for {user.username}: {reset_url}')
        else:
            send_mail(
                subject='Reset your password',
                message=(
                    f'Hi {user.username},\n\n'
                    f'Click the link below to reset your password. '
                    f'This link expires in 1 hour.\n\n'
                    f'{reset_url}\n\n'
                    f'If you did not request this, you can safely ignore this email.'
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=True,
            )

    @staticmethod
    def confirm_reset(token: str, new_password: str) -> None:
        try:
            reset_token = PasswordResetToken.objects.select_related('user').get(token=token)
        except PasswordResetToken.DoesNotExist:
            raise ValidationError('Invalid or expired reset link.')

        if not reset_token.is_valid():
            raise ValidationError('This reset link has expired. Please request a new one.')

        user = reset_token.user

        try:
            validate_password(new_password, user=user)
        except ValidationError:
            raise

        user.set_password(new_password)
        user.save(update_fields=['password'])

        reset_token.used = True
        reset_token.save(update_fields=['used'])