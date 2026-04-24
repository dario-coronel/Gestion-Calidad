from django.db import models
from django.utils import timezone
from apps.core.models import ModeloBase
from django.conf import settings


class EstadoQR(models.TextChoices):
    BORRADOR = 'borrador', 'Borrador'
    EN_REVISION = 'en_revision', 'En Revisión'
    EN_SEGUIMIENTO = 'en_seguimiento', 'En Seguimiento'
    CERRADO = 'cerrado', 'Cerrado'
    RECHAZADO = 'rechazado', 'Rechazado'


class TipoReclamo(models.TextChoices):
    CALIDAD_PRODUCTO = 'calidad_producto', 'Calidad del Producto en Destino'
    ENTREGA = 'entrega', 'Problema de Entrega'
    DOCUMENTACION = 'documentacion', 'Documentación'
    ATENCION = 'atencion', 'Atención al Cliente'
    OTRO = 'otro', 'Otro'


class QuejaReclamo(ModeloBase):
    """Queja o Reclamo de cliente. No incluye 5 Porqués ni Matriz de Riesgo."""
    folio = models.CharField(max_length=20, unique=True, editable=False)
    fecha = models.DateField(default=timezone.now)
    area_origen = models.CharField(max_length=100)
    responsable = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
        related_name='qr_responsable'
    )
    id_cliente_pedido = models.CharField(max_length=100)
    tipo_reclamo = models.CharField(max_length=30, choices=TipoReclamo)
    descripcion = models.TextField()
    prioridad = models.CharField(
        max_length=10,
        choices=[('baja', 'Baja'), ('media', 'Media'), ('alta', 'Alta')],
        default='media'
    )
    clasificacion = models.CharField(max_length=100, blank=True)
    estado = models.CharField(max_length=20, choices=EstadoQR, default=EstadoQR.BORRADOR)
    dias_resolucion = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        verbose_name = 'Queja y Reclamo'
        verbose_name_plural = 'Quejas y Reclamos'
        ordering = ['-fecha']

    def __str__(self):
        return f'{self.folio} - {self.id_cliente_pedido}'

    def save(self, *args, **kwargs):
        if not self.folio:
            anio = self.fecha.year if self.fecha else timezone.now().year
            ultimo = QuejaReclamo.objects.filter(
                folio__startswith=f'QR-{anio}-'
            ).count()
            self.folio = f'QR-{anio}-{str(ultimo + 1).zfill(4)}'
        super().save(*args, **kwargs)


class AdjuntoQR(models.Model):
    qr = models.ForeignKey(QuejaReclamo, on_delete=models.CASCADE, related_name='adjuntos')
    archivo = models.FileField(upload_to='qr/adjuntos/%Y/%m/')
    nombre = models.CharField(max_length=255)
    subido_en = models.DateTimeField(auto_now_add=True)
    subido_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True
    )

    def __str__(self):
        return self.nombre

