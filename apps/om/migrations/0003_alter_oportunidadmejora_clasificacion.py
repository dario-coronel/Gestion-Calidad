from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('om', '0002_add_sector_fks'),
    ]

    operations = [
        migrations.AlterField(
            model_name='oportunidadmejora',
            name='clasificacion',
            field=models.CharField(blank=True, max_length=100),
        ),
    ]
