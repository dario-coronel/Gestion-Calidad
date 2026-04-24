from django.db import models
from django.conf import settings


class TipoNotificacion(models.TextChoices):
    VERIFICACION_EFICACIA = 'verificacion_eficacia', 'Verificación de Eficacia'
    NC_PENDIENTE = 'nc_pendiente', 'NC Pendiente'
    PROYECTO_VENCIDO = 'proyecto_vencido', 'Proyecto Vencido'
    QR_SIN_RESPUESTA = 'qr_sin_respuesta', 'QR Sin Respuesta'
    SISTEMA = 'sistema', 'Sistema'


class Notificacion(models.Model):
    """
    Notificación de campana para el usuario.
    Se genera automáticamente por eventos del sistema.
    """
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='notificaciones'
    )
    tipo = models.CharField(max_length=30, choices=TipoNotificacion)
    titulo = models.CharField(max_length=200)
    mensaje = models.TextField()
    leida = models.BooleanField(default=False)
    creada_en = models.DateTimeField(auto_now_add=True)
    leida_en = models.DateTimeField(null=True, blank=True)
    # Referencia opcional al objeto relacionado
    url_destino = models.CharField(max_length=500, blank=True)

    class Meta:
        verbose_name = 'Notificación'
        verbose_name_plural = 'Notificaciones'
        ordering = ['-creada_en']

    def __str__(self):
        return f'[{self.tipo}] {self.titulo} → {self.usuario.username}'

    def marcar_leida(self):
        from django.utils import timezone
        self.leida = True
        self.leida_en = timezone.now()
        self.save(update_fields=['leida', 'leida_en'])

