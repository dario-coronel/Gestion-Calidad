from django.urls import path
from .views import (
    SGCLoginView,
    SGCLogoutView,
    usuarios_lista,
    usuarios_crear,
    usuarios_editar,
)

app_name = 'accounts'

urlpatterns = [
    path('login/', SGCLoginView.as_view(), name='login'),
    path('logout/', SGCLogoutView.as_view(), name='logout'),
    path('usuarios/', usuarios_lista, name='usuarios_lista'),
    path('usuarios/nuevo/', usuarios_crear, name='usuarios_crear'),
    path('usuarios/<int:pk>/editar/', usuarios_editar, name='usuarios_editar'),
]
