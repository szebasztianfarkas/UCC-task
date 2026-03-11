from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    has_mfa           = serializers.SerializerMethodField()
    is_helpdesk_agent = serializers.SerializerMethodField()

    class Meta:
        model  = User
        fields = ['id', 'username', 'email', 'bio',
                  'is_active', 'date_joined', 'has_mfa', 'is_helpdesk_agent']
        read_only_fields = fields

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
    username = serializers.CharField(max_length=150, min_length=3)
    email    = serializers.EmailField(max_length=254)
    password = serializers.CharField(write_only=True, min_length=10, max_length=128)
    bio      = serializers.CharField(required=False, allow_blank=True, default='', max_length=500)

    def validate_username(self, value):
        import re
        if not re.match(r'^[\w.@+-]+$', value):
            raise serializers.ValidationError('Username may only contain letters, digits, and @/./+/-/_')
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError('A user with that username already exists.')
        return value

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError('A user with that email already exists.')
        return value


class UpdateUserSerializer(serializers.Serializer):
    """Bio-only update — email is handled by the dedicated email-change flow."""
    bio = serializers.CharField(required=False, allow_blank=True, max_length=500)


class EmailChangeInitiateSerializer(serializers.Serializer):
    new_email = serializers.EmailField(max_length=254)


class EmailChangeConfirmSerializer(serializers.Serializer):
    """Email-link confirmation only."""
    email_token = serializers.CharField(max_length=128)


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True, max_length=128)
    new_password = serializers.CharField(write_only=True, min_length=10, max_length=128)
    totp_code    = serializers.CharField(required=False, allow_blank=True, write_only=True, max_length=10)