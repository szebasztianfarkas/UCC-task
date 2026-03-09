from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError, ObjectDoesNotExist

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
        for attr, value in fields.items():
            setattr(user, attr, value)
        user.save(update_fields=list(fields.keys()))
        return user

    @staticmethod
    def deactivate_user(user: User) -> None:
        user.deactivate()

    @staticmethod
    def change_password(user: User, old_password: str, new_password: str) -> None:
        if not user.check_password(old_password):
            raise ValidationError('Current password is incorrect.')
        validate_password(new_password, user=user)
        user.set_password(new_password)
        user.save(update_fields=['password'])