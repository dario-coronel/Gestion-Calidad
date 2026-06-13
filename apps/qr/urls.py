from django.urls import path
from . import views

app_name = 'qr'

urlpatterns = [
    path('', views.lista, name='lista'),
    path('nuevo/', views.crear, name='crear'),
    path('tipos-reclamo/', views.tipos_reclamo_lista, name='tipos_reclamo_lista'),
    path('tipos-reclamo/nuevo/', views.tipo_reclamo_crear, name='tipo_reclamo_crear'),
    path('tipos-reclamo/<int:pk>/editar/', views.tipo_reclamo_editar, name='tipo_reclamo_editar'),
    path('tipos-reclamo/<int:pk>/eliminar/', views.tipo_reclamo_eliminar, name='tipo_reclamo_eliminar'),
    path('<int:pk>/', views.detalle, name='detalle'),
    path('<int:pk>/editar/', views.editar, name='editar'),
    path('<int:pk>/pdf/', views.pdf, name='pdf'),
]
