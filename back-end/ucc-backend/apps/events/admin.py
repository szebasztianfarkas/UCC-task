from django.contrib import admin
from apps.events.models import Event


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display  = ['title', 'occurrence', 'created_by', 'attendee_count', 'created_at']
    list_filter   = ['occurrence']
    search_fields = ['title', 'description', 'created_by__username']
    raw_id_fields = ['created_by']
    filter_horizontal = ['attendees']

    def attendee_count(self, obj):
        return obj.attendees.count()
    attendee_count.short_description = 'Attendees'