import pyotp
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

User = get_user_model()


class UserNotFound(Exception):
    pass


class UserService:
    @staticmethod
    def get_all_users(include_inactive: bool = False):
        qs = User.objects.all()
        if not include_inactive:
            qs = qs.filter(is_active=True)
        return qs

    @staticmethod
    def get_user_by_id(user_id: int) -> User:
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            raise UserNotFound(f'User {user_id} does not exist.')


    @staticmethod
    def create_user(*, username: str, email: str, password: str, **extra) -> User:
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError('A user with that email already exists.')
        return User.objects.create_user(
            username=username,
            email=email,
            password=password,
            **extra,
        )

    @staticmethod
    def update_user(user: User, **fields) -> User:
        allowed = {'bio'}
        for attr, value in fields.items():
            if attr not in allowed:
                raise ValidationError(f'Field {attr!r} cannot be updated here.')
            setattr(user, attr, value)
        user.save(update_fields=list(fields.keys()))
        return user

    @staticmethod
    def deactivate_user(user: User) -> None:
        user.deactivate()

    @staticmethod
    def change_password(
        user: User,
        old_password: str,
        new_password: str,
        totp_code: str = '',
    ) -> None:
        has_mfa = False
        try:
            device  = user.mfa_device
            has_mfa = device.is_active
        except Exception:
            pass

        if has_mfa:
            if not totp_code:
                raise ValidationError('An authenticator code is required.')
            totp = pyotp.TOTP(device.secret)
            if not totp.verify(totp_code.strip(), valid_window=1):
                raise ValidationError('Invalid authenticator code.')

        if not user.check_password(old_password):
            raise ValidationError('Current password is incorrect.')

        validate_password(new_password, user=user)
        user.set_password(new_password)
        user.save(update_fields=['password'])

        UserService._blacklist_all_tokens(user)

    @staticmethod
    def _blacklist_all_tokens(user) -> None:
        try:
            from rest_framework_simplejwt.token_blacklist.models import OutstandingToken
            from rest_framework_simplejwt.tokens import RefreshToken as RT
            tokens = OutstandingToken.objects.filter(user=user, blacklistedtoken__isnull=True)
            for outstanding in tokens:
                try:
                    RT(outstanding.token).blacklist()
                except Exception:
                    pass
        except Exception:
            pass