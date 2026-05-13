from django.contrib import admin
from .models import NoConformidad, CincoPorques, AdjuntoNC, CausaRaizIdentificada


class CincoPorquesInline(admin.StackedInline):
    model = CincoPorques
    extra = 0


class AdjuntoNCInline(admin.TabularInline):
    model = AdjuntoNC
    extra = 0


@admin.register(CausaRaizIdentificada)
class CausaRaizIdentificadaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'activo', 'creado_en')
    list_filter = ('activo', 'creado_en')
    search_fields = ('nombre', 'descripcion')
    readonly_fields = ('creado_en', 'actualizado_en', 'creado_por', 'actualizado_por')
    fieldsets = (
        ('Información General', {
            'fields': ('nombre', 'descripcion', 'activo')
        }),
        ('Auditoría', {
            'fields': ('creado_en', 'actualizado_en', 'creado_por', 'actualizado_por'),
            'classes': ('collapse',)
        }),
    )

    def has_add_permission(self, request):
        return self._es_admin_o_calidad(request.user)

    def has_change_permission(self, request, obj=None):
        return self._es_admin_o_calidad(request.user)

    def has_delete_permission(self, request, obj=None):
        return self._es_admin_o_calidad(request.user)

    def _es_admin_o_calidad(self, user):
        """Verifica si el usuario es admin o calidad."""
        if user.es_admin or user.is_staff or user.is_superuser:
            return True
        # Verificar si tiene rol CALIDAD
        from apps.accounts.models import Rol
        return user.rol == Rol.CALIDAD


@admin.register(NoConformidad)
class NoConformidadAdmin(admin.ModelAdmin):
    list_display = ('folio', 'fecha', 'sector', 'prioridad', 'clasificacion', 'estado', 'riesgo_calculado')
    list_filter = ('estado', 'prioridad', 'clasificacion', 'sector')
    search_fields = ('folio', 'descripcion', 'id_muestra_lote')
    inlines = [CincoPorquesInline, AdjuntoNCInline]
    readonly_fields = ('folio', 'creado_en', 'actualizado_en')

