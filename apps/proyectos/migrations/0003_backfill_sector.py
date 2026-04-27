from django.db import migrations


def backfill_sector(apps, schema_editor):
    Proyecto = apps.get_model('proyectos', 'Proyecto')

    for proyecto in Proyecto.objects.filter(sector__isnull=True).select_related('nc', 'om'):
        sector = None
        if proyecto.nc_id and getattr(proyecto.nc, 'sector_id', None):
            sector = proyecto.nc.sector
        elif proyecto.om_id and getattr(proyecto.om, 'sector_id', None):
            sector = proyecto.om.sector

        if sector is not None:
            proyecto.sector = sector
            proyecto.save(update_fields=['sector'])


class Migration(migrations.Migration):

    dependencies = [
        ('proyectos', '0002_add_sector_and_origin_links'),
    ]

    operations = [
        migrations.RunPython(backfill_sector, migrations.RunPython.noop),
    ]