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
from apps.notifications.utils import enviar_email_pqrs_creada, enviar_email_pqrs_respondida
from apps.users.permissions import CanManagePQRS


class PQRSViewSet(viewsets.ModelViewSet):
    """ViewSet para gestionar PQRS"""
    
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
        # Resto de acciones requieren permisos de gestión
        return [CanManagePQRS()]
    
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
        
        # Enviar email de confirmación
        enviar_email_pqrs_creada(pqrs)
        
        return Response({
            'success': True,
            'message': 'PQRS creada exitosamente. Revise su correo electrónico.',
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
            
            pqrs.estado = estado_nuevo
            if estado_nuevo in ['resuelto', 'cerrado']:
                from django.utils import timezone
                pqrs.fecha_cierre = timezone.now()
            pqrs.save()
            
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
            
            # Enviar email de respuesta
            enviar_email_pqrs_respondida(pqrs, respuesta)
            
            return Response({
                'success': True,
                'message': 'Respuesta enviada correctamente. El ciudadano será notificado por correo.',
                'data': PQRSDetailSerializer(pqrs).data
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def archivar(self, request, pk=None):
        """Archivar una PQRS"""
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