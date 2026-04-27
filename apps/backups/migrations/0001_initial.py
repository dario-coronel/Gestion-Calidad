from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='RegistroBackup',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_hora', models.DateTimeField(auto_now_add=True)),
                ('tipo', models.CharField(choices=[('manual', 'Manual'), ('automatico', 'Automático')], max_length=20)),
                ('estado', models.CharField(choices=[('exitoso', 'Exitoso'), ('error', 'Error'), ('en_proceso', 'En proceso')], default='en_proceso', max_length=20)),
                ('ruta_archivo', models.CharField(blank=True, max_length=500)),
                ('tamaño_mb', models.FloatField(blank=True, null=True)),
                ('mensaje_error', models.TextField(blank=True)),
                ('realizado_por', models.ForeignKey(blank=True, help_text='Usuario que ejecutó el backup (vacío si fue automático)', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='backups_realizados', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Registro de Backup',
                'verbose_name_plural': 'Registros de Backup',
                'ordering': ['-fecha_hora'],
            },
        ),
    ]
