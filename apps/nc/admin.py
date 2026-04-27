from django.contrib import admin
from .models import NoConformidad, CincoPorques, AdjuntoNC


class CincoPorquesInline(admin.StackedInline):
    model = CincoPorques
    extra = 0


class AdjuntoNCInline(admin.TabularInline):
    model = AdjuntoNC
    extra = 0


@admin.register(NoConformidad)
class NoConformidadAdmin(admin.ModelAdmin):
    list_display = ('folio', 'fecha', 'sector', 'prioridad', 'clasificacion', 'estado', 'riesgo_calculado')
    list_filter = ('estado', 'prioridad', 'clasificacion', 'sector')
    search_fields = ('folio', 'descripcion', 'id_muestra_lote')
    inlines = [CincoPorquesInline, AdjuntoNCInline]
    readonly_fields = ('folio', 'creado_en', 'actualizado_en')

