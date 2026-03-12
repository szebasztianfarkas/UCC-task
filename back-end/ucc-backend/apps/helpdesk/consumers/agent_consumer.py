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
def _is_agent(user) -> bool:
    return user.groups.filter(name='helpdesk_agent').exists()


@database_sync_to_async
def _active_chat_ids() -> list[int]:
    from apps.helpdesk.models import HelpdeskChat
    return list(
        HelpdeskChat.objects
        .exclude(status__in=[HelpdeskChat.RESOLVED, HelpdeskChat.LOCKED])
        .values_list('id', flat=True)
    )


class AgentConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        qs = dict(
            pair.split('=', 1)
            for pair in self.scope['query_string'].decode().split('&')
            if '=' in pair
        )
        user = await _get_user_from_token(qs.get('token', ''))

        if isinstance(user, AnonymousUser) or not user.is_active:
            await self.close(code=4001)
            return

        if not await _is_agent(user):
            await self.close(code=4003)
            return

        self.user = user
        self.joined_groups: set[str] = set()

        await self.accept()
        await self._refresh_rooms()

    async def disconnect(self, code):
        for group in list(self.joined_groups):
            await self.channel_layer.group_discard(group, self.channel_name)
        self.joined_groups.clear()

    async def receive(self, text_data=None, bytes_data=None):
        if not text_data:
            return
        try:
            payload = json.loads(text_data)
        except (json.JSONDecodeError, ValueError):
            return
        if payload.get('type') == 'refresh_rooms':
            await self._refresh_rooms()

    async def _refresh_rooms(self):
        chat_ids = await _active_chat_ids()
        for chat_id in chat_ids:
            group = f'helpdesk_{chat_id}'
            if group not in self.joined_groups:
                await self.channel_layer.group_add(group, self.channel_name)
                self.joined_groups.add(group)

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'type':    'message',
            'message': event['message'],
            'chat_id': event['chat_id'],
        }))

    async def status_change(self, event):
        await self.send(text_data=json.dumps({
            'type':    'status_change',
            'status':  event['status'],
            'chat_id': event['chat_id'],
        }))
        await self._refresh_rooms()