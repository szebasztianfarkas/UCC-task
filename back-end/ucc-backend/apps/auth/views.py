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
from config.throttles import LoginRateThrottle, PasswordResetThrottle, MFAThrottle
from config.logging import log_security_event


def _validation_error_response(e):
    message = e.message if hasattr(e, 'message') else str(e)
    return Response({'detail': message}, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes  = [AllowAny]
    throttle_classes    = [LoginRateThrottle]

    @extend_schema(
        tags=['Auth'], summary='Login',
        request=LoginSerializer,
        responses={200: OpenApiResponse(description='Tokens or MFA challenge.'),
                   401: OpenApiResponse(description='Invalid credentials.')},
        auth=[],
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            result = AuthService.login(**serializer.validated_data)
        except ValidationError as e:
            log_security_event('login_failure', request,
                               user=serializer.validated_data.get('username'),
                               detail=str(e), level='warning')
            return Response({'detail': e.message}, status=status.HTTP_401_UNAUTHORIZED)

        if result.get('mfa_required'):
            log_security_event('login_mfa_required', request, user=result.get('user'))
            return Response({'mfa_required': True, 'mfa_token': result['mfa_token']})

        log_security_event('login_success', request, user=result['user'])
        return Response({
            'access':  result['access'],
            'refresh': result['refresh'],
            'user':    UserSerializer(result['user']).data,
        })


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=['Auth'], summary='Logout',
        request={'application/json': {'type': 'object',
                 'properties': {'refresh': {'type': 'string'}}}},
        responses={204: OpenApiResponse(description='Logged out.')},
    )
    def post(self, request):
        refresh_token = request.data.get('refresh', '')
        AuthService.logout(refresh_token)
        log_security_event('logout', request, user=request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(tags=['Auth'], summary='Get current user',
                   responses={200: UserSerializer})
    def get(self, request):
        return Response(UserSerializer(request.user).data)


class MFAVerifyView(APIView):
    permission_classes = [AllowAny]
    throttle_classes   = [MFAThrottle]

    @extend_schema(
        tags=['Auth — MFA'], summary='Verify TOTP code',
        request=MFAVerifySerializer,
        responses={200: OpenApiResponse(description='MFA verified.'),
                   400: OpenApiResponse(description='Invalid code.')},
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
            log_security_event('mfa_failure', request,
                               detail='TOTP verify failed', level='warning')
            return _validation_error_response(e)

        log_security_event('mfa_success', request, user=result['user'])
        return Response({
            'access':  result['access'],
            'refresh': result['refresh'],
            'user':    UserSerializer(result['user']).data,
        })


class MFARecoveryView(APIView):
    permission_classes = [AllowAny]
    throttle_classes   = [MFAThrottle]

    @extend_schema(
        tags=['Auth — MFA'], summary='Verify recovery code',
        request=MFARecoverySerializer,
        responses={200: OpenApiResponse(description='Recovery code accepted.'),
                   400: OpenApiResponse(description='Invalid code.')},
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
            log_security_event('mfa_failure', request,
                               detail='Recovery code verify failed', level='warning')
            return _validation_error_response(e)

        log_security_event('mfa_recovery_success', request, user=result['user'])
        return Response({
            'access':  result['access'],
            'refresh': result['refresh'],
            'user':    UserSerializer(result['user']).data,
        })


class PasswordResetRequestView(APIView):
    permission_classes = [AllowAny]
    throttle_classes   = [PasswordResetThrottle]

    @extend_schema(
        tags=['Auth — Password Reset'], summary='Request password reset',
        request=PasswordResetRequestSerializer,
        responses={204: OpenApiResponse(description='Reset email sent (if account exists).')},
        auth=[],
    )
    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        PasswordResetService.request_reset(email=serializer.validated_data['email'])
        log_security_event('password_reset_req', request,
                           detail=serializer.validated_data['email'])
        return Response(status=status.HTTP_204_NO_CONTENT)


class PasswordResetConfirmView(APIView):
    permission_classes = [AllowAny]
    throttle_classes   = [PasswordResetThrottle]

    @extend_schema(
        tags=['Auth — Password Reset'], summary='Confirm password reset',
        request=PasswordResetConfirmSerializer,
        responses={204: OpenApiResponse(description='Password updated.'),
                   400: OpenApiResponse(description='Invalid token.')},
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

        log_security_event('password_reset_confirmed', request)
        return Response(status=status.HTTP_204_NO_CONTENT)