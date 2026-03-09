from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.core.exceptions import ValidationError
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample

from apps.auth.serializers import (
    LoginSerializer,
    MFAVerifySerializer,
    MFARecoverySerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
)
from apps.auth.services.auth_service import AuthService
from apps.auth.services.mfa_service import MFAService
from apps.auth.services.password_reset_service import PasswordResetService
from apps.users.serializers import UserSerializer


def _validation_error_response(e):
    message = e.message if hasattr(e, 'message') else str(e)
    return Response({'detail': message}, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        tags=['Auth'],
        summary='Login',
        description=(
            'Step 1 of authentication. Returns full JWT tokens if the user has no MFA device, '
            'or a short-lived `mfa_token` if MFA is enabled.'
        ),
        request=LoginSerializer,
        responses={
            200: OpenApiResponse(description='Authenticated — returns tokens and user, or mfa_required flag.'),
            401: OpenApiResponse(description='Invalid credentials or account disabled.'),
        },
        examples=[
            OpenApiExample('No MFA', value={
                'access': 'eyJ...', 'refresh': 'eyJ...', 'user': {'id': 1, 'username': 'alice'}
            }),
            OpenApiExample('MFA required', value={
                'mfa_required': True, 'mfa_token': 'abc123xyz'
            }),
        ],
        auth=[],
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            result = AuthService.login(**serializer.validated_data)
        except ValidationError as e:
            return Response({'detail': e.message}, status=status.HTTP_401_UNAUTHORIZED)
        if result.get('mfa_required'):
            return Response({'mfa_required': True, 'mfa_token': result['mfa_token']})
        return Response({
            'access': result['access'],
            'refresh': result['refresh'],
            'user': UserSerializer(result['user']).data,
        })


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=['Auth'],
        summary='Logout',
        description='Blacklists the provided refresh token, invalidating the session.',
        request={'application/json': {'type': 'object', 'properties': {'refresh': {'type': 'string'}}}},
        responses={204: OpenApiResponse(description='Logged out successfully.')},
    )
    def post(self, request):
        refresh_token = request.data.get('refresh', '')
        AuthService.logout(refresh_token)
        return Response(status=status.HTTP_204_NO_CONTENT)

class MFAVerifyView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        tags=['Auth — MFA'],
        summary='Verify TOTP code',
        description=(
            'Step 2a of authentication. Exchanges a valid `mfa_token` and a 6-digit '
            'TOTP code from an authenticator app for full JWT tokens.'
        ),
        request=MFAVerifySerializer,
        responses={
            200: OpenApiResponse(description='MFA verified — returns tokens and user.'),
            400: OpenApiResponse(description='Invalid or expired MFA session, or wrong code.'),
        },
        auth=[],
    )
    def post(self, request):
        serializer = MFAVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            result = MFAService.verify_totp(
                mfa_token=serializer.validated_data['mfa_token'],
                code=serializer.validated_data['code'],
            )
        except ValidationError as e:
            return _validation_error_response(e)
        return Response({
            'access': result['access'],
            'refresh': result['refresh'],
            'user': UserSerializer(result['user']).data,
        })


class MFARecoveryView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        tags=['Auth — MFA'],
        summary='Verify recovery code',
        description=(
            'Step 2b of authentication. Exchanges a valid `mfa_token` and a one-time '
            'recovery code for full JWT tokens. The recovery code is marked as used.'
        ),
        request=MFARecoverySerializer,
        responses={
            200: OpenApiResponse(description='Recovery code accepted — returns tokens and user.'),
            400: OpenApiResponse(description='Invalid, expired, or already used recovery code.'),
        },
        auth=[],
    )
    def post(self, request):
        serializer = MFARecoverySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            result = MFAService.verify_recovery_code(
                mfa_token=serializer.validated_data['mfa_token'],
                code=serializer.validated_data['code'],
            )
        except ValidationError as e:
            return _validation_error_response(e)
        return Response({
            'access': result['access'],
            'refresh': result['refresh'],
            'user': UserSerializer(result['user']).data,
        })


class PasswordResetRequestView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        tags=['Auth — Password Reset'],
        summary='Request password reset',
        description=(
            'Sends a password reset email if the address is associated with an active account. '
            'Always returns 204 regardless of whether the email exists, to prevent user enumeration.'
        ),
        request=PasswordResetRequestSerializer,
        responses={204: OpenApiResponse(description='Reset email sent (if account exists).')},
        auth=[],
    )
    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        PasswordResetService.request_reset(email=serializer.validated_data['email'])
        return Response(status=status.HTTP_204_NO_CONTENT)


class PasswordResetConfirmView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        tags=['Auth — Password Reset'],
        summary='Confirm password reset',
        description='Validates the reset token and sets the new password. The token is single-use.',
        request=PasswordResetConfirmSerializer,
        responses={
            204: OpenApiResponse(description='Password updated successfully.'),
            400: OpenApiResponse(description='Invalid, expired, or already used token.'),
        },
        auth=[],
    )
    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            PasswordResetService.confirm_reset(
                token=serializer.validated_data['token'],
                new_password=serializer.validated_data['new_password'],
            )
        except ValidationError as e:
            return _validation_error_response(e)
        return Response(status=status.HTTP_204_NO_CONTENT)