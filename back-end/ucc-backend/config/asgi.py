import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.urls import re_path

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

django_asgi_app = get_asgi_application()

from apps.helpdesk.consumers.helpdesk_consumer import HelpdeskConsumer
from apps.helpdesk.consumers.agent_consumer import AgentConsumer
from apps.helpdesk.consumers.voice_consumer import VoiceSignalConsumer 

websocket_urlpatterns = [
    re_path(r'^ws/helpdesk/agent/$',                   AgentConsumer.as_asgi()),
    re_path(r'^ws/helpdesk/(?P<chat_id>\d+)/$',        HelpdeskConsumer.as_asgi()),
    re_path(r'^ws/helpdesk/(?P<chat_id>\d+)/voice/$',  VoiceSignalConsumer.as_asgi()),
]

application = ProtocolTypeRouter({
    'http': django_asgi_app,
    'websocket': AllowedHostsOriginValidator(
        URLRouter(websocket_urlpatterns)
    ),
})