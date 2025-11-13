from django.core.mail import EmailMessage
from django.conf import settings
from django.utils import timezone
from .models import Notificacion


def enviar_email_pqrs_creada(pqrs):
    """Envia email cuando se crea una PQRS"""
    
    asunto = f"PQRS Registrada - {pqrs.numero_radicado}"
    
    mensaje = f"""
Hola {pqrs.nombre_completo},

Su PQRS ha sido registrada exitosamente.

Numero de Radicado: {pqrs.numero_radicado}
Tipo: {pqrs.get_tipo_display()}
Asunto: {pqrs.asunto}
Fecha: {pqrs.fecha_radicacion.strftime('%d/%m/%Y %H:%M')}

Guarde este numero para consultar el estado.

Atentamente,
Sistema PQRS
    """
    
    notificacion = Notificacion.objects.create(
        pqrs=pqrs,
        tipo='pqrs_creada',
        destinatario_email=pqrs.correo_electronico,
        asunto=asunto,
        mensaje=mensaje
    )
    
    try:
        email = EmailMessage(
            subject=asunto,
            body=mensaje,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[pqrs.correo_electronico],
        )
        email.content_subtype = "plain"
        email.encoding = 'utf-8'
        email.send(fail_silently=False)
        
        notificacion.enviado = True
        notificacion.fecha_envio = timezone.now()
        notificacion.save()
        
        return True
    
    except Exception as e:
        notificacion.error = str(e)
        notificacion.save()
        print(f"Error: {e}")
        return False


def enviar_email_pqrs_respondida(pqrs, respuesta):
    """Envia email cuando se responde una PQRS"""
    
    asunto = f"Respuesta a PQRS - {pqrs.numero_radicado}"
    
    mensaje = f"""
Hola {pqrs.nombre_completo},

Su PQRS ha sido respondida.

Numero: {pqrs.numero_radicado}
Tipo: {pqrs.get_tipo_display()}

Respuesta:
{respuesta.respuesta}

Atentamente,
Sistema PQRS
    """
    
    notificacion = Notificacion.objects.create(
        pqrs=pqrs,
        tipo='pqrs_respondida',
        destinatario_email=pqrs.correo_electronico,
        asunto=asunto,
        mensaje=mensaje
    )
    
    try:
        email = EmailMessage(
            subject=asunto,
            body=mensaje,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[pqrs.correo_electronico],
        )
        email.content_subtype = "plain"
        email.encoding = 'utf-8'
        email.send(fail_silently=False)
        
        notificacion.enviado = True
        notificacion.fecha_envio = timezone.now()
        notificacion.save()
        
        return True
    
    except Exception as e:
        notificacion.error = str(e)
        notificacion.save()
        print(f"Error: {e}")
        return False