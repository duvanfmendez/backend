from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .views import TestView

urlpatterns = [
    # Admin de Django
    path('admin/', admin.site.urls),
    
    # Test endpoint
    path('test/', TestView.as_view()),
    
    # API de PQRS
    path('api/', include('apps.pqrs.urls')),
    
    # API de Autenticación
    path('api/auth/', include('apps.users.urls')),
    
    # API de Dashboard  🆕 AGREGA ESTA LÍNEA SI NO ESTÁ
    path('api/dashboard/', include('apps.dashboard.urls')),
    
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Servir archivos media en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)