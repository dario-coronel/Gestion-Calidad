from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.backups.utils import ejecutar_backup


class Command(BaseCommand):
    help = 'Ejecuta un backup manual de la base de datos.'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--tipo',
            type=str,
            default='manual',
            help='Tipo de backup: manual o automatico',
        )
    
    def handle(self, *args, **options):
        tipo = options.get('tipo', 'manual')
        
        self.stdout.write(self.style.WARNING('🔄 Iniciando backup...'))
        
        registro = ejecutar_backup(tipo=tipo)
        
        if registro.estado == 'exitoso':
            self.stdout.write(
                self.style.SUCCESS(
                    f'✓ Backup exitoso\n'
                    f'  Archivo: {registro.ruta_archivo}\n'
                    f'  Tamaño: {registro.tamaño_mb:.2f} MB'
                )
            )
        else:
            self.stdout.write(
                self.style.ERROR(
                    f'✗ Error al realizar backup\n'
                    f'  {registro.mensaje_error}'
                )
            )
