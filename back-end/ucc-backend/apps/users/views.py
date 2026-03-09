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
)
from apps.users.services.user_service import UserService, UserNotFound


def _get_user_or_404(user_id: int):
    try:
        return UserService.get_user_by_id(user_id)
    except UserNotFound:
        return None


class UserListView(APIView):
    permission_classes = [IsAdminUser]

    @extend_schema(
        tags=['Users'],
        summary='List users',
        description='Returns all active users. Pass `?include_inactive=true` to include deactivated accounts. Admin only.',
        parameters=[
            OpenApiParameter(
                name='include_inactive',
                type=OpenApiTypes.BOOL,
                location=OpenApiParameter.QUERY,
                description='Include deactivated users in results.',
                default=False,
            )
        ],
        responses={200: UserSerializer(many=True)},
    )
    def get(self, request):
        include_inactive = request.query_params.get('include_inactive') == 'true'
        users = UserService.get_all_users(include_inactive=include_inactive)
        return Response(UserSerializer(users, many=True).data)

    @extend_schema(
        tags=['Users'],
        summary='Create user',
        description='Creates a new user account. Admin only.',
        request=CreateUserSerializer,
        responses={
            201: UserSerializer,
            400: OpenApiResponse(description='Validation error — username or email already taken.'),
        },
    )
    def post(self, request):
        serializer = CreateUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            user = UserService.create_user(**serializer.validated_data)
        except ValidationError as e:
            return Response({'detail': e.message}, status=status.HTTP_400_BAD_REQUEST)
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)


class UserDetailView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=['Users'],
        summary='Get user',
        description='Returns a user by ID. Admins can fetch any user; regular users can only fetch themselves.',
        responses={
            200: UserSerializer,
            403: OpenApiResponse(description='Insufficient permissions.'),
            404: OpenApiResponse(description='User not found.'),
        },
    )
    def get(self, request, pk):
        user = _get_user_or_404(pk)
        if not user:
            return Response(status=status.HTTP_404_NOT_FOUND)
        if not request.user.is_staff and request.user.pk != pk:
            return Response(status=status.HTTP_403_FORBIDDEN)
        return Response(UserSerializer(user).data)

    @extend_schema(
        tags=['Users'],
        summary='Update user',
        description='Partially updates a user profile. Users can only update their own profile.',
        request=UpdateUserSerializer,
        responses={
            200: UserSerializer,
            403: OpenApiResponse(description='Cannot update another user\'s profile.'),
            404: OpenApiResponse(description='User not found.'),
        },
    )
    def patch(self, request, pk):
        user = _get_user_or_404(pk)
        if not user:
            return Response(status=status.HTTP_404_NOT_FOUND)
        if request.user.pk != pk:
            return Response(status=status.HTTP_403_FORBIDDEN)
        serializer = UpdateUserSerializer(data=request.data, context={'user': user})
        serializer.is_valid(raise_exception=True)
        updated = UserService.update_user(user, **serializer.validated_data)
        return Response(UserSerializer(updated).data)

    @extend_schema(
        tags=['Users'],
        summary='Deactivate user',
        description='Soft-deletes a user by setting `is_active=False`. All data is retained. Admin only.',
        responses={
            204: OpenApiResponse(description='User deactivated.'),
            400: OpenApiResponse(description='Cannot deactivate your own account.'),
            403: OpenApiResponse(description='Admin access required.'),
            404: OpenApiResponse(description='User not found.'),
        },
    )
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

    @extend_schema(
        tags=['Users'],
        summary='Get my profile',
        description='Returns the profile of the currently authenticated user.',
        responses={200: UserSerializer},
    )
    def get(self, request):
        return Response(UserSerializer(request.user).data)

    @extend_schema(
        tags=['Users'],
        summary='Update my profile',
        description='Updates the currently authenticated user\'s own profile.',
        request=UpdateUserSerializer,
        responses={
            200: UserSerializer,
            400: OpenApiResponse(description='Validation error.'),
        },
    )
    def patch(self, request):
        serializer = UpdateUserSerializer(
            data=request.data,
            context={'user': request.user},
        )
        serializer.is_valid(raise_exception=True)
        updated = UserService.update_user(request.user, **serializer.validated_data)
        return Response(UserSerializer(updated).data)


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=['Users'],
        summary='Change password',
        description='Changes the authenticated user\'s password. Requires the current password for verification.',
        request=ChangePasswordSerializer,
        responses={
            200: OpenApiResponse(description='Password updated successfully.'),
            400: OpenApiResponse(description='Current password incorrect or new password fails validation.'),
        },
    )
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            UserService.change_password(request.user, **serializer.validated_data)
        except ValidationError as e:
            return Response({'detail': e.message}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'detail': 'Password updated.'})