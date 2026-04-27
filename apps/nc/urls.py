from django.urls import path
from . import views

app_name = 'nc'

urlpatterns = [
    path('', views.lista, name='lista'),
    path('nueva/', views.crear, name='crear'),
    path('<int:pk>/', views.detalle, name='detalle'),
    path('<int:pk>/editar/', views.editar, name='editar'),
    path('<int:pk>/pdf/resumen/', views.pdf_resumen, name='pdf_resumen'),
    path('<int:pk>/pdf/completo/', views.pdf_completo, name='pdf_completo'),
]
