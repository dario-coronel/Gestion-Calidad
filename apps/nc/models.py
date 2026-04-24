from django.db import models
from django.utils import timezone
from apps.core.models import ModeloBase
from django.conf import settings


class EstadoNC(models.TextChoices):
    BORRADOR = 'borrador', 'Borrador'
    EN_REVISION = 'en_revision', 'En Revisión'
    APROBADA = 'aprobada', 'Aprobada'
    EN_IMPLEMENTACION = 'en_implementacion', 'En Implementación'
    CERRADA = 'cerrada', 'Cerrada'
    RECHAZADA = 'rechazada', 'Rechazada'


class PrioridadNC(models.TextChoices):
    BAJA = 'baja', 'Baja'
    MEDIA = 'media', 'Media'
    ALTA = 'alta', 'Alta'
    CRITICA = 'critica', 'Crítica'


class ClasificacionNC(models.TextChoices):
    MATERIAL_NO_CONFORME = 'material_no_conforme', 'Material no conforme'
    PROCESO = 'proceso', 'Proceso'
    PRODUCTO = 'producto', 'Producto'
    SISTEMA = 'sistema', 'Sistema'
    LOGISTICA = 'logistica', 'Logística'


class NoConformidad(ModeloBase):
    """No Conformidad detectada en el sistema de gestión de calidad."""
    folio = models.CharField(max_length=20, unique=True, editable=False)
    fecha = models.DateField(default=timezone.now)
    area = models.CharField(max_length=100)
    responsable = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
        related_name='nc_responsable'
    )
    id_muestra_lote = models.CharField(max_length=100, blank=True)
    parametro_afectado = models.CharField(max_length=100, blank=True)
    descripcion = models.TextField()
    prioridad = models.CharField(max_length=10, choices=PrioridadNC, default=PrioridadNC.MEDIA)
    clasificacion = models.CharField(max_length=30, choices=ClasificacionNC)
    estado = models.CharField(max_length=20, choices=EstadoNC, default=EstadoNC.BORRADOR)
    # Matriz de riesgo
    probabilidad = models.PositiveSmallIntegerField(null=True, blank=True, help_text='1-5')
    impacto = models.PositiveSmallIntegerField(null=True, blank=True, help_text='1-5')

    class Meta:
        verbose_name = 'No Conformidad'
        verbose_name_plural = 'No Conformidades'
        ordering = ['-fecha']

    def __str__(self):
        return f'{self.folio} - {self.descripcion[:60]}'

    @property
    def riesgo_calculado(self):
        if self.probabilidad and self.impacto:
            return self.probabilidad * self.impacto
        return None

    def save(self, *args, **kwargs):
        if not self.folio:
            anio = self.fecha.year if self.fecha else timezone.now().year
            ultimo = NoConformidad.objects.filter(
                folio__startswith=f'NC-{anio}-'
            ).count()
            self.folio = f'NC-{anio}-{str(ultimo + 1).zfill(4)}'
        super().save(*args, **kwargs)


class CincoPorques(ModeloBase):
    """Análisis de causa raíz 5 Porqués, exclusivo de No Conformidades."""
    nc = models.OneToOneField(NoConformidad, on_delete=models.CASCADE, related_name='cinco_porques')
    etapa_1 = models.TextField(help_text='Problema detectado (se pre-carga desde la NC)')
    etapa_2 = models.TextField(blank=True, help_text='¿Por qué? (Why 1)')
    etapa_3 = models.TextField(blank=True, help_text='¿Por qué? (Why 2)')
    etapa_4 = models.TextField(blank=True, help_text='¿Por qué? (Why 3)')
    etapa_5 = models.TextField(blank=True, help_text='¿Por qué? (Why 4)')
    causa_raiz = models.TextField(blank=True, help_text='Causa raíz identificada (Why 5)')
    accion_correctiva = models.TextField(blank=True)
    completo = models.BooleanField(default=False)

    class Meta:
        verbose_name = '5 Porqués'
        verbose_name_plural = '5 Porqués'

    def __str__(self):
        return f'5P de {self.nc.folio}'


class AdjuntoNC(models.Model):
    """Archivos adjuntos de una No Conformidad."""
    nc = models.ForeignKey(NoConformidad, on_delete=models.CASCADE, related_name='adjuntos')
    archivo = models.FileField(upload_to='nc/adjuntos/%Y/%m/')
    nombre = models.CharField(max_length=255)
    subido_en = models.DateTimeField(auto_now_add=True)
    subido_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True
    )

    def __str__(self):
        return self.nombre

