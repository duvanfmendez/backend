from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from .models import Notificacion


def enviar_email_pqrs_creada(pqrs):
    """Envía email cuando se crea una PQRS"""
    
    asunto = f"PQRS Registrada Exitosamente - {pqrs.numero_radicado}"
    
    mensaje = f"""
Estimado/a {pqrs.nombre_completo},

Su PQRS ha sido registrada exitosamente en nuestro sistema.

DATOS DE SU SOLICITUD:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Número de Radicado: {pqrs.numero_radicado}
Tipo: {pqrs.get_tipo_display()}
Asunto: {pqrs.asunto}
Fecha de Radicación: {pqrs.fecha_radicacion.strftime('%d/%m/%Y %H:%M')}
Fecha Límite de Respuesta: {pqrs.fecha_limite_respuesta.strftime('%d/%m/%Y')}

IMPORTANTE:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Guarde este número de radicado para consultar el estado de su solicitud.

Puede consultar el estado en cualquier momento ingresando su número de radicado.

Atentamente,
Sistema de PQRS - ELITE
    """
    
    # Crear registro de notificación
    notificacion = Notificacion.objects.create(
        pqrs=pqrs,
        tipo='pqrs_creada',
        destinatario_email=pqrs.correo_electronico,
        asunto=asunto,
        mensaje=mensaje
    )
    
    try:
        # Enviar email
        send_mail(
            subject=asunto,
            message=mensaje,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[pqrs.correo_electronico],
            fail_silently=False,
        )
        
        # Marcar como enviado
        notificacion.enviado = True
        notificacion.fecha_envio = timezone.now()
        notificacion.save()
        
        return True
    
    except Exception as e:
        # Registrar error
        notificacion.error = str(e)
        notificacion.save()
        return False


def enviar_email_pqrs_respondida(pqrs, respuesta):
    """Envía email cuando se responde una PQRS"""
    
    asunto = f"Respuesta a su PQRS - {pqrs.numero_radicado}"
    
    mensaje = f"""
Estimado/a {pqrs.nombre_completo},

Su PQRS ha sido respondida por nuestro equipo.

DATOS DE SU SOLICITUD:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Número de Radicado: {pqrs.numero_radicado}
Tipo: {pqrs.get_tipo_display()}
Asunto: {pqrs.asunto}

RESPUESTA:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{respuesta.respuesta}

Respondido por: {respuesta.usuario.get_full_name() if respuesta.usuario else 'Sistema'}
Fecha: {respuesta.fecha_respuesta.strftime('%d/%m/%Y %H:%M')}

Si tiene alguna pregunta adicional, no dude en contactarnos.

Atentamente,
Sistema de PQRS - ELITE
    """
    
    # Crear registro de notificación
    notificacion = Notificacion.objects.create(
        pqrs=pqrs,
        tipo='pqrs_respondida',
        destinatario_email=pqrs.correo_electronico,
        asunto=asunto,
        mensaje=mensaje
    )
    
    try:
        # Enviar email
        send_mail(
            subject=asunto,
            message=mensaje,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[pqrs.correo_electronico],
            fail_silently=False,
        )
        
        # Marcar como enviado
        notificacion.enviado = True
        notificacion.fecha_envio = timezone.now()
        notificacion.save()
        
        return True
    
    except Exception as e:
        # Registrar error
        notificacion.error = str(e)
        notificacion.save()
        return False
    
    