from apscheduler.schedulers.background import BackgroundScheduler
from django.conf import settings
from .utils import ejecutar_backup, limpiar_backups_antiguos

scheduler = None


def start_scheduler():
    """Inicia el scheduler de backups automáticos."""
    global scheduler
    
    if scheduler is not None:
        return
    
    try:
        scheduler = BackgroundScheduler()
        
        # Backup automático cada noche a las 2:00 AM
        scheduler.add_job(
            ejecutar_backup,
            'cron',
            hour=2,
            minute=0,
            kwargs={'tipo': 'automatico'},
            id='backup_nocturo',
            name='Backup automático nocturno',
            replace_existing=True,
        )
        
        # Limpiar backups antiguos cada domingo a las 3:00 AM
        scheduler.add_job(
            limpiar_backups_antiguos,
            'cron',
            day_of_week='sun',
            hour=3,
            minute=0,
            kwargs={'dias': 30},
            id='limpiar_backups',
            name='Limpiar backups antiguos',
            replace_existing=True,
        )
        
        scheduler.start()
        print('✓ Scheduler de backups iniciado')
        print('  - Backup automático: 02:00 AM diariamente')
        print('  - Limpieza: Domingos 03:00 AM (backups > 30 días)')
    
    except Exception as e:
        print(f'Error al iniciar scheduler de backups: {e}')
