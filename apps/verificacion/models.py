from django.db import models
from django.utils import timezone
from datetime import timedelta
from apps.core.models import ModeloBase
from django.conf import settings


class EstadoVerificacion(models.TextChoices):
    PENDIENTE = 'pendiente', 'Pendiente'
    EN_REVISION = 'en_revision', 'En Revisión'
    EFICAZ = 'eficaz', 'Eficaz'
    NO_EFICAZ = 'no_eficaz', 'No Eficaz'


class VerificacionEficacia(ModeloBase):
    """
    Verificación de eficacia post-cierre de un Proyecto.
    Se crea automáticamente al finalizar el Proyecto.
    Si resultado == NO_EFICAZ → genera nueva NC automáticamente.
    """
    proyecto = models.OneToOneField(
        'proyectos.Proyecto', on_delete=models.CASCADE,
        related_name='verificacion_eficacia'
    )
    fecha_cierre_proyecto = models.DateField()
    fecha_objetivo = models.DateField(
        help_text='Fecha en que se debe realizar la verificación (cierre + 90 días)'
    )
    estado = models.CharField(
        max_length=15, choices=EstadoVerificacion,
        default=EstadoVerificacion.PENDIENTE
    )
    responsable = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL, related_name='verificaciones'
    )
    fecha_realizada = models.DateField(null=True, blank=True)
    resultado_descripcion = models.TextField(blank=True)
    evidencia = models.FileField(upload_to='verificacion/%Y/%m/', null=True, blank=True)
    # Si No Eficaz, referencia a la NC generada
    nc_generada = models.ForeignKey(
        'nc.NoConformidad', null=True, blank=True,
        on_delete=models.SET_NULL, related_name='origen_verificacion'
    )

    class Meta:
        verbose_name = 'Verificación de Eficacia'
        verbose_name_plural = 'Verificaciones de Eficacia'
        ordering = ['fecha_objetivo']

    def __str__(self):
        return f'Verificación de {self.proyecto.folio} — {self.get_estado_display()}'

    @property
    def dias_restantes(self):
        return (self.fecha_objetivo - timezone.now().date()).days

    @property
    def vencida(self):
        return (
            self.estado == EstadoVerificacion.PENDIENTE
            and timezone.now().date() > self.fecha_objetivo
        )

    @classmethod
    def crear_para_proyecto(cls, proyecto, dias_aviso=90):
        """Crea la verificación al finalizar un proyecto."""
        fecha_cierre = proyecto.fecha_fin or timezone.now().date()
        return cls.objects.create(
            proyecto=proyecto,
            fecha_cierre_proyecto=fecha_cierre,
            fecha_objetivo=fecha_cierre + timedelta(days=dias_aviso),
            responsable=proyecto.responsable,
        )

