"""
Comando: python manage.py seed_grupos

Crea (o actualiza) los tres grupos de seguridad del SGC y asigna
a cada usuario existente el grupo que corresponde a su rol.

Grupos:
  Calidad_Admin     → roles calidad + admin  → CRUD en todos los módulos
  Operadores_Planta → rol operario           → crear y ver NC/QR/OM
  Gerencia          → rol manager            → solo lectura en todo

Uso:
  python manage.py seed_grupos            # crea grupos y sincroniza usuarios
  python manage.py seed_grupos --solo-grupos  # solo crea/actualiza grupos sin tocar usuarios
"""

from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand

from apps.accounts.models import Rol, Usuario
from apps.accounts.signals import sincronizar_grupo


# ---------------------------------------------------------------------------
# Definición de permisos por grupo
# Formato: { 'app_label.codename': 'solo para documentar', ... }
# ---------------------------------------------------------------------------

PERMISOS_CALIDAD_ADMIN = [
    # No Conformidades
    'nc.add_noconformidad', 'nc.change_noconformidad',
    'nc.delete_noconformidad', 'nc.view_noconformidad',
    # Quejas y Reclamos
    'qr.add_quejareclamo', 'qr.change_quejareclamo',
    'qr.delete_quejareclamo', 'qr.view_quejareclamo',
    # Oportunidades de Mejora
    'om.add_oportunidadmejora', 'om.change_oportunidadmejora',
    'om.delete_oportunidadmejora', 'om.view_oportunidadmejora',
    # Proyectos
    'proyectos.add_proyecto', 'proyectos.change_proyecto',
    'proyectos.delete_proyecto', 'proyectos.view_proyecto',
    'proyectos.add_subtarea', 'proyectos.change_subtarea',
    'proyectos.delete_subtarea', 'proyectos.view_subtarea',
    # Verificación de Eficacia
    'verificacion.add_verificacioneficacia', 'verificacion.change_verificacioneficacia',
    'verificacion.delete_verificacioneficacia', 'verificacion.view_verificacioneficacia',
    # Sectores / Catálogos
    'core.add_sector', 'core.change_sector',
    'core.delete_sector', 'core.view_sector',
    # Adjuntos NC
    'nc.add_adjuntonc', 'nc.change_adjuntonc',
    'nc.delete_adjuntonc', 'nc.view_adjuntonc',
]

PERMISOS_OPERADORES_PLANTA = [
    # NC: solo crear y ver
    'nc.add_noconformidad', 'nc.view_noconformidad',
    'nc.add_adjuntonc', 'nc.view_adjuntonc',
    # QR: solo crear y ver
    'qr.add_quejareclamo', 'qr.view_quejareclamo',
    # OM: solo crear y ver
    'om.add_oportunidadmejora', 'om.view_oportunidadmejora',
    # Proyectos y Verificación: solo ver
    'proyectos.view_proyecto', 'proyectos.view_subtarea',
    'verificacion.view_verificacioneficacia',
    'core.view_sector',
]

PERMISOS_GERENCIA = [
    # Todo en modo lectura
    'nc.view_noconformidad', 'nc.view_adjuntonc',
    'qr.view_quejareclamo',
    'om.view_oportunidadmejora',
    'proyectos.view_proyecto', 'proyectos.view_subtarea',
    'verificacion.view_verificacioneficacia',
    'core.view_sector',
]

GRUPOS = {
    'Calidad_Admin':     PERMISOS_CALIDAD_ADMIN,
    'Operadores_Planta': PERMISOS_OPERADORES_PLANTA,
    'Gerencia':          PERMISOS_GERENCIA,
}


def _get_perm(codename_completo: str) -> Permission | None:
    """Retorna el objeto Permission dado 'app_label.codename', o None si no existe."""
    try:
        app_label, codename = codename_completo.split('.')
        return Permission.objects.get(codename=codename, content_type__app_label=app_label)
    except (Permission.DoesNotExist, ValueError):
        return None


class Command(BaseCommand):
    help = 'Crea los grupos del SGC con sus permisos y sincroniza usuarios existentes'

    def add_arguments(self, parser):
        parser.add_argument(
            '--solo-grupos',
            action='store_true',
            help='Solo crea/actualiza los grupos sin sincronizar usuarios existentes',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_HEADING('▶ Configurando grupos de seguridad SGC…'))

        # ── 1. Crear/actualizar grupos con sus permisos ──────────────────────
        for nombre_grupo, codenames in GRUPOS.items():
            grupo, creado = Group.objects.get_or_create(name=nombre_grupo)
            accion = 'Creado' if creado else 'Actualizado'

            permisos = []
            faltantes = []
            for codename in codenames:
                p = _get_perm(codename)
                if p:
                    permisos.append(p)
                else:
                    faltantes.append(codename)

            grupo.permissions.set(permisos)

            self.stdout.write(
                f'  {self.style.SUCCESS("✓")} {accion}: {nombre_grupo} '
                f'({len(permisos)} permisos)'
            )
            for f in faltantes:
                self.stdout.write(
                    f'    {self.style.WARNING("⚠")} Permiso no encontrado: {f}'
                )

        # ── 2. Sincronizar usuarios existentes ────────────────────────────────
        if options['solo_grupos']:
            self.stdout.write(self.style.SUCCESS('\n✓ Grupos actualizados (sin sincronizar usuarios).'))
            return

        self.stdout.write(self.style.MIGRATE_HEADING('\n▶ Sincronizando usuarios con sus grupos…'))
        usuarios = Usuario.objects.all()
        for u in usuarios:
            sincronizar_grupo(u)
            grupo_asignado = GRUPOS.keys() and next(
                (g for g, _ in {
                    Rol.ADMIN: 'Calidad_Admin',
                    Rol.CALIDAD: 'Calidad_Admin',
                    Rol.MANAGER: 'Gerencia',
                    Rol.OPERARIO: 'Operadores_Planta',
                }.items() if g == u.rol), '?'
            )
            nombre_grupo_asignado = {
                Rol.ADMIN:    'Calidad_Admin',
                Rol.CALIDAD:  'Calidad_Admin',
                Rol.MANAGER:  'Gerencia',
                Rol.OPERARIO: 'Operadores_Planta',
            }.get(u.rol, '—')
            self.stdout.write(
                f'  {self.style.SUCCESS("✓")} {u.username:<20} '
                f'rol={u.rol:<10} → grupo={nombre_grupo_asignado}'
            )

        self.stdout.write(
            self.style.SUCCESS(f'\n✓ {usuarios.count()} usuarios sincronizados.')
        )
        self.stdout.write('')
        self.stdout.write('  Grupos activos:')
        for nombre_grupo in GRUPOS:
            g = Group.objects.get(name=nombre_grupo)
            miembros = g.user_set.count()
            self.stdout.write(f'    • {nombre_grupo}: {miembros} usuario(s)')
