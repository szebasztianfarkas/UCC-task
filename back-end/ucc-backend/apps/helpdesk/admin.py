from django.contrib import admin
from apps.helpdesk.models import HelpdeskChat, HelpdeskMessage


class HelpdeskMessageInline(admin.TabularInline):
    model = HelpdeskMessage
    extra = 0
    readonly_fields = ['role', 'sender', 'content', 'created_at']
    can_delete = False


@admin.register(HelpdeskChat)
class HelpdeskChatAdmin(admin.ModelAdmin):
    list_display  = ['id', 'user', 'status', 'assigned_agent', 'message_count', 'updated_at']
    list_filter   = ['status']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['created_at', 'updated_at']
    raw_id_fields = ['user', 'assigned_agent']
    inlines = [HelpdeskMessageInline]
    actions = ['lock_chats', 'unlock_chats']

    def message_count(self, obj):
        return obj.messages.count()
    message_count.short_description = 'Messages'

    def lock_chats(self, request, queryset):
        queryset.update(status=HelpdeskChat.LOCKED)
    lock_chats.short_description = 'Lock selected chats'

    def unlock_chats(self, request, queryset):
        queryset.update(status=HelpdeskChat.OPEN)
    unlock_chats.short_description = 'Unlock selected chats'