from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from rest_framework.permissions import IsAdminUser
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

handler400 = 'config.handlers.bad_request'
handler403 = 'config.handlers.permission_denied'
handler404 = 'config.handlers.not_found'
handler500 = 'config.handlers.server_error'

urlpatterns = [
    path('admin/', admin.site.urls),

    path('api/auth/',     include('apps.auth.urls')),
    path('api/users/',    include('apps.users.urls')),
    path('api/events/',   include('apps.events.urls')),
    path('api/helpdesk/', include('apps.helpdesk.urls')),

    path('api/schema/',
         SpectacularAPIView.as_view(permission_classes=[IsAdminUser]),
         name='schema'),
    path('api/schema/swagger/',
         SpectacularSwaggerView.as_view(
             url_name='schema', permission_classes=[IsAdminUser]
         ),
         name='swagger-ui'),
    path('api/schema/redoc/',
         SpectacularRedocView.as_view(
             url_name='schema', permission_classes=[IsAdminUser]
         ),
         name='redoc'),
]