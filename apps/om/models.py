from django.db import models
from django.utils import timezone
from apps.core.models import ModeloBase, Sector
from django.conf import settings
from calendar import monthrange


class EstadoOM(models.TextChoices):
    BORRADOR = 'borrador', 'Borrador'
    EN_REVISION = 'en_revision', 'En Revisión'
    APROBADA = 'aprobada', 'Aprobada'
    EN_IMPLEMENTACION = 'en_implementacion', 'En Implementación'
    CERRADA = 'cerrada', 'Cerrada'
    RECHAZADA = 'rechazada', 'Rechazada'


class ClasificacionOM(models.TextChoices):
    MEJORA_PROCESO = 'mejora_proceso', 'Mejora de Proceso'
    INNOVACION = 'innovacion', 'Innovación / Mejora Continua'
    EFICIENCIA = 'eficiencia', 'Eficiencia Operativa'
    CALIDAD = 'calidad', 'Calidad'
    OTRO = 'otro', 'Otro'


class RangoEvaluacion(models.TextChoices):
    UN_MES    = '1m', '1 mes'
    TRES_MESES = '3m', '3 meses'
    SEIS_MESES = '6m', '6 meses'


class EficaciaOM(models.TextChoices):
    PENDIENTE  = 'pendiente',  'Pendiente de evaluación'
    EFICAZ     = 'eficaz',     'Eficaz'
    NO_EFICAZ  = 'no_eficaz',  'No Eficaz'


class OportunidadMejora(ModeloBase):
    """Oportunidad de Mejora. No incluye 5 Porqués ni Matriz de Riesgo."""
    folio = models.CharField(max_length=20, unique=True, editable=False)
    fecha = models.DateField(default=timezone.now)
    sector = models.ForeignKey(
        Sector, on_delete=models.PROTECT,
        null=True, blank=True, related_name='om_sector',
        verbose_name='Sector'
    )
    responsable = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
        related_name='om_responsable'
    )
    descripcion = models.TextField(help_text='Descripción de la oportunidad o sugerencia')
    problema_a_mejorar = models.TextField('Problema a mejorar', blank=True)
    beneficio_potencial = models.CharField(
        max_length=10,
        choices=[('baja', 'Baja'), ('media', 'Media'), ('alta', 'Alta')],
        default='media'
    )
    clasificacion = models.CharField(max_length=30, choices=ClasificacionOM)
    estado = models.CharField(max_length=20, choices=EstadoOM, default=EstadoOM.BORRADOR)

    # Seguimiento y evaluación
    seguimiento = models.TextField('Seguimiento', blank=True)
    evidencia = models.TextField('Evidencia', blank=True)
    rango_evaluacion = models.CharField(
        'Rango de evaluación', max_length=2,
        choices=RangoEvaluacion, blank=True
    )
    fecha_evaluacion = models.DateField('Fecha de evaluación', null=True, blank=True)
    fecha_implementacion = models.DateField('Fecha de implementación', null=True, blank=True)
    eficacia = models.CharField(
        max_length=10, choices=EficaciaOM, default=EficaciaOM.PENDIENTE
    )
    om_origen = models.ForeignKey(
        'self', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='om_generadas',
        verbose_name='OM que originó esta (No Eficaz)',
    )

    class Meta:
        verbose_name = 'Oportunidad de Mejora'
        verbose_name_plural = 'Oportunidades de Mejora'
        ordering = ['-fecha']

    def __str__(self):
        return f'{self.folio} - {self.descripcion[:60]}'

    @staticmethod
    def _sumar_meses(fecha, meses):
        """Suma N meses a una fecha sin depender de dateutil."""
        m = fecha.month - 1 + meses
        year = fecha.year + m // 12
        month = m % 12 + 1
        import datetime
        day = min(fecha.day, monthrange(year, month)[1])
        return datetime.date(year, month, day)

    def save(self, *args, **kwargs):
        if not self.folio:
            anio = self.fecha.year if self.fecha else timezone.now().year
            ultimo = OportunidadMejora.objects.filter(
                folio__startswith=f'OM-{anio}-'
            ).count()
            self.folio = f'OM-{anio}-{str(ultimo + 1).zfill(4)}'
        # Auto-calcular fecha_evaluacion si hay rango
        if self.fecha and self.rango_evaluacion:
            meses_map = {'1m': 1, '3m': 3, '6m': 6}
            meses = meses_map.get(self.rango_evaluacion)
            if meses:
                self.fecha_evaluacion = self._sumar_meses(self.fecha, meses)
        super().save(*args, **kwargs)


class AdjuntoOM(models.Model):
    om = models.ForeignKey(OportunidadMejora, on_delete=models.CASCADE, related_name='adjuntos')
    archivo = models.FileField(upload_to='om/adjuntos/%Y/%m/')
    nombre = models.CharField(max_length=255)
    subido_en = models.DateTimeField(auto_now_add=True)
    subido_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True
    )

    def __str__(self):
        return self.nombre

