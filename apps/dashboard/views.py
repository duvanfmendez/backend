from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count, Avg, Q
from django.utils import timezone
from datetime import timedelta
from apps.pqrs.models import PQRS
from apps.users.permissions import IsAdministradorOrSupervisor


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def estadisticas_generales(request):
    """KPIs generales del sistema"""
    
    # Total de PQRS
    total_pqrs = PQRS.objects.count()
    
    # Por estado
    por_estado = PQRS.objects.values('estado').annotate(
        total=Count('id')
    )
    
    # Por tipo
    por_tipo = PQRS.objects.values('tipo').annotate(
        total=Count('id')
    )
    
    # Por semáforo
    por_semaforo = PQRS.objects.values('color_semaforo').annotate(
        total=Count('id')
    )
    
    # PQRS del mes actual
    mes_actual = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    pqrs_mes_actual = PQRS.objects.filter(
        fecha_radicacion__gte=mes_actual
    ).count()
    
    # PQRS vencidas
    pqrs_vencidas = PQRS.objects.filter(estado='vencido').count()
    
    # Promedio de días para responder
    pqrs_cerradas = PQRS.objects.filter(
        estado__in=['resuelto', 'cerrado'],
        fecha_cierre__isnull=False
    )
    
    if pqrs_cerradas.exists():
        tiempo_promedio = 0
        for pqrs in pqrs_cerradas:
            dias = (pqrs.fecha_cierre - pqrs.fecha_radicacion).days
            tiempo_promedio += dias
        tiempo_promedio = tiempo_promedio / pqrs_cerradas.count()
    else:
        tiempo_promedio = 0
    
    return Response({
        'success': True,
        'data': {
            'total_pqrs': total_pqrs,
            'pqrs_mes_actual': pqrs_mes_actual,
            'pqrs_vencidas': pqrs_vencidas,
            'tiempo_promedio_respuesta': round(tiempo_promedio, 1),
            'por_estado': list(por_estado),
            'por_tipo': list(por_tipo),
            'por_semaforo': list(por_semaforo),
        }
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def distribucion_por_tipo(request):
    """Distribución de PQRS por tipo (para gráfico circular)"""
    
    data = PQRS.objects.values('tipo').annotate(
        total=Count('id')
    ).order_by('-total')
    
    # Calcular porcentajes
    total_general = PQRS.objects.count()
    resultado = []
    
    for item in data:
        porcentaje = (item['total'] / total_general * 100) if total_general > 0 else 0
        resultado.append({
            'tipo': item['tipo'],
            'tipo_display': dict(PQRS.TIPO_CHOICES)[item['tipo']],
            'total': item['total'],
            'porcentaje': round(porcentaje, 2)
        })
    
    return Response({
        'success': True,
        'data': resultado
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def distribucion_por_estado(request):
    """Distribución de PQRS por estado"""
    
    data = PQRS.objects.values('estado').annotate(
        total=Count('id')
    ).order_by('-total')
    
    total_general = PQRS.objects.count()
    resultado = []
    
    for item in data:
        porcentaje = (item['total'] / total_general * 100) if total_general > 0 else 0
        resultado.append({
            'estado': item['estado'],
            'estado_display': dict(PQRS.ESTADO_CHOICES)[item['estado']],
            'total': item['total'],
            'porcentaje': round(porcentaje, 2)
        })
    
    return Response({
        'success': True,
        'data': resultado
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def evolucion_mensual(request):
    """Evolución de PQRS por mes (últimos 6 meses)"""
    
    ahora = timezone.now()
    resultado = []
    
    for i in range(5, -1, -1):
        fecha_inicio = (ahora - timedelta(days=30*i)).replace(day=1, hour=0, minute=0, second=0)
        if i == 0:
            fecha_fin = ahora
        else:
            fecha_fin = (ahora - timedelta(days=30*(i-1))).replace(day=1, hour=0, minute=0, second=0)
        
        total = PQRS.objects.filter(
            fecha_radicacion__gte=fecha_inicio,
            fecha_radicacion__lt=fecha_fin
        ).count()
        
        resultado.append({
            'mes': fecha_inicio.strftime('%B %Y'),
            'total': total
        })
    
    return Response({
        'success': True,
        'data': resultado
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def por_area_responsable(request):
    """PQRS por área responsable"""
    
    data = PQRS.objects.exclude(
        area_responsable=''
    ).values('area_responsable').annotate(
        total=Count('id')
    ).order_by('-total')[:10]  # Top 10 áreas
    
    return Response({
        'success': True,
        'data': list(data)
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def tiempo_respuesta_por_tipo(request):
    """Tiempo promedio de respuesta por tipo de PQRS"""
    
    resultado = []
    
    for tipo_key, tipo_display in PQRS.TIPO_CHOICES:
        pqrs_cerradas = PQRS.objects.filter(
            tipo=tipo_key,
            estado__in=['resuelto', 'cerrado'],
            fecha_cierre__isnull=False
        )
        
        if pqrs_cerradas.exists():
            tiempo_promedio = 0
            for pqrs in pqrs_cerradas:
                dias = (pqrs.fecha_cierre - pqrs.fecha_radicacion).days
                tiempo_promedio += dias
            tiempo_promedio = tiempo_promedio / pqrs_cerradas.count()
        else:
            tiempo_promedio = 0
        
        resultado.append({
            'tipo': tipo_key,
            'tipo_display': tipo_display,
            'tiempo_promedio_dias': round(tiempo_promedio, 1),
            'total_resueltas': pqrs_cerradas.count()
        })
    
    return Response({
        'success': True,
        'data': resultado
    })