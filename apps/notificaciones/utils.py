"""
Utilidades para crear notificaciones de forma centralizada.
"""
from django.contrib.auth import get_user_model

from .models import Notificacion, TipoNotificacion

Usuario = get_user_model()


def crear_notificacion(usuario, tipo, titulo, mensaje, url_destino=''):
    """Crea una notificación para el usuario dado, evitando duplicados recientes (últimas 24 h)."""
    from django.utils import timezone
    from datetime import timedelta

    hace_24h = timezone.now() - timedelta(hours=24)
    ya_existe = Notificacion.objects.filter(
        usuario=usuario,
        tipo=tipo,
        titulo=titulo,
        leida=False,
        creada_en__gte=hace_24h,
    ).exists()

    if not ya_existe:
        Notificacion.objects.create(
            usuario=usuario,
            tipo=tipo,
            titulo=titulo,
            mensaje=mensaje,
            url_destino=url_destino,
        )


def notificar_calidad(tipo, titulo, mensaje, url_destino=''):
    """Envía la notificación a todos los usuarios con rol calidad, manager o admin."""
    for usuario in Usuario.objects.filter(
        rol__in=['calidad', 'manager', 'admin'], is_active=True
    ):
        crear_notificacion(usuario, tipo, titulo, mensaje, url_destino)
