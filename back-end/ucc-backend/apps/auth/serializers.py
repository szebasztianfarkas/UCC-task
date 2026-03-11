from rest_framework import serializers


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True, max_length=128)


class MFAVerifySerializer(serializers.Serializer):
    code      = serializers.CharField(min_length=6, max_length=6)
    mfa_token = serializers.CharField(max_length=128)


class MFARecoverySerializer(serializers.Serializer):
    code      = serializers.CharField(max_length=32)
    mfa_token = serializers.CharField(max_length=128)


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=254)


class PasswordResetConfirmSerializer(serializers.Serializer):
    token        = serializers.CharField(max_length=128)
    new_password = serializers.CharField(min_length=10, max_length=128, write_only=True)