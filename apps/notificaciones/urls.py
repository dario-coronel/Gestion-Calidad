from django.urls import path
from . import views

app_name = 'notificaciones'

urlpatterns = [
    path('', views.panel, name='lista'),
    path('panel/', views.panel, name='panel'),
    path('<int:pk>/leida/', views.marcar_leida, name='marcar_leida'),
    path('todas-leidas/', views.marcar_todas, name='marcar_todas'),
]