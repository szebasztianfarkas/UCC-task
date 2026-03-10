from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.core.exceptions import ValidationError
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from apps.events.models import Event
from apps.events.serializers import (
    EventSerializer,
    CreateEventSerializer,
    UpdateEventSerializer,
)
from apps.events.services.event_service import EventService, EventNotFound


def _serialize(event_or_qs, request, many=False):
    return EventSerializer(event_or_qs, many=many, context={'request': request}).data


def _get_event_or_404(event_id):
    try:
        return EventService.get_event_by_id(event_id)
    except EventNotFound:
        return None


class EventListView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=['Events'],
        summary='List events',
        description='Returns all events. Supports filtering by search query, upcoming only, or events the current user is attending.',
        parameters=[
            OpenApiParameter('search', OpenApiTypes.STR, OpenApiParameter.QUERY,
                             description='Search in title and description.'),
            OpenApiParameter('upcoming', OpenApiTypes.BOOL, OpenApiParameter.QUERY,
                             description='If true, only returns future events.'),
            OpenApiParameter('attending', OpenApiTypes.BOOL, OpenApiParameter.QUERY,
                             description='If true, only returns events the current user is attending.'),
            OpenApiParameter('createdBy', OpenApiTypes.BOOL, OpenApiParameter.QUERY,
                             description='If true, only returns the events the current user has created.'),
        ],
        responses={200: EventSerializer(many=True)},
    )
    def get(self, request):
        search        = request.query_params.get('search', '').strip() or None
        upcoming_only = request.query_params.get('upcoming') == 'true'
        attending     = request.query_params.get('attending') == 'true'
        created_by    = request.query_params.get('createdBy') == 'true'

        events = EventService.get_all_events(
            search=search,
            upcoming_only=upcoming_only,
            attending_user=request.user if attending else None,
            created_by_user=request.user if created_by else None
        )
        return Response(_serialize(events, request, many=True))

    @extend_schema(
        tags=['Events'],
        summary='Create event',
        description='Creates a new event. The authenticated user becomes the creator.',
        request=CreateEventSerializer,
        responses={
            201: EventSerializer,
            400: OpenApiResponse(description='Validation error.'),
        },
    )
    def post(self, request):
        serializer = CreateEventSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        event = EventService.create_event(user=request.user, **serializer.validated_data)
        return Response(_serialize(event, request), status=status.HTTP_201_CREATED)


class EventDetailView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=['Events'],
        summary='Get event',
        responses={200: EventSerializer, 404: OpenApiResponse(description='Not found.')},
    )
    def get(self, request, pk):
        event = _get_event_or_404(pk)
        if not event:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(_serialize(event, request))

    @extend_schema(
        tags=['Events'],
        summary='Update event',
        description='Partially updates an event. Only the creator can do this.',
        request=UpdateEventSerializer,
        responses={
            200: EventSerializer,
            403: OpenApiResponse(description='Not the event creator.'),
            404: OpenApiResponse(description='Not found.'),
        },
    )
    def patch(self, request, pk):
        event = _get_event_or_404(pk)
        if not event:
            return Response(status=status.HTTP_404_NOT_FOUND)
        if event.created_by_id != request.user.pk:
            return Response(status=status.HTTP_403_FORBIDDEN)
        serializer = UpdateEventSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        updated = EventService.update_event(event, **serializer.validated_data)
        return Response(_serialize(updated, request))

    @extend_schema(
        tags=['Events'],
        summary='Delete event',
        description='Deletes an event. Only the creator can do this.',
        responses={
            204: OpenApiResponse(description='Deleted.'),
            403: OpenApiResponse(description='Not the event creator.'),
            404: OpenApiResponse(description='Not found.'),
        },
    )
    def delete(self, request, pk):
        event = _get_event_or_404(pk)
        if not event:
            return Response(status=status.HTTP_404_NOT_FOUND)
        if event.created_by_id != request.user.pk:
            return Response(status=status.HTTP_403_FORBIDDEN)
        EventService.delete_event(event)
        return Response(status=status.HTTP_204_NO_CONTENT)


class EventJoinView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=['Events'],
        summary='Join event',
        description='Adds the authenticated user to the event\'s attendee list. Creators cannot join their own events.',
        responses={
            200: EventSerializer,
            400: OpenApiResponse(description='Already attending, or creator trying to join own event.'),
            404: OpenApiResponse(description='Not found.'),
        },
    )
    def post(self, request, pk):
        event = _get_event_or_404(pk)
        if not event:
            return Response(status=status.HTTP_404_NOT_FOUND)
        try:
            EventService.join_event(event, request.user)
        except ValidationError as e:
            return Response({'detail': e.message}, status=status.HTTP_400_BAD_REQUEST)
        return Response(_serialize(event, request))


class EventLeaveView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=['Events'],
        summary='Leave event',
        description='Removes the authenticated user from the event\'s attendee list.',
        responses={
            200: EventSerializer,
            400: OpenApiResponse(description='Not currently attending.'),
            404: OpenApiResponse(description='Not found.'),
        },
    )
    def post(self, request, pk):
        event = _get_event_or_404(pk)
        if not event:
            return Response(status=status.HTTP_404_NOT_FOUND)
        try:
            EventService.leave_event(event, request.user)
        except ValidationError as e:
            return Response({'detail': e.message}, status=status.HTTP_400_BAD_REQUEST)
        return Response(_serialize(event, request))