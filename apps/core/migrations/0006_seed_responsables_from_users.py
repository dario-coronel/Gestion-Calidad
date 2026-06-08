from django.conf import settings
from django.db import migrations


def seed_responsables(apps, schema_editor):
    """
    Crea un Responsable por cada Usuario existente, forzando el mismo PK
    para que las FK actuales (que almacenan user IDs) queden automáticamente
    válidas al cambiar el target de la FK a core.Responsable.
    """
    app_label, model_name = settings.AUTH_USER_MODEL.split('.')
    Usuario = apps.get_model(app_label, model_name)
    Responsable = apps.get_model('core', 'Responsable')

    for user in Usuario.objects.order_by('id'):
        nombre = f"{user.first_name} {user.last_name}".strip() or user.username
        # Garantizar unicidad si dos usuarios comparten nombre completo
        base_nombre = nombre
        if Responsable.objects.filter(nombre=nombre).exists():
            nombre = f"{base_nombre} ({user.username})"

        Responsable.objects.create(
            id=user.id,
            nombre=nombre,
            email=user.email or '',
            activo=user.is_active,
            usuario_id=user.id,
        )

    # Reiniciar secuencia PostgreSQL para que próximos inserts no colisionen
    if schema_editor.connection.vendor == 'postgresql':
        schema_editor.execute(
            "SELECT setval("
            "  pg_get_serial_sequence('core_responsable', 'id'),"
            "  COALESCE((SELECT MAX(id) FROM core_responsable), 1)"
            ")"
        )


def unseed_responsables(apps, schema_editor):
    apps.get_model('core', 'Responsable').objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_responsable'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RunPython(seed_responsables, unseed_responsables),
    ]
