import json

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError

User = get_user_model()

RELAY_TYPES = {'offer', 'answer', 'ice-candidate', 'call-start', 'call-end', 'call-busy'}


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


class VoiceSignalConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.chat_id    = int(self.scope['url_route']['kwargs']['chat_id'])
        self.room_group = f'helpdesk_voice_{self.chat_id}'

        qs = dict(
            pair.split('=', 1)
            for pair in self.scope['query_string'].decode().split('&')
            if '=' in pair
        )
        user = await _get_user_from_token(qs.get('token', ''))

        if isinstance(user, AnonymousUser) or not user.is_active:
            await self.close(code=4001)
            return

        if not await _can_access_chat(user, self.chat_id):
            await self.close(code=4003)
            return

        self.user     = user
        self.username = user.username

        await self.channel_layer.group_add(self.room_group, self.channel_name)
        await self.accept()

        await self.channel_layer.group_send(self.room_group, {
            'type':     'voice.signal',
            'payload':  {'type': 'peer-joined', 'from': self.username},
            'sender':   self.channel_name,
        })

    async def disconnect(self, code):
        if not hasattr(self, 'room_group'):
            return
        await self.channel_layer.group_send(self.room_group, {
            'type':    'voice.signal',
            'payload': {'type': 'peer-left', 'from': getattr(self, 'username', '?')},
            'sender':  self.channel_name,
        })
        await self.channel_layer.group_discard(self.room_group, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        if not text_data:
            return
        try:
            payload = json.loads(text_data)
        except (json.JSONDecodeError, ValueError):
            return

        if payload.get('type') not in RELAY_TYPES:
            return

        payload['from'] = self.username

        await self.channel_layer.group_send(self.room_group, {
            'type':    'voice.signal',
            'payload': payload,
            'sender':  self.channel_name,
        })

    async def voice_signal(self, event):
        if event.get('sender') == self.channel_name:
            return
        await self.send(text_data=json.dumps(event['payload']))