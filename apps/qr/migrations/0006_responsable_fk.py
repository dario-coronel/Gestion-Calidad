import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_seed_responsables_from_users'),
        ('qr', '0005_split_actions_add_lote'),
    ]

    operations = [
        migrations.AlterField(
            model_name='quejareclamo',
            name='responsable',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name='qr_responsable',
                to='core.responsable',
            ),
        ),
    ]
