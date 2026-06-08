import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_seed_responsables_from_users'),
        ('nc', '0009_alter_noconformidad_origen'),
    ]

    operations = [
        migrations.AlterField(
            model_name='noconformidad',
            name='responsable',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name='nc_responsable',
                to='core.responsable',
            ),
        ),
        migrations.AlterField(
            model_name='noconformidad',
            name='responsable_accion',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='nc_responsable_accion',
                to='core.responsable',
                verbose_name='Responsable de la acción',
            ),
        ),
    ]
