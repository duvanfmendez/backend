# document document-compose.yaml

# document.py
import os

from django.core.asgi import get_asgi_application  # Corrección: "asgi" no "asgl"

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')  # Corrección: "core.settings" no "core_settings"

django_asgi_app = get_asgi_application()  # Corrección: "asgi" no "asgl"

from channels.routing import ProtocolTypeRouter

application = ProtocolTypeRouter({
    "http": django_asgi_app  # Maneja conexiones HTTP tradicionales
})