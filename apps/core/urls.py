from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('sectores/', views.sectores_lista, name='sectores_lista'),
    path('sectores/nuevo/', views.sector_crear, name='sector_crear'),
    path('sectores/<int:pk>/editar/', views.sector_editar, name='sector_editar'),
    path('sectores/<int:pk>/eliminar/', views.sector_eliminar, name='sector_eliminar'),
    path('clasificaciones/', views.clasificaciones_lista, name='clasificaciones_lista'),
    path('clasificaciones/nuevo/', views.clasificacion_crear, name='clasificacion_crear'),
    path('clasificaciones/<int:pk>/editar/', views.clasificacion_editar, name='clasificacion_editar'),
    path('clasificaciones/<int:pk>/eliminar/', views.clasificacion_eliminar, name='clasificacion_eliminar'),
    path('responsables/', views.responsables_lista, name='responsables_lista'),
    path('responsables/nuevo/', views.responsable_crear, name='responsable_crear'),
    path('responsables/<int:pk>/editar/', views.responsable_editar, name='responsable_editar'),
    path('responsables/<int:pk>/eliminar/', views.responsable_eliminar, name='responsable_eliminar'),
]

