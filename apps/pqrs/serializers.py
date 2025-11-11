from rest_framework import serializers
from .models import PQRS, HistorialPQRS, RespuestaPQRS
import os


class HistorialSerializer(serializers.ModelSerializer):
    """Serializer para el historial de cambios"""
    
    usuario_nombre = serializers.CharField(
        source='usuario.get_full_name', 
        read_only=True
    )
    
    class Meta:
        model = HistorialPQRS
        fields = [
            'id',
            'estado_anterior',
            'estado_nuevo',
            'observacion',
            'usuario_nombre',
            'fecha_cambio',
        ]


class RespuestaSerializer(serializers.ModelSerializer):
    """Serializer para las respuestas"""
    
    usuario_nombre = serializers.CharField(
        source='usuario.get_full_name', 
        read_only=True
    )
    
    class Meta:
        model = RespuestaPQRS
        fields = [
            'id',
            'respuesta',
            'usuario_nombre',
            'fecha_respuesta',
            'notificado',
        ]


class PQRSCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear PQRS (público)"""
    
    class Meta:
        model = PQRS
        fields = [
            'tipo',
            'asunto',
            'descripcion',
            'nombre_completo',
            'correo_electronico',
            'telefono',
            'archivo_adjunto',
        ]
    
    def validate_archivo_adjunto(self, value):
        """Valida tamaño y tipo de archivo"""
        if value:
            # Validar tamaño (máx 10MB)
            if value.size > 10 * 1024 * 1024:
                raise serializers.ValidationError(
                    "El archivo no debe superar 10MB"
                )
            
            # Validar extensión
            extensiones_permitidas = [
                '.pdf', '.jpg', '.jpeg', '.png', 
                '.doc', '.docx', '.txt'
            ]
            ext = os.path.splitext(value.name)[1].lower()
            if ext not in extensiones_permitidas:
                raise serializers.ValidationError(
                    f"Formato no permitido. Use: {', '.join(extensiones_permitidas)}"
                )
        return value


class PQRSListSerializer(serializers.ModelSerializer):
    """Serializer para listar PQRS (tabla principal del admin)"""
    
    tipo_display = serializers.CharField(
        source='get_tipo_display', 
        read_only=True
    )
    estado_display = serializers.CharField(
        source='get_estado_display', 
        read_only=True
    )
    responsable_nombre = serializers.CharField(
        source='responsable.get_full_name',
        read_only=True,
        allow_null=True
    )
    
    class Meta:
        model = PQRS
        fields = [
            'id',
            'numero_radicado',
            'tipo',
            'tipo_display',
            'asunto',
            'nombre_completo',
            'estado',
            'estado_display',
            'fecha_radicacion',
            'fecha_limite_respuesta',
            'dias_restantes',
            'color_semaforo',
            'responsable_nombre',
            'area_responsable',
        ]


class PQRSDetailSerializer(serializers.ModelSerializer):
    """Serializer detallado para ver una PQRS específica"""
    
    tipo_display = serializers.CharField(
        source='get_tipo_display', 
        read_only=True
    )
    estado_display = serializers.CharField(
        source='get_estado_display', 
        read_only=True
    )
    color_semaforo_display = serializers.CharField(
        source='get_color_semaforo_display', 
        read_only=True
    )
    historial = HistorialSerializer(many=True, read_only=True)
    respuestas = RespuestaSerializer(many=True, read_only=True)
    esta_vencida = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = PQRS
        fields = '__all__'


class PQRSConsultaPublicaSerializer(serializers.ModelSerializer):
    """Serializer para consulta pública por radicado (sin auth)"""
    
    tipo_display = serializers.CharField(
        source='get_tipo_display', 
        read_only=True
    )
    estado_display = serializers.CharField(
        source='get_estado_display', 
        read_only=True
    )
    historial = HistorialSerializer(many=True, read_only=True)
    respuestas = RespuestaSerializer(many=True, read_only=True)
    
    class Meta:
        model = PQRS
        fields = [
            'numero_radicado',
            'tipo',
            'tipo_display',
            'asunto',
            'descripcion',
            'estado',
            'estado_display',
            'fecha_radicacion',
            'fecha_limite_respuesta',
            'dias_restantes',
            'color_semaforo',
            'historial',
            'respuestas',
        ]


class CambiarEstadoSerializer(serializers.Serializer):
    """Serializer para cambiar el estado de una PQRS"""
    
    estado_nuevo = serializers.ChoiceField(
        choices=PQRS.ESTADO_CHOICES
    )
    observacion = serializers.CharField(
        required=True,
        max_length=500
    )


class ResponderPQRSSerializer(serializers.Serializer):
    """Serializer para enviar una respuesta"""
    
    respuesta = serializers.CharField(required=True)