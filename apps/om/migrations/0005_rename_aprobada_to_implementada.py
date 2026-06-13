from django.db import migrations, models


def forwards_convert_estado(apps, schema_editor):
    OportunidadMejora = apps.get_model('om', 'OportunidadMejora')
    OportunidadMejora.objects.filter(estado='aprobada').update(estado='implementada')


def backwards_convert_estado(apps, schema_editor):
    OportunidadMejora = apps.get_model('om', 'OportunidadMejora')
    OportunidadMejora.objects.filter(estado='implementada').update(estado='aprobada')


class Migration(migrations.Migration):

    dependencies = [
        ('om', '0004_responsable_fk'),
    ]

    operations = [
        migrations.RunPython(forwards_convert_estado, backwards_convert_estado),
        migrations.AlterField(
            model_name='oportunidadmejora',
            name='estado',
            field=models.CharField(
                choices=[
                    ('borrador', 'Borrador'),
                    ('en_revision', 'En Revisión'),
                    ('implementada', 'Implementada'),
                    ('en_implementacion', 'En Implementación'),
                    ('cerrada', 'Cerrada'),
                    ('rechazada', 'Rechazada'),
                ],
                default='borrador',
                max_length=20,
            ),
        ),
    ]
