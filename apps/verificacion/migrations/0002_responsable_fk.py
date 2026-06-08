import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_seed_responsables_from_users'),
        ('verificacion', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='verificacioneficacia',
            name='responsable',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='verificaciones',
                to='core.responsable',
            ),
        ),
    ]
