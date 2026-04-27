from django.urls import path
from django.contrib.auth import views as auth_views
from .views import (
    SGCLoginView,
    SGCLogoutView,
    usuarios_lista,
    usuarios_crear,
    usuarios_editar,
    roles_lista,
)

app_name = 'accounts'

urlpatterns = [
    path('login/', SGCLoginView.as_view(), name='login'),
    path('logout/', SGCLogoutView.as_view(), name='logout'),

    # Recuperar contraseña
    path('password-reset/',
         auth_views.PasswordResetView.as_view(
             template_name='accounts/password_reset_form.html',
             email_template_name='accounts/email/password_reset_email.txt',
             html_email_template_name='accounts/email/password_reset_email.html',
             subject_template_name='accounts/email/password_reset_subject.txt',
             success_url='/accounts/password-reset/enviado/',
         ), name='password_reset'),
    path('password-reset/enviado/',
         auth_views.PasswordResetDoneView.as_view(
             template_name='accounts/password_reset_done.html',
         ), name='password_reset_done'),
    path('reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='accounts/password_reset_confirm.html',
             success_url='/accounts/reset/completado/',
         ), name='password_reset_confirm'),
    path('reset/completado/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='accounts/password_reset_complete.html',
         ), name='password_reset_complete'),
    path('usuarios/', usuarios_lista, name='usuarios_lista'),
    path('roles/', roles_lista, name='roles_lista'),
    path('usuarios/nuevo/', usuarios_crear, name='usuarios_crear'),
    path('usuarios/<int:pk>/editar/', usuarios_editar, name='usuarios_editar'),
]
