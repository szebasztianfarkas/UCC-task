"""
ASGI config — wraps Django with Django Channels so WebSocket connections
can be handled alongside regular HTTP requests.
"""
import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.urls import re_path

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

django_asgi_app = get_asgi_application()

from apps.helpdesk.consumers import HelpdeskConsumer

websocket_urlpatterns = [
    re_path(r'^ws/helpdesk/(?P<chat_id>\d+)/$', HelpdeskConsumer.as_asgi()),
]

application = ProtocolTypeRouter({
    'http': django_asgi_app,
    'websocket': AllowedHostsOriginValidator(
        URLRouter(websocket_urlpatterns)
    ),
})