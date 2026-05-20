from django.core.management.base import BaseCommand
from django.db import transaction

from apps.qr.models import QuejaReclamo


class Command(BaseCommand):
    help = (
        'Backfill de relaciones explícitas en QyR: '
        'nc_relacionada (desde NC.qr_relacionada) y '
        'om_asociada (desde NC.om_relacionada cuando aplique).'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Muestra qué actualizaría sin guardar cambios.',
        )
        parser.add_argument(
            '--overwrite',
            action='store_true',
            help='Permite sobreescribir nc_relacionada/om_asociada existentes.',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        overwrite = options['overwrite']

        total = 0
        updated_nc = 0
        updated_om = 0

        qs = QuejaReclamo.objects.filter(eliminado=False).order_by('id')

        if dry_run:
            self.stdout.write(self.style.WARNING('Modo dry-run: no se guardarán cambios.'))

        with transaction.atomic():
            for qr in qs:
                total += 1
                cambios = []

                ncs = list(qr.nc_relacionadas.select_related('om_relacionada').order_by('-fecha', '-id'))
                nc_candidata = ncs[0] if ncs else None

                if nc_candidata and (overwrite or qr.nc_relacionada_id is None):
                    if qr.nc_relacionada_id != nc_candidata.id:
                        qr.nc_relacionada = nc_candidata
                        cambios.append('nc_relacionada')

                om_candidata = None
                if nc_candidata and nc_candidata.om_relacionada_id:
                    om_candidata = nc_candidata.om_relacionada

                if om_candidata and (overwrite or qr.om_asociada_id is None):
                    if qr.om_asociada_id != om_candidata.id:
                        qr.om_asociada = om_candidata
                        cambios.append('om_asociada')

                if cambios:
                    if dry_run:
                        self.stdout.write(
                            f'QyR {qr.folio}: actualizar {", ".join(cambios)}'
                        )
                    else:
                        qr.save(update_fields=cambios)

                    if 'nc_relacionada' in cambios:
                        updated_nc += 1
                    if 'om_asociada' in cambios:
                        updated_om += 1

            if dry_run:
                transaction.set_rollback(True)

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('Backfill finalizado'))
        self.stdout.write(f'  QyR evaluadas: {total}')
        self.stdout.write(f'  NC vinculadas: {updated_nc}')
        self.stdout.write(f'  OM vinculadas: {updated_om}')
