from rest_framework import serializers
from django.contrib.auth import get_user_model
from apps.helpdesk.models import HelpdeskChat, HelpdeskMessage

User = get_user_model()


class SenderSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']


class HelpdeskMessageSerializer(serializers.ModelSerializer):
    sender = SenderSerializer(read_only=True)

    class Meta:
        model = HelpdeskMessage
        fields = ['id', 'chat_id', 'role', 'sender', 'content', 'created_at']


class HelpdeskChatSerializer(serializers.ModelSerializer):
    messages       = HelpdeskMessageSerializer(many=True, read_only=True)
    user_username  = serializers.CharField(source='user.username', read_only=True)
    agent_username = serializers.CharField(source='assigned_agent.username', read_only=True, default=None)

    class Meta:
        model = HelpdeskChat
        fields = [
            'id', 'status',
            'user_username', 'agent_username',
            'created_at', 'updated_at',
            'messages',
        ]


class HelpdeskChatSummarySerializer(serializers.ModelSerializer):
    user_username  = serializers.CharField(source='user.username', read_only=True)
    agent_username = serializers.CharField(source='assigned_agent.username', read_only=True, default=None)
    last_message   = serializers.SerializerMethodField()

    class Meta:
        model = HelpdeskChat
        fields = [
            'id', 'status',
            'user_username', 'agent_username',
            'created_at', 'updated_at',
            'last_message',
        ]

    def get_last_message(self, obj):
        msg = obj.messages.exclude(role='system').last()
        if not msg:
            return None
        return {'role': msg.role, 'content': (msg.content or '')[:80]}


class PostMessageSerializer(serializers.Serializer):
    text = serializers.CharField(max_length=2000)