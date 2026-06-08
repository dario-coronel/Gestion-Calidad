import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_seed_responsables_from_users'),
        ('om', '0003_alter_oportunidadmejora_clasificacion'),
    ]

    operations = [
        migrations.AlterField(
            model_name='oportunidadmejora',
            name='responsable',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name='om_responsable',
                to='core.responsable',
            ),
        ),
    ]
