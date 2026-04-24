"""
Context processor global: inyecta el contador de notificaciones no leídas
en todos los templates para mostrar el badge en la campana.
"""
from apps.notificaciones.models import Notificacion


def notificaciones(request):
    if not request.user.is_authenticated:
        return {'notif_no_leidas': 0}
    count = Notificacion.objects.filter(
        usuario=request.user, leida=False
    ).count()
    return {'notif_no_leidas': count}
