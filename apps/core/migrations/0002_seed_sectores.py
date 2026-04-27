from django.db import migrations


SECTORES_INICIALES = [
    'Produccion Balanceado',
    'Produccion Aceitera',
    'Produccion Cluster',
    'Acopio',
    'Mantenimiento',
    'Administracion',
    'IT',
    'Logistica',
    'Comercial',
    'Laboratorio',
]


def seed_sectores(apps, schema_editor):
    Sector = apps.get_model('core', 'Sector')
    for nombre in SECTORES_INICIALES:
        Sector.objects.get_or_create(nombre=nombre, defaults={'activo': True})


def unseed_sectores(apps, schema_editor):
    Sector = apps.get_model('core', 'Sector')
    Sector.objects.filter(nombre__in=SECTORES_INICIALES).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_add_sector_fks'),
    ]

    operations = [
        migrations.RunPython(seed_sectores, unseed_sectores),
    ]