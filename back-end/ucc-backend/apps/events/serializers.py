from rest_framework import serializers
from django.contrib.auth import get_user_model
from apps.events.models import Event

User = get_user_model()


class AttendeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']


class EventSerializer(serializers.ModelSerializer):
    created_by  = AttendeeSerializer(read_only=True)
    attendees   = AttendeeSerializer(many=True, read_only=True)
    attendee_count = serializers.SerializerMethodField()
    is_attending   = serializers.SerializerMethodField()
    is_owner       = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = [
            'id', 'title', 'occurrence', 'description',
            'created_by', 'attendees', 'attendee_count',
            'is_attending', 'is_owner',
            'created_at', 'updated_at',
        ]

    def _current_user(self):
        return self.context.get('request').user

    def get_attendee_count(self, obj):
        return obj.attendees.count()

    def get_is_attending(self, obj):
        user = self._current_user()
        if not user or not user.is_authenticated:
            return False
        return obj.attendees.filter(pk=user.pk).exists()

    def get_is_owner(self, obj):
        user = self._current_user()
        if not user or not user.is_authenticated:
            return False
        return obj.created_by_id == user.pk


class CreateEventSerializer(serializers.Serializer):
    title       = serializers.CharField(max_length=255)
    occurrence  = serializers.DateTimeField()
    description = serializers.CharField(required=False, allow_blank=True, default='')


class UpdateEventSerializer(serializers.Serializer):
    title       = serializers.CharField(max_length=255, required=False)
    occurrence  = serializers.DateTimeField(required=False)
    description = serializers.CharField(required=False, allow_blank=True)