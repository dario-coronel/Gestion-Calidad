from django.contrib.auth.models import AbstractUser
from django.db import models


class Rol(models.TextChoices):
    OPERARIO = 'operario', 'Operario'
    CALIDAD = 'calidad', 'Calidad'
    MANAGER = 'manager', 'Manager'
    ADMIN = 'admin', 'Administrador'


class Usuario(AbstractUser):
    """Usuario del sistema con rol asignado."""
    rol = models.CharField(max_length=20, choices=Rol, default=Rol.OPERARIO)
    area = models.CharField(max_length=100, blank=True)
    telefono = models.CharField(max_length=30, blank=True)

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'

    def __str__(self):
        return f'{self.get_full_name() or self.username} ({self.get_rol_display()})'

    @property
    def es_calidad(self):
        return self.rol in (Rol.CALIDAD, Rol.MANAGER, Rol.ADMIN)

    @property
    def es_manager(self):
        return self.rol in (Rol.MANAGER, Rol.ADMIN)

    @property
    def es_admin(self):
        return self.rol == Rol.ADMIN

    @property
    def es_operario(self):
        return self.rol == Rol.OPERARIO

