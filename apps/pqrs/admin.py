from django.contrib import admin
from .models import PQRS, HistorialPQRS, RespuestaPQRS


@admin.register(PQRS)
class PQRSAdmin(admin.ModelAdmin):
    """Configuración del admin para PQRS"""
    
    list_display = [
        'numero_radicado',
        'tipo',
        'asunto',
        'nombre_completo',
        'estado',
        'color_semaforo',
        'dias_restantes',
        'fecha_radicacion',
        'responsable',
    ]
    
    list_filter = [
        'tipo',
        'estado',
        'color_semaforo',
        'area_responsable',
        'fecha_radicacion',
    ]
    
    search_fields = [
        'numero_radicado',
        'asunto',
        'nombre_completo',
        'correo_electronico',
        'descripcion',
    ]
    
    readonly_fields = [
        'numero_radicado',
        'fecha_radicacion',
        'created_at',
        'updated_at',
        'dias_restantes',
        'color_semaforo',
    ]
    
    fieldsets = (
        ('Información Básica', {
            'fields': (
                'numero_radicado',
                'tipo',
                'asunto',
                'descripcion',
            )
        }),
        ('Datos del Ciudadano', {
            'fields': (
                'nombre_completo',
                'correo_electronico',
                'telefono',
            )
        }),
        ('Estado y Seguimiento', {
            'fields': (
                'estado',
                'fecha_radicacion',
                'fecha_limite_respuesta',
                'fecha_cierre',
                'color_semaforo',
                'dias_restantes',
            )
        }),
        ('Asignación', {
            'fields': (
                'area_responsable',
                'responsable',
            )
        }),
        ('Archivo Adjunto', {
            'fields': ('archivo_adjunto',)
        }),
        ('Auditoría', {
            'fields': (
                'created_at',
                'updated_at',
            ),
            'classes': ('collapse',)
        }),
    )
    
    date_hierarchy = 'fecha_radicacion'


@admin.register(HistorialPQRS)
class HistorialPQRSAdmin(admin.ModelAdmin):
    """Configuración del admin para Historial"""
    
    list_display = [
        'pqrs',
        'estado_anterior',
        'estado_nuevo',
        'usuario',
        'fecha_cambio',
    ]
    
    list_filter = [
        'estado_nuevo',
        'fecha_cambio',
    ]
    
    search_fields = [
        'pqrs__numero_radicado',
        'observacion',
    ]
    
    readonly_fields = [
        'fecha_cambio',
    ]


@admin.register(RespuestaPQRS)
class RespuestaPQRSAdmin(admin.ModelAdmin):
    """Configuración del admin para Respuestas"""
    
    list_display = [
        'pqrs',
        'usuario',
        'fecha_respuesta',
        'notificado',
    ]
    
    list_filter = [
        'notificado',
        'fecha_respuesta',
    ]
    
    search_fields = [
        'pqrs__numero_radicado',
        'respuesta',
    ]
    
    readonly_fields = [
        'fecha_respuesta',
    ]