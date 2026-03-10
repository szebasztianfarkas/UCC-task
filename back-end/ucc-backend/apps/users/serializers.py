from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'bio', 'is_active', 'date_joined']
        read_only_fields = ['id', 'is_active', 'date_joined']

class MeSerializer(UserSerializer):
    has_mfa = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ['has_mfa']

    def get_has_mfa(self, obj):
        return obj.mfa_device is not None

class CreateUserSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    email    = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)
    bio      = serializers.CharField(required=False, allow_blank=True, default='')

    def validate_username(self, value):
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError('A user with that username already exists.')
        return value

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError('A user with that email already exists.')
        return value


class UpdateUserSerializer(serializers.Serializer):
    bio = serializers.CharField(required=False, allow_blank=True)


class EmailChangeInitiateSerializer(serializers.Serializer):
    new_email = serializers.EmailField()


class EmailChangeConfirmSerializer(serializers.Serializer):
    request_token = serializers.CharField(required=False, allow_blank=True)
    totp_code     = serializers.CharField(required=False, allow_blank=True)
    email_token   = serializers.CharField(required=False, allow_blank=True)

    def validate(self, data):
        has_mfa   = data.get('request_token') and data.get('totp_code')
        has_email = bool(data.get('email_token'))
        if not has_mfa and not has_email:
            raise serializers.ValidationError(
                'Provide either (request_token + totp_code) or email_token.'
            )
        return data


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, min_length=8)