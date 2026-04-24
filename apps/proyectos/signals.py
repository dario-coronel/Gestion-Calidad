"""
Señales de Proyectos.
Regla: al finalizar un Proyecto se crea automáticamente la Verificación de Eficacia.
"""
from django.db.models.signals import pre_save
from django.dispatch import receiver

from .models import Proyecto, EstadoProyecto


@receiver(pre_save, sender=Proyecto)
def crear_verificacion_al_finalizar(sender, instance, **kwargs):
    """
    Cuando un proyecto pasa a estado FINALIZADO, crea la
    VerificacionEficacia si no existe todavía.
    """
    if not instance.pk:
        return  # objeto nuevo, aún no guardado

    try:
        anterior = Proyecto.objects.get(pk=instance.pk)
    except Proyecto.DoesNotExist:
        return

    # Detectar transición hacia FINALIZADO
    if (anterior.estado != EstadoProyecto.FINALIZADO
            and instance.estado == EstadoProyecto.FINALIZADO):

        from django.conf import settings
        from apps.verificacion.models import VerificacionEficacia

        dias = getattr(settings, 'VERIFICACION_DIAS_AVISO', 90)

        # Crear verificación (post_save no aplica aquí, usamos post_save en otro receiver)
        # Guardamos bandera para que post_save la ejecute
        instance._crear_verificacion = True
        instance._dias_verificacion = dias


@receiver(pre_save, sender=Proyecto)
def _set_verificacion_flag(sender, instance, **kwargs):
    # Inicializa el flag si no existe
    if not hasattr(instance, '_crear_verificacion'):
        instance._crear_verificacion = False


from django.db.models.signals import post_save


@receiver(post_save, sender=Proyecto)
def _crear_verificacion_post_save(sender, instance, **kwargs):
    if getattr(instance, '_crear_verificacion', False):
        from apps.verificacion.models import VerificacionEficacia
        dias = getattr(instance, '_dias_verificacion', 90)
        if not hasattr(instance, 'verificacion_eficacia'):
            VerificacionEficacia.crear_para_proyecto(instance, dias)
        instance._crear_verificacion = False
