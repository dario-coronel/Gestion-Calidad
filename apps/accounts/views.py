from django.contrib.auth.views import LoginView, LogoutView
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import UsuarioCreateForm, UsuarioUpdateForm
from .models import Usuario


class SGCLoginView(LoginView):
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True


class SGCLogoutView(LogoutView):
    next_page = '/'


def _es_admin_sistema(user):
    return user.is_authenticated and (getattr(user, 'es_admin', False) or user.is_superuser)


@login_required
def usuarios_lista(request):
    if not _es_admin_sistema(request.user):
        messages.error(request, 'Solo un administrador puede gestionar usuarios.')
        return redirect('dashboard:index')

    usuarios = Usuario.objects.order_by('username')
    return render(request, 'accounts/usuarios_lista.html', {'usuarios': usuarios})


@login_required
def usuarios_crear(request):
    if not _es_admin_sistema(request.user):
        messages.error(request, 'Solo un administrador puede crear usuarios.')
        return redirect('dashboard:index')

    if request.method == 'POST':
        form = UsuarioCreateForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'Usuario {user.username} creado correctamente.')
            return redirect('accounts:usuarios_lista')
    else:
        form = UsuarioCreateForm(initial={'is_active': True})

    return render(request, 'accounts/usuarios_form.html', {
        'form': form,
        'titulo': 'Nuevo Usuario',
        'accion': 'Crear usuario',
    })


@login_required
def usuarios_editar(request, pk):
    if not _es_admin_sistema(request.user):
        messages.error(request, 'Solo un administrador puede editar usuarios.')
        return redirect('dashboard:index')

    usuario = get_object_or_404(Usuario, pk=pk)

    if request.method == 'POST':
        accion = request.POST.get('accion')
        if accion == 'toggle_activo':
            if usuario.pk == request.user.pk:
                messages.error(request, 'No podés desactivarte a vos mismo.')
                return redirect('accounts:usuarios_lista')
            usuario.is_active = not usuario.is_active
            usuario.save(update_fields=['is_active'])
            estado = 'activado' if usuario.is_active else 'desactivado'
            messages.success(request, f'Usuario {usuario.username} {estado}.')
            return redirect('accounts:usuarios_lista')

        form = UsuarioUpdateForm(request.POST, instance=usuario)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'Usuario {user.username} actualizado.')
            return redirect('accounts:usuarios_lista')
    else:
        form = UsuarioUpdateForm(instance=usuario)

    return render(request, 'accounts/usuarios_form.html', {
        'form': form,
        'titulo': f'Editar usuario: {usuario.username}',
        'accion': 'Guardar cambios',
        'usuario_obj': usuario,
    })

