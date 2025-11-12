from django.urls import path
from .views import (
    estadisticas_generales,
    distribucion_por_tipo,
    distribucion_por_estado,
    evolucion_mensual,
    por_area_responsable,
    tiempo_respuesta_por_tipo,
)

urlpatterns = [
    path('stats/', estadisticas_generales, name='estadisticas_generales'),
    path('por-tipo/', distribucion_por_tipo, name='distribucion_por_tipo'),
    path('por-estado/', distribucion_por_estado, name='distribucion_por_estado'),
    path('evolucion-mensual/', evolucion_mensual, name='evolucion_mensual'),
    path('por-area/', por_area_responsable, name='por_area_responsable'),
    path('tiempo-respuesta/', tiempo_respuesta_por_tipo, name='tiempo_respuesta_por_tipo'),
]