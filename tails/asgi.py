"""
ASGI config for tails project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""
from channels.routing import ProtocolTypeRouter
import os
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tails.settings')

application = get_asgi_application()

import cust.routing

application = ProtocolTypeRouter({
    "http": application,
    "websocket": AllowedHostsOriginValidator(
            AuthMiddlewareStack(URLRouter(cust.routing.websocket_urlpatterns)))
})