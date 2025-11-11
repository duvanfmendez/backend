from django.contrib import admin
from .models import Notificacion


@admin.register(Notificacion)
class NotificacionAdmin(admin.ModelAdmin):
    list_display = [
        'pqrs',
        'tipo',
        'destinatario_email',
        'enviado',
        'fecha_envio',
        'fecha_creacion',
    ]
    
    list_filter = [
        'tipo',
        'enviado',
        'fecha_creacion',
    ]
    
    search_fields = [
        'pqrs__numero_radicado',
        'destinatario_email',
        'asunto',
    ]
    
    readonly_fields = [
        'fecha_creacion',
        'fecha_envio',
    ]