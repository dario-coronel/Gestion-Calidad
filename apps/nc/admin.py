from django.contrib import admin
from .models import (
    NoConformidad, CincoPorques, AdjuntoNC, CausaRaizIdentificada,
    NormaNC, PuntoNormaNC,
)


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


class PuntoNormaNCInline(admin.TabularInline):
    model = PuntoNormaNC
    extra = 1
    fields = ('codigo', 'descripcion', 'activo')


@admin.register(NormaNC)
class NormaNCAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'activo', 'creado_en')
    list_filter = ('activo', 'creado_en')
    search_fields = ('nombre', 'descripcion', 'puntos__codigo', 'puntos__descripcion')
    readonly_fields = ('creado_en', 'actualizado_en', 'creado_por', 'actualizado_por')
    inlines = [PuntoNormaNCInline]

    def has_add_permission(self, request):
        return CausaRaizIdentificadaAdmin._es_admin_o_calidad(self, request.user)

    def has_change_permission(self, request, obj=None):
        return CausaRaizIdentificadaAdmin._es_admin_o_calidad(self, request.user)

    def has_delete_permission(self, request, obj=None):
        return CausaRaizIdentificadaAdmin._es_admin_o_calidad(self, request.user)


@admin.register(NoConformidad)
class NoConformidadAdmin(admin.ModelAdmin):
    list_display = ('folio', 'fecha', 'sector', 'norma', 'punto_norma', 'prioridad', 'clasificacion', 'estado', 'riesgo_calculado')
    list_filter = ('estado', 'prioridad', 'clasificacion', 'sector', 'norma')
    search_fields = ('folio', 'descripcion', 'id_muestra_lote', 'norma__nombre', 'punto_norma__codigo', 'punto_norma__descripcion')
    inlines = [CincoPorquesInline, AdjuntoNCInline]
    readonly_fields = ('folio', 'creado_en', 'actualizado_en')

