from django.db import models
from django.utils import timezone
from apps.core.models import ModeloBase
from django.conf import settings


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


class OportunidadMejora(ModeloBase):
    """Oportunidad de Mejora. No incluye 5 Porqués ni Matriz de Riesgo."""
    folio = models.CharField(max_length=20, unique=True, editable=False)
    fecha = models.DateField(default=timezone.now)
    sector = models.CharField(max_length=100)
    responsable = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
        related_name='om_responsable'
    )
    descripcion = models.TextField(help_text='Descripción de la oportunidad o sugerencia')
    beneficio_potencial = models.CharField(
        max_length=10,
        choices=[('baja', 'Baja'), ('media', 'Media'), ('alta', 'Alta')],
        default='media'
    )
    clasificacion = models.CharField(max_length=30, choices=ClasificacionOM)
    estado = models.CharField(max_length=20, choices=EstadoOM, default=EstadoOM.BORRADOR)

    class Meta:
        verbose_name = 'Oportunidad de Mejora'
        verbose_name_plural = 'Oportunidades de Mejora'
        ordering = ['-fecha']

    def __str__(self):
        return f'{self.folio} - {self.descripcion[:60]}'

    def save(self, *args, **kwargs):
        if not self.folio:
            anio = self.fecha.year if self.fecha else timezone.now().year
            ultimo = OportunidadMejora.objects.filter(
                folio__startswith=f'OM-{anio}-'
            ).count()
            self.folio = f'OM-{anio}-{str(ultimo + 1).zfill(4)}'
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

