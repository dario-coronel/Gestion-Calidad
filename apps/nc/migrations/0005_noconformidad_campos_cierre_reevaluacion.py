from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('nc', '0004_alter_cincoporques_etapa_1'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='noconformidad',
            name='dias_cierre',
            field=models.PositiveIntegerField(blank=True, null=True, verbose_name='Cantidad de dias de cierre'),
        ),
        migrations.AddField(
            model_name='noconformidad',
            name='fecha_implementacion_accion',
            field=models.DateField(blank=True, null=True, verbose_name='Fecha de implementación de acción correctiva'),
        ),
        migrations.AddField(
            model_name='noconformidad',
            name='rango_dias_reevaluacion',
            field=models.PositiveSmallIntegerField(blank=True, choices=[(30, '30 dias'), (60, '60 dias'), (90, '90 dias'), (120, '120 dias'), (150, '150 dias'), (180, '180 dias'), (360, '360 dias')], null=True, verbose_name='Rango de dias para reevaluación'),
        ),
        migrations.AddField(
            model_name='noconformidad',
            name='responsable_accion',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='nc_responsable_accion', to=settings.AUTH_USER_MODEL, verbose_name='Responsable de la acción'),
        ),
    ]
