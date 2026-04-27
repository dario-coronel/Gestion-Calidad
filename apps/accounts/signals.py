"""
Signals de accounts: sincroniza automáticamente el Grupo Django del usuario
cada vez que su campo `rol` cambia.

Grupos manejados:
  Calidad_Admin     → roles calidad + admin
  Operadores_Planta → rol operario
  Gerencia          → rol manager
"""
from django.contrib.auth.models import Group
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Rol, Usuario

# Mapa rol → nombre del grupo
_ROL_A_GRUPO = {
    Rol.ADMIN:    'Calidad_Admin',
    Rol.CALIDAD:  'Calidad_Admin',
    Rol.MANAGER:  'Gerencia',
    Rol.OPERARIO: 'Operadores_Planta',
}

# Todos los grupos gestionados (para poder quitarlos antes de asignar el correcto)
_GRUPOS_SGC = set(_ROL_A_GRUPO.values())


def sincronizar_grupo(usuario: Usuario) -> None:
    """Asegura que el usuario pertenezca solo al grupo que corresponde a su rol.
    Si los grupos aún no existen (primera ejecución) no falla."""
    nombre_grupo = _ROL_A_GRUPO.get(usuario.rol)
    if not nombre_grupo:
        return

    try:
        grupos_sgc = Group.objects.filter(name__in=_GRUPOS_SGC)
        # Quitar todos los grupos SGC y asignar el correcto
        usuario.groups.remove(*grupos_sgc)
        grupo, _ = Group.objects.get_or_create(name=nombre_grupo)
        usuario.groups.add(grupo)
    except Exception:
        # Si la tabla de grupos aún no existe (durante migrate inicial) ignorar
        pass


@receiver(post_save, sender=Usuario)
def usuario_post_save(sender, instance: Usuario, created: bool, **kwargs):
    """Sincroniza el grupo del usuario cada vez que se guarda."""
    sincronizar_grupo(instance)
