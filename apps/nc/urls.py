from django.urls import path
from . import views

app_name = 'nc'

urlpatterns = [
    path('', views.lista, name='lista'),
    path('nueva/', views.crear, name='crear'),
    path('normas/<int:norma_id>/puntos/', views.puntos_norma_por_norma, name='puntos_norma_por_norma'),
    path('<int:pk>/', views.detalle, name='detalle'),
    path('<int:pk>/editar/', views.editar, name='editar'),
    path('<int:pk>/pdf/resumen/', views.pdf_resumen, name='pdf_resumen'),
    path('<int:pk>/pdf/completo/', views.pdf_completo, name='pdf_completo'),
    
    # Causa Raíz Identificada
    path('causas-raiz/', views.causa_raiz_lista, name='causa_raiz_lista'),
    path('causas-raiz/nueva/', views.causa_raiz_crear, name='causa_raiz_crear'),
    path('causas-raiz/<int:pk>/', views.causa_raiz_detalle, name='causa_raiz_detalle'),
    path('causas-raiz/<int:pk>/editar/', views.causa_raiz_editar, name='causa_raiz_editar'),
    path('causas-raiz/<int:pk>/eliminar/', views.causa_raiz_eliminar, name='causa_raiz_eliminar'),

    # Normas
    path('normas/', views.norma_lista, name='norma_lista'),
    path('normas/nueva/', views.norma_crear, name='norma_crear'),
    path('normas/<int:pk>/', views.norma_detalle, name='norma_detalle'),
    path('normas/<int:pk>/editar/', views.norma_editar, name='norma_editar'),
    path('normas/<int:pk>/eliminar/', views.norma_eliminar, name='norma_eliminar'),
]
