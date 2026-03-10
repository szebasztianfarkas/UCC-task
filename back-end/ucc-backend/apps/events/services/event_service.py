from django.core.exceptions import ValidationError
from django.utils import timezone
from apps.events.models import Event


class EventNotFound(Exception):
    pass


class EventService:
    @staticmethod
    def get_all_events(search=None, upcoming_only=False, attending_user=None, created_by_user=None):
        qs = Event.objects.select_related('created_by').prefetch_related('attendees')

        if search:
            from django.db.models import Q
            qs = qs.filter(
                Q(title__icontains=search) | Q(description__icontains=search)
            )

        if upcoming_only:
            qs = qs.filter(occurrence__gte=timezone.now())

        if attending_user:
            qs = qs.filter(attendees=attending_user)

        if created_by_user:
            qs = qs.filter(created_by=created_by_user)

        return qs

    @staticmethod
    def get_event_by_id(event_id: int) -> Event:
        try:
            return (
                Event.objects
                .select_related('created_by')
                .prefetch_related('attendees')
                .get(pk=event_id)
            )
        except Event.DoesNotExist:
            raise EventNotFound(f'Event {event_id} does not exist.')

    @staticmethod
    def create_event(*, user, title: str, occurrence, description: str = '') -> Event:
        return Event.objects.create(
            title=title,
            occurrence=occurrence,
            description=description,
            created_by=user,
        )

    @staticmethod
    def update_event(event: Event, **fields) -> Event:
        for attr, value in fields.items():
            setattr(event, attr, value)
        event.save(update_fields=list(fields.keys()) + ['updated_at'])
        return event

    @staticmethod
    def delete_event(event: Event) -> None:
        event.delete()

    @staticmethod
    def join_event(event: Event, user) -> None:
        if event.created_by_id == user.pk:
            raise ValidationError('You cannot join an event you created.')
        if event.attendees.filter(pk=user.pk).exists():
            raise ValidationError('You are already attending this event.')
        event.attendees.add(user)

    @staticmethod
    def leave_event(event: Event, user) -> None:
        if not event.attendees.filter(pk=user.pk).exists():
            raise ValidationError('You are not attending this event.')
        event.attendees.remove(user)