from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('om', '0005_rename_aprobada_to_implementada'),
    ]

    operations = [
        migrations.AddField(
            model_name='oportunidadmejora',
            name='explicacion_eficacia',
            field=models.TextField(blank=True, help_text='Detalle de por qué la OM fue considerada eficaz.', verbose_name='Explicación de eficacia'),
        ),
    ]
