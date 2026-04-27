from django.db import models
from django.conf import settings


class RegistroBackup(models.Model):
    """Registro de copias de seguridad realizadas."""
    
    TIPO_CHOICES = [
        ('manual', 'Manual'),
        ('automatico', 'Automático'),
    ]
    
    STATUS_CHOICES = [
        ('exitoso', 'Exitoso'),
        ('error', 'Error'),
        ('en_proceso', 'En proceso'),
    ]
    
    fecha_hora = models.DateTimeField(auto_now_add=True)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    estado = models.CharField(max_length=20, choices=STATUS_CHOICES, default='en_proceso')
    ruta_archivo = models.CharField(max_length=500, blank=True)
    tamaño_mb = models.FloatField(null=True, blank=True)
    mensaje_error = models.TextField(blank=True)
    realizado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='backups_realizados',
        help_text='Usuario que ejecutó el backup (vacío si fue automático)'
    )
    
    class Meta:
        ordering = ['-fecha_hora']
        verbose_name = 'Registro de Backup'
        verbose_name_plural = 'Registros de Backup'
    
    def __str__(self):
        return f'{self.get_tipo_display()} - {self.fecha_hora.strftime("%d/%m/%Y %H:%M")} - {self.get_estado_display()}'
