from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from django.core.exceptions import ValidationError
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from apps.users.serializers import (
    UserSerializer,
    CreateUserSerializer,
    UpdateUserSerializer,
    ChangePasswordSerializer,
    EmailChangeInitiateSerializer,
    EmailChangeConfirmSerializer,
    MeSerializer,
)
from apps.users.services.user_service import UserService, UserNotFound
from apps.auth.services.email_change_service import EmailChangeService


def _err(e):
    message = e.message if hasattr(e, 'message') else str(e)
    return Response({'detail': message}, status=status.HTTP_400_BAD_REQUEST)


def _get_user_or_404(user_id: int):
    try:
        return UserService.get_user_by_id(user_id)
    except UserNotFound:
        return None


class UserListView(APIView):
    permission_classes = [IsAdminUser]

    @extend_schema(
        tags=['Users'], summary='List users',
        parameters=[OpenApiParameter('include_inactive', OpenApiTypes.BOOL, OpenApiParameter.QUERY)],
        responses={200: UserSerializer(many=True)},
    )
    def get(self, request):
        include_inactive = request.query_params.get('include_inactive') == 'true'
        users = UserService.get_all_users(include_inactive=include_inactive)
        return Response(UserSerializer(users, many=True).data)

    @extend_schema(
        tags=['Users'], summary='Create user',
        request=CreateUserSerializer,
        responses={201: UserSerializer, 400: OpenApiResponse(description='Validation error.')},
    )
    def post(self, request):
        serializer = CreateUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            user = UserService.create_user(**serializer.validated_data)
        except ValidationError as e:
            return _err(e)
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)


class UserDetailView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(tags=['Users'], summary='Get user', responses={200: UserSerializer})
    def get(self, request, pk):
        user = _get_user_or_404(pk)
        if not user:
            return Response(status=status.HTTP_404_NOT_FOUND)
        if not request.user.is_staff and request.user.pk != pk:
            return Response(status=status.HTTP_403_FORBIDDEN)
        return Response(UserSerializer(user).data)

    @extend_schema(
        tags=['Users'], summary='Update user',
        request=UpdateUserSerializer, responses={200: UserSerializer},
    )
    def patch(self, request, pk):
        user = _get_user_or_404(pk)
        if not user:
            return Response(status=status.HTTP_404_NOT_FOUND)
        if request.user.pk != pk:
            return Response(status=status.HTTP_403_FORBIDDEN)
        serializer = UpdateUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        updated = UserService.update_user(user, **serializer.validated_data)
        return Response(UserSerializer(updated).data)

    @extend_schema(tags=['Users'], summary='Deactivate user', responses={204: None})
    def delete(self, request, pk):
        if not request.user.is_staff:
            return Response(status=status.HTTP_403_FORBIDDEN)
        user = _get_user_or_404(pk)
        if not user:
            return Response(status=status.HTTP_404_NOT_FOUND)
        if request.user.pk == pk:
            return Response(
                {'detail': 'You cannot deactivate your own account.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        UserService.deactivate_user(user)
        return Response(status=status.HTTP_204_NO_CONTENT)


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(tags=['Users'], summary='Get my profile', responses={200: MeSerializer})
    def get(self, request):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        return Response(MeSerializer(User.objects.prefetch_related('groups').get(pk=request.user.pk)).data)

    @extend_schema(
        tags=['Users'], summary='Update my profile (bio)',
        request=UpdateUserSerializer, responses={200: MeSerializer},
    )
    def patch(self, request):
        serializer = UpdateUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        updated = UserService.update_user(request.user, **serializer.validated_data)
        return Response(MeSerializer(User.objects.prefetch_related('groups').get(pk=request.user.pk)).data)


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=['Users'], summary='Change password',
        request=ChangePasswordSerializer,
        responses={200: OpenApiResponse(description='Password updated.'), 400: None},
    )
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            UserService.change_password(request.user, **serializer.validated_data)
        except ValidationError as e:
            return _err(e)
        return Response({'detail': 'Password updated.'})


class EmailChangeInitiateView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=['Users'],
        summary='Initiate email change',
        description=(
            'Starts the email-change flow. '
            'Sends a confirmation link to the new address.'
        ),
        request=EmailChangeInitiateSerializer,
        responses={
            200: OpenApiResponse(description='Flow initiated.'),
            400: OpenApiResponse(description='Email already in use or same as current.'),
        },
    )
    def post(self, request):
        serializer = EmailChangeInitiateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            result = EmailChangeService.initiate(request.user, serializer.validated_data['new_email'])
        except ValidationError as e:
            return _err(e)
        return Response(result)


class EmailChangeConfirmView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=['Users'],
        summary='Confirm email change',
        description=(
            'Confirms the email change. '
            'Send `email_token` (from the link in the confirmation email).'
        ),
        request=EmailChangeConfirmSerializer,
        responses={
            200: OpenApiResponse(description='Email updated.'),
            400: OpenApiResponse(description='Invalid/expired token.'),
        },
    )
    def post(self, request):
        serializer = EmailChangeConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        d = serializer.validated_data
        try:
            EmailChangeService.confirm_with_email_token(request.user, d['email_token'])
        except ValidationError as e:
            return _err(e)
        return Response({'detail': 'Email address updated.'})