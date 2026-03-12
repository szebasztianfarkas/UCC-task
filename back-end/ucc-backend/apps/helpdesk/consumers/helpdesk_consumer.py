import json

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError

User = get_user_model()


@database_sync_to_async
def _get_user_from_token(token_str: str):
    try:
        token = AccessToken(token_str)
        return User.objects.get(pk=token['user_id'])
    except (InvalidToken, TokenError, User.DoesNotExist, KeyError):
        return AnonymousUser()


@database_sync_to_async
def _can_access_chat(user, chat_id: int) -> bool:
    from apps.helpdesk.models import HelpdeskChat
    from apps.helpdesk.services.helpdesk_service import _is_agent
    try:
        chat = HelpdeskChat.objects.get(pk=chat_id)
    except HelpdeskChat.DoesNotExist:
        return False
    return chat.user_id == user.pk or _is_agent(user)


class HelpdeskConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.chat_id   = int(self.scope['url_route']['kwargs']['chat_id'])
        self.room_group = f'helpdesk_{self.chat_id}'

        qs = dict(
            pair.split('=', 1)
            for pair in self.scope['query_string'].decode().split('&')
            if '=' in pair
        )
        token_str = qs.get('token', '')
        user = await _get_user_from_token(token_str)

        if isinstance(user, AnonymousUser) or not user.is_active:
            await self.close(code=4001)
            return

        if not await _can_access_chat(user, self.chat_id):
            await self.close(code=4003)
            return

        self.user = user
        await self.channel_layer.group_add(self.room_group, self.channel_name)
        await self.accept()

    async def disconnect(self, code):
        if hasattr(self, 'room_group'):
            await self.channel_layer.group_discard(self.room_group, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        pass

    async def chat_message(self, event):
        """Broadcast a new message to all room participants."""
        await self.send(text_data=json.dumps({
            'type':    'message',
            'message': event['message'],
        }))

    async def status_change(self, event):
        """Broadcast a chat status change."""
        await self.send(text_data=json.dumps({
            'type':   'status_change',
            'status': event['status'],
            'chat_id': self.chat_id,
        }))