from django.db import models
from django.conf import settings


class ModeloBase(models.Model):
    """Modelo abstracto con campos de auditoría compartidos por todas las entidades."""
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL, related_name='%(class)s_creados'
    )
    actualizado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL, related_name='%(class)s_actualizados'
    )
    eliminado = models.BooleanField(default=False)  # soft delete

    class Meta:
        abstract = True

