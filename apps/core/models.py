from django.db import models
from django.conf import settings


class Sector(models.Model):
    """Sectores de la empresa. Tabla transversal usada por NC, QR y OM."""
    nombre = models.CharField(max_length=100, unique=True)
    activo = models.BooleanField(default=True)

    class Meta:
        ordering = ['nombre']
        verbose_name = 'Sector'
        verbose_name_plural = 'Sectores'

    def __str__(self):
        return self.nombre


class Clasificacion(models.Model):
    """Clasificaciones transversales para OM y QR."""
    nombre = models.CharField(max_length=100, unique=True)
    activo = models.BooleanField(default=True)

    class Meta:
        ordering = ['nombre']
        verbose_name = 'Clasificación'
        verbose_name_plural = 'Clasificaciones'

    def __str__(self):
        return self.nombre


class Responsable(models.Model):
    """Responsables operativos seleccionables en NC, QR, OM, Proyectos y Verificaciones."""
    nombre = models.CharField(max_length=150, unique=True)
    email = models.EmailField(blank=True)
    activo = models.BooleanField(default=True)
    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='responsable_perfil',
    )

    class Meta:
        ordering = ['nombre']
        verbose_name = 'Responsable'
        verbose_name_plural = 'Responsables'

    def __str__(self):
        return self.nombre

    def corresponde_a_usuario(self, user):
        return bool(user and user.is_authenticated and self.usuario_id == user.id)


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

