from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nc', '0003_add_sector_fks'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cincoporques',
            name='etapa_1',
            field=models.TextField(blank=True, help_text='Problema detectado (se pre-carga desde la NC)'),
        ),
    ]
