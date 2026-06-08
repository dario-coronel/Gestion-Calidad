import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_seed_responsables_from_users'),
        ('proyectos', '0003_backfill_sector'),
    ]

    operations = [
        migrations.AlterField(
            model_name='proyecto',
            name='responsable',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name='proyectos_responsable',
                to='core.responsable',
            ),
        ),
    ]
