import shutil
import os
from datetime import datetime
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
        # Obtener ruta de la base de datos SQLite
        db_path = settings.DATABASES['default']['NAME']
        
        if not os.path.exists(db_path):
            raise FileNotFoundError(f'Base de datos no encontrada: {db_path}')
        
        # Crear directorio de backups si no existe
        backup_dir = Path(settings.BASE_DIR) / 'backups'
        backup_dir.mkdir(exist_ok=True)
        
        # Generar nombre del archivo con timestamp
        timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f'sgc_backup_{timestamp}.db'
        backup_path = backup_dir / backup_filename
        
        # Realizar copia
        shutil.copy2(db_path, backup_path)
        
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
    
    for archivo in backup_dir.glob('*.db'):
        if archivo.stat().st_mtime < cutoff_time:
            try:
                archivo.unlink()
                eliminados += 1
            except Exception as e:
                print(f'Error al eliminar {archivo}: {e}')
    
    return eliminados
