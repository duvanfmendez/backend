from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import PQRS, HistorialPQRS, RespuestaPQRS
from .serializers import (
    PQRSCreateSerializer,
    PQRSListSerializer,
    PQRSDetailSerializer,
    PQRSConsultaPublicaSerializer,
    CambiarEstadoSerializer,
    ResponderPQRSSerializer,
)


class PQRSViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar PQRS
    
    Endpoints:
    - GET /api/pqrs/ - Listar todas las PQRS (requiere auth)
    - POST /api/pqrs/ - Crear PQRS (público)
    - GET /api/pqrs/{id}/ - Ver detalle (requiere auth)
    - PUT /api/pqrs/{id}/ - Actualizar (requiere auth)
    - DELETE /api/pqrs/{id}/ - Eliminar (requiere auth)
    - GET /api/pqrs/consultar/{radicado}/ - Consultar por radicado (público)
    - PATCH /api/pqrs/{id}/cambiar_estado/ - Cambiar estado (requiere auth)
    - POST /api/pqrs/{id}/responder/ - Enviar respuesta (requiere auth)
    """
    
    queryset = PQRS.objects.all()
    
    def get_serializer_class(self):
        """Retorna el serializer según la acción"""
        if self.action == 'create':
            return PQRSCreateSerializer
        elif self.action == 'list':
            return PQRSListSerializer
        elif self.action == 'consultar':
            return PQRSConsultaPublicaSerializer
        return PQRSDetailSerializer
    
    def get_permissions(self):
        """Define permisos según la acción"""
        if self.action in ['create', 'consultar']:
            # Crear PQRS y consultar son públicos
            return [AllowAny()]
        # Resto de acciones requieren autenticación
        return [IsAuthenticated()]
    
    def create(self, request, *args, **kwargs):
        """Crear una nueva PQRS (público)"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        pqrs = serializer.save()
        
        # Crear registro en historial
        HistorialPQRS.objects.create(
            pqrs=pqrs,
            estado_anterior='',
            estado_nuevo='pendiente',
            observacion='PQRS registrada por el usuario',
            usuario=None
        )
        
        # Retornar el número de radicado
        return Response({
            'success': True,
            'message': 'PQRS creada exitosamente',
            'numero_radicado': pqrs.numero_radicado,
            'data': PQRSDetailSerializer(pqrs).data
        }, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['get'], url_path='consultar/(?P<radicado>[^/.]+)')
    def consultar(self, request, radicado=None):
        """Consultar PQRS por número de radicado (público)"""
        pqrs = get_object_or_404(PQRS, numero_radicado=radicado)
        serializer = self.get_serializer(pqrs)
        return Response(serializer.data)
    
    @action(detail=True, methods=['patch'])
    def cambiar_estado(self, request, pk=None):
        """Cambiar el estado de una PQRS"""
        pqrs = self.get_object()
        serializer = CambiarEstadoSerializer(data=request.data)
        
        if serializer.is_valid():
            estado_anterior = pqrs.estado
            estado_nuevo = serializer.validated_data['estado_nuevo']
            observacion = serializer.validated_data['observacion']
            
            # Actualizar estado
            pqrs.estado = estado_nuevo
            if estado_nuevo in ['resuelto', 'cerrado']:
                from django.utils import timezone
                pqrs.fecha_cierre = timezone.now()
            pqrs.save()
            
            # Registrar en historial
            HistorialPQRS.objects.create(
                pqrs=pqrs,
                estado_anterior=estado_anterior,
                estado_nuevo=estado_nuevo,
                observacion=observacion,
                usuario=request.user
            )
            
            return Response({
                'success': True,
                'message': 'Estado actualizado correctamente',
                'data': PQRSDetailSerializer(pqrs).data
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def responder(self, request, pk=None):
        """Enviar una respuesta a la PQRS"""
        pqrs = self.get_object()
        serializer = ResponderPQRSSerializer(data=request.data)
        
        if serializer.is_valid():
            respuesta = RespuestaPQRS.objects.create(
                pqrs=pqrs,
                respuesta=serializer.validated_data['respuesta'],
                usuario=request.user
            )
            
            # Cambiar estado a "en_tramite" si está pendiente
            if pqrs.estado == 'pendiente':
                pqrs.estado = 'en_tramite'
                pqrs.save()
                
                HistorialPQRS.objects.create(
                    pqrs=pqrs,
                    estado_anterior='pendiente',
                    estado_nuevo='en_tramite',
                    observacion='Respuesta enviada por el gestor',
                    usuario=request.user
                )
            
            return Response({
                'success': True,
                'message': 'Respuesta enviada correctamente',
                'data': PQRSDetailSerializer(pqrs).data
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def archivar(self, request, pk=None):
        """Archivar una PQRS (cambiar estado a cerrado)"""
        pqrs = self.get_object()
        
        if pqrs.estado == 'cerrado':
            return Response({
                'success': False,
                'message': 'La PQRS ya está cerrada'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        estado_anterior = pqrs.estado
        pqrs.estado = 'cerrado'
        from django.utils import timezone
        pqrs.fecha_cierre = timezone.now()
        pqrs.save()
        
        HistorialPQRS.objects.create(
            pqrs=pqrs,
            estado_anterior=estado_anterior,
            estado_nuevo='cerrado',
            observacion='PQRS archivada por el usuario',
            usuario=request.user
        )
        
        return Response({
            'success': True,
            'message': 'PQRS archivada correctamente'
        })