"""
Señales que generan notificaciones automáticas ante eventos del sistema.
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse


@receiver(post_save, sender='nc.NoConformidad')
def nc_creada_o_actualizada(sender, instance, created, **kwargs):
    from .utils import notificar_calidad, crear_notificacion
    from .models import TipoNotificacion

    try:
        url = reverse('nc:detalle', args=[instance.pk])
    except Exception:
        url = ''

    if created:
        area_nc = getattr(instance, 'area', None) or '—'
        notificar_calidad(
            tipo=TipoNotificacion.NC_PENDIENTE,
            titulo=f'Nueva NC registrada: {instance.folio}',
            mensaje=f'Se registró la NC {instance.folio} en el área {area_nc}. '
                    f'Prioridad: {instance.get_prioridad_display()}.',
            url_destino=url,
        )


@receiver(post_save, sender='qr.QuejaReclamo')
def qr_creado(sender, instance, created, **kwargs):
    from .utils import notificar_calidad
    from .models import TipoNotificacion

    if not created:
        return

    try:
        url = reverse('qr:detalle', args=[instance.pk])
    except Exception:
        url = ''

    notificar_calidad(
        tipo=TipoNotificacion.QR_SIN_RESPUESTA,
        titulo=f'Nuevo reclamo registrado: {instance.folio}',
        mensaje=f'Se registró el reclamo {instance.folio} '
                f'({instance.get_tipo_reclamo_display()}). '
                f'Prioridad: {instance.get_prioridad_display()}.',
        url_destino=url,
    )


@receiver(post_save, sender='proyectos.Proyecto')
def proyecto_finalizado(sender, instance, created, **kwargs):
    from .utils import crear_notificacion
    from .models import TipoNotificacion

    if created or instance.estado != 'finalizado':
        return
    if not instance.responsable_id:
        return

    try:
        url = reverse('proyectos:detalle', args=[instance.pk])
    except Exception:
        url = ''

    crear_notificacion(
        usuario=instance.responsable,
        tipo=TipoNotificacion.PROYECTO_VENCIDO,
        titulo=f'Proyecto finalizado: {instance.folio}',
        mensaje=f'El proyecto "{instance.nombre}" fue marcado como Finalizado. '
                f'Se generó una verificación de eficacia automáticamente.',
        url_destino=url,
    )


@receiver(post_save, sender='verificacion.VerificacionEficacia')
def verificacion_no_eficaz(sender, instance, created, **kwargs):
    from .utils import notificar_calidad, crear_notificacion
    from .models import TipoNotificacion

    if created or instance.estado != 'no_eficaz':
        return

    try:
        url = reverse('verificacion:detalle', args=[instance.pk])
    except Exception:
        url = ''

    notificar_calidad(
        tipo=TipoNotificacion.VERIFICACION_EFICACIA,
        titulo=f'Verificación NO EFICAZ: {instance.proyecto.folio}',
        mensaje=f'La verificación del proyecto {instance.proyecto.folio} resultó No Eficaz. '
                f'Se requiere una nueva acción correctiva.',
        url_destino=url,
    )

    # También notificar al responsable del proyecto
    if instance.proyecto.responsable_id:
        crear_notificacion(
            usuario=instance.proyecto.responsable,
            tipo=TipoNotificacion.VERIFICACION_EFICACIA,
            titulo=f'Verificación NO EFICAZ: {instance.proyecto.folio}',
            mensaje=f'La verificación del proyecto "{instance.proyecto.nombre}" resultó No Eficaz.',
            url_destino=url,
        )
