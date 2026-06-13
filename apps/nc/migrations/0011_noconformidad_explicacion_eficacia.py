from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nc', '0010_responsable_fk'),
    ]

    operations = [
        migrations.AddField(
            model_name='noconformidad',
            name='explicacion_eficacia',
            field=models.TextField(blank=True, help_text='Detalle de por qué la acción fue considerada eficaz.', verbose_name='Explicación de eficacia'),
        ),
    ]
