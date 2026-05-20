from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('qr', '0004_add_nc_om_links'),
    ]

    operations = [
        migrations.AddField(
            model_name='quejareclamo',
            name='acciones_a_tomar_correctivas',
            field=models.TextField(blank=True, verbose_name='Acciones a tomar correctivas'),
        ),
        migrations.AddField(
            model_name='quejareclamo',
            name='id_muestra_lote',
            field=models.CharField(blank=True, max_length=100, verbose_name='ID Muestra / LOTE'),
        ),
    ]
