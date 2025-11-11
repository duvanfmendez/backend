from django.db import models
from django.conf import settings


class Notificacion(models.Model):
    """Modelo para gestionar notificaciones por email"""
    
    TIPO_CHOICES = [
        ('pqrs_creada', 'PQRS Creada'),
        ('pqrs_respondida', 'PQRS Respondida'),
        ('pqrs_cerrada', 'PQRS Cerrada'),
        ('pqrs_vencida', 'PQRS Vencida'),
    ]
    
    pqrs = models.ForeignKey(
        'pqrs.PQRS',
        on_delete=models.CASCADE,
        related_name='notificaciones',
        verbose_name='PQRS'
    )
    tipo = models.CharField(
        max_length=20,
        choices=TIPO_CHOICES,
        verbose_name='Tipo'
    )
    destinatario_email = models.EmailField(
        verbose_name='Destinatario'
    )
    asunto = models.CharField(
        max_length=200,
        verbose_name='Asunto'
    )
    mensaje = models.TextField(
        verbose_name='Mensaje'
    )
    enviado = models.BooleanField(
        default=False,
        verbose_name='Enviado'
    )
    fecha_envio = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Fecha de Envío'
    )
    error = models.TextField(
        blank=True,
        verbose_name='Error'
    )
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de Creación'
    )
    
    class Meta:
        ordering = ['-fecha_creacion']
        verbose_name = 'Notificación'
        verbose_name_plural = 'Notificaciones'
    
    def __str__(self):
        return f"{self.get_tipo_display()} - {self.pqrs.numero_radicado}"