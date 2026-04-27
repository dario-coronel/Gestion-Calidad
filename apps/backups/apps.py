from django.apps import AppConfig


class BackupsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.backups'
    verbose_name = 'Copias de Seguridad'

    def ready(self):
        """Inicializar scheduler de backups al cargar la app."""
        from .scheduler import start_scheduler
        start_scheduler()
