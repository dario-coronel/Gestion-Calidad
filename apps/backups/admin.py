from django.contrib import admin
from .models import RegistroBackup


@admin.register(RegistroBackup)
class RegistroBackupAdmin(admin.ModelAdmin):
    list_display = ('fecha_hora', 'tipo', 'estado', 'tamaño_mb', 'realizado_por')
    list_filter = ('tipo', 'estado', 'fecha_hora')
    search_fields = ('ruta_archivo', 'mensaje_error')
    readonly_fields = ('fecha_hora', 'ruta_archivo', 'tamaño_mb', 'mensaje_error', 'realizado_por')
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
