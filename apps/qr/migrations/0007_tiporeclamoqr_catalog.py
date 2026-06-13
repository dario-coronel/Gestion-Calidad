from django.db import migrations, models


def seed_tipos_reclamo(apps, schema_editor):
    TipoReclamoQR = apps.get_model('qr', 'TipoReclamoQR')
    initial = [
        ('calidad_producto', 'Calidad del Producto en Destino', True),
        ('entrega', 'Problema de Entrega', False),
        ('documentacion', 'Documentación', False),
        ('atencion', 'Atención al Cliente', False),
        ('otro', 'Otro', False),
    ]
    for codigo, nombre, requiere_lote in initial:
        TipoReclamoQR.objects.update_or_create(
            codigo=codigo,
            defaults={
                'nombre': nombre,
                'activo': True,
                'requiere_lote': requiere_lote,
            },
        )


class Migration(migrations.Migration):

    dependencies = [
        ('qr', '0006_responsable_fk'),
    ]

    operations = [
        migrations.CreateModel(
            name='TipoReclamoQR',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('codigo', models.CharField(max_length=50, unique=True)),
                ('nombre', models.CharField(max_length=150, unique=True)),
                ('activo', models.BooleanField(default=True)),
                ('requiere_lote', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name': 'Tipo de Reclamo',
                'verbose_name_plural': 'Tipos de Reclamo',
                'ordering': ['nombre'],
            },
        ),
        migrations.AlterField(
            model_name='quejareclamo',
            name='tipo_reclamo',
            field=models.CharField(max_length=50),
        ),
        migrations.RunPython(seed_tipos_reclamo, migrations.RunPython.noop),
    ]
