from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.accounts'
    verbose_name = 'Usuarios y Accesos'

    def ready(self):
        import apps.accounts.signals  # noqa: F401 — registra los signals
