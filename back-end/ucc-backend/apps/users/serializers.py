from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    is_helpdesk_agent = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'bio', 'is_active', 'date_joined', 'has_mfa', 'is_helpdesk_agent']
        read_only_fields = ['id', 'is_active', 'date_joined', 'has_mfa', 'is_helpdesk_agent']

    def get_has_mfa(self, obj):
        try:
            return obj.mfa_device.is_active
        except Exception:
            return False

    def get_is_helpdesk_agent(self, obj):
        return obj.groups.filter(name='helpdesk_agent').exists()

class MeSerializer(UserSerializer):
    has_mfa = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ['has_mfa']

    def get_has_mfa(self, obj):
        return hasattr(obj, "mfa_device")

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
    email_token = serializers.CharField()


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, min_length=8)
    totp_code    = serializers.CharField(required=False, allow_blank=True, write_only=True)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'bio', 'is_active', 'date_joined']
        read_only_fields = ['id', 'is_active', 'date_joined']