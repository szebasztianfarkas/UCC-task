import pyotp
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone

from apps.auth.models import EmailChangeRequest

User = get_user_model()

TOKEN_TTL = timedelta(hours=1)


class EmailChangeService:
    @staticmethod
    def initiate(user, new_email: str) -> dict:
        if User.objects.filter(email__iexact=new_email).exclude(pk=user.pk).exists():
            raise ValidationError('That email address is already in use.')

        if user.email.lower() == new_email.lower():
            raise ValidationError('That is already your current email address.')

        EmailChangeRequest.objects.filter(user=user, status=EmailChangeRequest.PENDING).delete()

        request = EmailChangeRequest.objects.create(
            user=user,
            new_email=new_email,
            expires_at=timezone.now() + TOKEN_TTL,
        )

        confirm_url = (
            f"{settings.FRONTEND_URL}/profile"
            f"?email_token={request.token}"
        )

        if (settings.DEBUG):
            print(f'Email confirm link for {user.username}: {confirm_url}')
        else:
            send_mail(
                subject='Confirm your new email address',
                message=(
                    f'Hi {user.username},\n\n'
                    f'Click the link below to confirm your new email address.\n'
                    f'This link expires in 1 hour.\n\n'
                    f'{confirm_url}\n\n'
                    f'If you did not request this change, you can safely ignore this email.\n'
                    f'Your email will not be changed unless you click the link above.'
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[new_email],
                fail_silently=True,
            )
        return

    @staticmethod
    def confirm_with_email_token(user, email_token: str) -> None:
        request = EmailChangeService._get_valid_request(user, email_token)
        EmailChangeService._apply(request)

    @staticmethod
    def _get_valid_request(user, token: str) -> EmailChangeRequest:
        try:
            request = EmailChangeRequest.objects.get(token=token, user=user)
        except EmailChangeRequest.DoesNotExist:
            raise ValidationError('Invalid or expired email change request.')

        if not request.is_valid():
            raise ValidationError('This email change request has expired. Please start again.')

        return request

    @staticmethod
    def _apply(request: EmailChangeRequest) -> None:
        user = request.user
        user.email = request.new_email
        user.save(update_fields=['email'])

        request.status = EmailChangeRequest.CONFIRMED
        request.save(update_fields=['status'])