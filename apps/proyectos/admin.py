from django.contrib import admin

from .models import Proyecto, Subtarea


class SubtareaInline(admin.TabularInline):
	model = Subtarea
	extra = 0


@admin.register(Proyecto)
class ProyectoAdmin(admin.ModelAdmin):
	list_display = ('folio', 'nombre', 'sector', 'origen', 'prioridad', 'estado', 'fecha_inicio')
	list_filter = ('estado', 'origen', 'prioridad', 'sector')
	search_fields = ('folio', 'nombre', 'proveedor')
	readonly_fields = ('folio', 'creado_en', 'actualizado_en')
	inlines = [SubtareaInline]

