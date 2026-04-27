import shutil
import os
import subprocess
from pathlib import Path
from django.conf import settings
from django.utils import timezone
from .models import RegistroBackup


def ejecutar_backup(tipo='manual', usuario=None):
    """
    Ejecuta backup de la base de datos.
    
    Args:
        tipo: 'manual' o 'automatico'
        usuario: Usuario que ejecuta el backup (para backups manuales)
    
    Returns:
        RegistroBackup: Registro del backup realizado
    """
    # Crear registro en base de datos
    registro = RegistroBackup.objects.create(
        tipo=tipo,
        estado='en_proceso',
        realizado_por=usuario if tipo == 'manual' else None,
    )
    
    try:
        # Crear directorio de backups si no existe
        backup_dir = Path(settings.BASE_DIR) / 'backups'
        backup_dir.mkdir(exist_ok=True)

        # Generar nombre del archivo con timestamp
        timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
        db_config = settings.DATABASES['default']
        db_engine = db_config.get('ENGINE', '')

        if db_engine == 'django.db.backends.sqlite3':
            db_path = db_config.get('NAME')

            if not db_path or not os.path.exists(db_path):
                raise FileNotFoundError(f'Base de datos no encontrada: {db_path}')

            backup_filename = f'sgc_backup_{timestamp}.sqlite3'
            backup_path = backup_dir / backup_filename
            shutil.copy2(db_path, backup_path)

        elif db_engine in ('django.db.backends.postgresql', 'django.db.backends.postgresql_psycopg2'):
            if shutil.which('pg_dump') is None:
                raise FileNotFoundError(
                    'No se encontro pg_dump en el sistema. Instala cliente de PostgreSQL para generar backups.'
                )

            backup_filename = f'sgc_backup_{timestamp}.sql'
            backup_path = backup_dir / backup_filename

            env = os.environ.copy()
            if db_config.get('PASSWORD'):
                env['PGPASSWORD'] = db_config['PASSWORD']
            if db_config.get('OPTIONS', {}).get('sslmode'):
                env['PGSSLMODE'] = db_config['OPTIONS']['sslmode']

            command = [
                'pg_dump',
                '-h', db_config.get('HOST') or 'localhost',
                '-p', str(db_config.get('PORT') or '5432'),
                '-U', db_config.get('USER') or '',
                '-d', db_config.get('NAME') or '',
                '-f', str(backup_path),
            ]

            result = subprocess.run(command, capture_output=True, text=True, env=env, check=False)
            if result.returncode != 0:
                error = result.stderr.strip() or result.stdout.strip() or 'Error desconocido al ejecutar pg_dump'
                raise RuntimeError(error)

        else:
            raise NotImplementedError(f'Motor de base de datos no soportado para backup: {db_engine}')
        
        # Obtener tamaño del archivo
        tamaño_bytes = os.path.getsize(backup_path)
        tamaño_mb = tamaño_bytes / (1024 * 1024)
        
        # Actualizar registro
        registro.estado = 'exitoso'
        registro.ruta_archivo = str(backup_path)
        registro.tamaño_mb = tamaño_mb
        registro.save()
        
        return registro
    
    except Exception as e:
        # Registrar error
        registro.estado = 'error'
        registro.mensaje_error = str(e)
        registro.save()
        
        return registro


def limpiar_backups_antiguos(dias=30):
    """
    Elimina backups más antiguos que N días.
    
    Args:
        dias: Días de antigüedad para considerar como "antigua"
    """
    backup_dir = Path(settings.BASE_DIR) / 'backups'
    
    if not backup_dir.exists():
        return 0
    
    cutoff_time = timezone.now().timestamp() - (dias * 24 * 60 * 60)
    eliminados = 0
    
    for archivo in backup_dir.glob('sgc_backup_*'):
        if not archivo.is_file():
            continue
        if archivo.stat().st_mtime < cutoff_time:
            try:
                archivo.unlink()
                eliminados += 1
            except Exception as e:
                print(f'Error al eliminar {archivo}: {e}')
    
    return eliminados
