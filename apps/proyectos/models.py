from django.db import models
from django.utils import timezone
from datetime import timedelta
from apps.core.models import ModeloBase
from django.conf import settings


class PrioridadProyecto(models.TextChoices):
    BAJA = 'baja', 'Baja'
    MEDIA = 'media', 'Media'
    ALTA = 'alta', 'Alta'


class EstadoProyecto(models.TextChoices):
    POR_HACER = 'por_hacer', 'Por Hacer'
    EN_CURSO = 'en_curso', 'En Curso'
    FINALIZADO = 'finalizado', 'Finalizado'


class OrigenProyecto(models.TextChoices):
    NC = 'nc', 'No Conformidad'
    OM = 'om', 'Oportunidad de Mejora'
    INDEPENDIENTE = 'independiente', 'Independiente'


class Proyecto(ModeloBase):
    """
    Proyecto de mejora o correctivo.
    Reglas:
      - Si origen == NC: nc FK es obligatorio y se crea automáticamente al aprobar la NC.
      - Si origen == OM: om FK es opcional.
      - Si origen == INDEPENDIENTE: ambas FK son nulas.
    """
    folio = models.CharField(max_length=20, unique=True, editable=False)
    nombre = models.CharField(max_length=255)
    prioridad = models.CharField(max_length=10, choices=PrioridadProyecto, default=PrioridadProyecto.MEDIA)
    proveedor = models.CharField(max_length=200, blank=True, help_text='Proveedor externo o "Interno"')
    fecha_inicio = models.DateField()
    dias_ejecucion = models.PositiveIntegerField(help_text='Días de ejecución estimados')
    responsable = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
        related_name='proyectos_responsable'
    )
    estado = models.CharField(max_length=15, choices=EstadoProyecto, default=EstadoProyecto.POR_HACER)
    origen = models.CharField(max_length=15, choices=OrigenProyecto, default=OrigenProyecto.INDEPENDIENTE)
    # FK de origen (mutuamente excluyentes)
    nc = models.OneToOneField(
        'nc.NoConformidad', null=True, blank=True,
        on_delete=models.SET_NULL, related_name='proyecto'
    )
    om = models.ForeignKey(
        'om.OportunidadMejora', null=True, blank=True,
        on_delete=models.SET_NULL, related_name='proyectos'
    )

    class Meta:
        verbose_name = 'Proyecto'
        verbose_name_plural = 'Proyectos'
        ordering = ['-fecha_inicio']

    def __str__(self):
        return f'{self.folio} - {self.nombre}'

    @property
    def fecha_fin(self):
        """Fecha de finalización calculada, nunca ingresada manualmente."""
        if self.fecha_inicio and self.dias_ejecucion:
            return self.fecha_inicio + timedelta(days=self.dias_ejecucion)
        return None

    @property
    def porcentaje_avance(self):
        total = self.subtareas.count()
        if total == 0:
            return 0
        completadas = self.subtareas.filter(completada=True).count()
        return round((completadas / total) * 100)

    def save(self, *args, **kwargs):
        if not self.folio:
            anio = self.fecha_inicio.year if self.fecha_inicio else timezone.now().year
            ultimo = Proyecto.objects.filter(
                folio__startswith=f'PRY-{anio}-'
            ).count()
            self.folio = f'PRY-{anio}-{str(ultimo + 1).zfill(4)}'
        super().save(*args, **kwargs)


class Subtarea(models.Model):
    """Subtarea o hito dentro de un Proyecto."""
    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE, related_name='subtareas')
    descripcion = models.CharField(max_length=500)
    completada = models.BooleanField(default=False)
    orden = models.PositiveSmallIntegerField(default=0)
    completada_en = models.DateTimeField(null=True, blank=True)
    completada_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL
    )

    class Meta:
        ordering = ['orden']

    def __str__(self):
        estado = '✓' if self.completada else '○'
        return f'{estado} {self.descripcion[:80]}'

