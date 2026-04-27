"""
Señales de No Conformidades.
Regla: al aprobar una NC se crea automáticamente un Proyecto vinculado.
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from .models import NoConformidad, EstadoNC


@receiver(post_save, sender=NoConformidad)
def crear_proyecto_desde_nc(sender, instance, created, **kwargs):
    """
    Al pasar una NC al estado APROBADA, genera automáticamente
    un Proyecto vinculado si todavía no existe.
    """
    if instance.estado != EstadoNC.APROBADA:
        return

    # Importación diferida para evitar circular imports
    from apps.proyectos.models import Proyecto, OrigenProyecto, PrioridadProyecto

    # Evita crear duplicado si el proyecto ya existe
    if hasattr(instance, 'proyecto') and instance.proyecto is not None:
        return

    # Mapeo de prioridad NC → Proyecto
    mapa_prioridad = {
        'baja': PrioridadProyecto.BAJA,
        'media': PrioridadProyecto.MEDIA,
        'alta': PrioridadProyecto.ALTA,
        'critica': PrioridadProyecto.ALTA,
    }

    Proyecto.objects.create(
        nombre=f'Corrección de {instance.folio}',
        sector=instance.sector,
        prioridad=mapa_prioridad.get(instance.prioridad, PrioridadProyecto.MEDIA),
        fecha_inicio=timezone.now().date(),
        dias_ejecucion=30,
        responsable=instance.responsable,
        origen=OrigenProyecto.NC,
        nc=instance,
        creado_por=instance.creado_por,
    )
