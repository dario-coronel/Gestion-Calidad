from django.db import migrations


CLASIFICACIONES_INICIALES = [
    'Calidad',
    'General',
    'Mejora de Proceso',
    'Innovación / Mejora Continua',
    'Eficiencia Operativa',
    'Otro',
]


def seed_clasificaciones(apps, schema_editor):
    Clasificacion = apps.get_model('core', 'Clasificacion')
    for nombre in CLASIFICACIONES_INICIALES:
        Clasificacion.objects.get_or_create(nombre=nombre, defaults={'activo': True})


def unseed_clasificaciones(apps, schema_editor):
    Clasificacion = apps.get_model('core', 'Clasificacion')
    Clasificacion.objects.filter(nombre__in=CLASIFICACIONES_INICIALES).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_add_clasificacion'),
    ]

    operations = [
        migrations.RunPython(seed_clasificaciones, unseed_clasificaciones),
    ]
