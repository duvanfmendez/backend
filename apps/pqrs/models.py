from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
import random
import string


def generar_radicado():
    """Genera un número de radicado único en formato: PQRS-YYYYMMDD-XXXX"""
    fecha = timezone.now().strftime('%Y%m%d')
    codigo = ''.join(random.choices(string.digits, k=4))
    return f"PQRS-{fecha}-{codigo}"


class PQRS(models.Model):
    """Modelo principal para gestionar Peticiones, Quejas, Reclamos y Sugerencias"""
    
    TIPO_CHOICES = [
        ('peticion', 'Petición'),
        ('queja', 'Queja'),
        ('reclamo', 'Reclamo'),
        ('sugerencia', 'Sugerencia'),
    ]
    
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('en_tramite', 'En Trámite'),
        ('vencido', 'Vencido'),
        ('resuelto', 'Resuelto'),
        ('cerrado', 'Cerrado'),
    ]
    
    COLOR_SEMAFORO_CHOICES = [
        ('verde', 'Verde - En plazo'),
        ('amarillo', 'Amarillo - Próximo a vencer'),
        ('rojo', 'Rojo - Vencido'),
    ]
    
    # Información básica
    numero_radicado = models.CharField(
        max_length=20, 
        unique=True, 
        default=generar_radicado,
        editable=False,
        verbose_name='Número de Radicado'
    )
    tipo = models.CharField(
        max_length=20, 
        choices=TIPO_CHOICES,
        verbose_name='Tipo'
    )
    asunto = models.CharField(
        max_length=200,
        verbose_name='Asunto'
    )
    descripcion = models.TextField(
        verbose_name='Descripción'
    )
    
    # Información del ciudadano
    nombre_completo = models.CharField(
        max_length=200,
        verbose_name='Nombre Completo'
    )
    correo_electronico = models.EmailField(
        verbose_name='Correo Electrónico'
    )
    telefono = models.CharField(
        max_length=20, 
        blank=True,
        verbose_name='Teléfono'
    )
    
    # Estado y seguimiento
    estado = models.CharField(
        max_length=20, 
        choices=ESTADO_CHOICES, 
        default='pendiente',
        verbose_name='Estado'
    )
    fecha_radicacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de Radicación'
    )
    fecha_limite_respuesta = models.DateTimeField(
        verbose_name='Fecha Límite de Respuesta'
    )
    fecha_cierre = models.DateTimeField(
        null=True, 
        blank=True,
        verbose_name='Fecha de Cierre'
    )
    
    # Sistema de semaforización
    dias_restantes = models.IntegerField(
        default=0,
        verbose_name='Días Restantes'
    )
    color_semaforo = models.CharField(
        max_length=10, 
        choices=COLOR_SEMAFORO_CHOICES,
        default='verde',
        verbose_name='Color del Semáforo'
    )
    
    # Archivos adjuntos
    archivo_adjunto = models.FileField(
        upload_to='pqrs_attachments/%Y/%m/', 
        null=True, 
        blank=True,
        verbose_name='Archivo Adjunto'
    )
    
    # Asignación
    area_responsable = models.CharField(
        max_length=100, 
        blank=True,
        verbose_name='Área Responsable'
    )
    responsable = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='pqrs_asignadas',
        verbose_name='Responsable'
    )
    
    # Auditoría
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Creado el'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Actualizado el'
    )
    
    class Meta:
        ordering = ['-fecha_radicacion']
        verbose_name = 'PQRS'
        verbose_name_plural = 'PQRS'
        indexes = [
            models.Index(fields=['numero_radicado']),
            models.Index(fields=['estado', 'fecha_radicacion']),
            models.Index(fields=['color_semaforo']),
        ]
    
    def __str__(self):
        return f"{self.numero_radicado} - {self.get_tipo_display()}"
    
    def save(self, *args, **kwargs):
        """Override save para calcular fecha límite y actualizar semáforo"""
        if not self.pk:  # Solo al crear
            self.calcular_fecha_limite()
        self.actualizar_semaforo()
        super().save(*args, **kwargs)
    
    def calcular_fecha_limite(self):
        """Calcula la fecha límite según el tipo de PQRS"""
        dias_por_tipo = {
            'peticion': 15,
            'queja': 15,
            'reclamo': 15,
            'sugerencia': 30,
        }
        dias = dias_por_tipo.get(self.tipo, 15)
        self.fecha_limite_respuesta = timezone.now() + timedelta(days=dias)
    
    def actualizar_semaforo(self):
        """Actualiza el color del semáforo según días restantes"""
        if self.estado in ['resuelto', 'cerrado']:
            self.color_semaforo = 'verde'
            return
        
        ahora = timezone.now()
        diferencia = (self.fecha_limite_respuesta - ahora).days
        self.dias_restantes = diferencia
        
        if diferencia < 0:
            self.color_semaforo = 'rojo'
            if self.estado != 'vencido':
                self.estado = 'vencido'
        elif diferencia <= 3:
            self.color_semaforo = 'amarillo'
        else:
            self.color_semaforo = 'verde'
    
    @property
    def esta_vencida(self):
        """Indica si la PQRS está vencida"""
        return timezone.now() > self.fecha_limite_respuesta


class HistorialPQRS(models.Model):
    """Registra todos los cambios de estado de una PQRS"""
    
    pqrs = models.ForeignKey(
        PQRS,
        on_delete=models.CASCADE,
        related_name='historial',
        verbose_name='PQRS'
    )
    estado_anterior = models.CharField(
        max_length=20, 
        blank=True,
        verbose_name='Estado Anterior'
    )
    estado_nuevo = models.CharField(
        max_length=20,
        verbose_name='Estado Nuevo'
    )
    observacion = models.TextField(
        verbose_name='Observación'
    )
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Usuario'
    )
    fecha_cambio = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de Cambio'
    )
    
    class Meta:
        ordering = ['-fecha_cambio']
        verbose_name = 'Historial'
        verbose_name_plural = 'Historiales'
    
    def __str__(self):
        return f"{self.pqrs.numero_radicado} - {self.estado_nuevo}"


class RespuestaPQRS(models.Model):
    """Almacena las respuestas dadas a una PQRS"""
    
    pqrs = models.ForeignKey(
        PQRS,
        on_delete=models.CASCADE,
        related_name='respuestas',
        verbose_name='PQRS'
    )
    respuesta = models.TextField(
        verbose_name='Respuesta'
    )
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Usuario'
    )
    fecha_respuesta = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de Respuesta'
    )
    notificado = models.BooleanField(
        default=False,
        verbose_name='Notificado'
    )
    
    class Meta:
        ordering = ['-fecha_respuesta']
        verbose_name = 'Respuesta'
        verbose_name_plural = 'Respuestas'
    
    def __str__(self):
        return f"Respuesta a {self.pqrs.numero_radicado}"
    