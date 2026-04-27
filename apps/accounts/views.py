from django.contrib.auth.views import LoginView, LogoutView
from django.contrib import messages
from django.contrib.auth.models import Permission
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import UsuarioCreateForm, UsuarioUpdateForm
from .models import Usuario
from .signals import sincronizar_grupo


NIVELES_ACCION = {
    'none': [],
    'view': ['view'],
    'create': ['view', 'add'],
    'manage': ['view', 'add', 'change', 'delete'],
}

MODULOS_PERMISOS = [
    {
        'key': 'nc',
        'label': 'No Conformidades',
        'app_label': 'nc',
        'models': ['noconformidad'],
        'menu_perm': 'nc.view_noconformidad',
    },
    {
        'key': 'qr',
        'label': 'Quejas y Reclamos',
        'app_label': 'qr',
        'models': ['quejareclamo'],
        'menu_perm': 'qr.view_quejareclamo',
    },
    {
        'key': 'om',
        'label': 'Oportunidades de Mejora',
        'app_label': 'om',
        'models': ['oportunidadmejora'],
        'menu_perm': 'om.view_oportunidadmejora',
    },
    {
        'key': 'proyectos',
        'label': 'Proyectos',
        'app_label': 'proyectos',
        'models': ['proyecto', 'subtarea'],
        'menu_perm': 'proyectos.view_proyecto',
    },
    {
        'key': 'verificacion',
        'label': 'Verificación de Eficacia',
        'app_label': 'verificacion',
        'models': ['verificacioneficacia'],
        'menu_perm': 'verificacion.view_verificacioneficacia',
    },
]


def _nivel_usuario_modulo(user, modulo):
    app = modulo['app_label']
    modelos = modulo['models']

    def _tiene_todas(accion):
        return all(user.has_perm(f'{app}.{accion}_{m}') for m in modelos)

    if _tiene_todas('delete') and _tiene_todas('change') and _tiene_todas('add') and _tiene_todas('view'):
        return 'manage'
    if _tiene_todas('add') and _tiene_todas('view'):
        return 'create'
    if _tiene_todas('view'):
        return 'view'
    return 'none'


class SGCLoginView(LoginView):
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True

    def form_valid(self, form):
        # Mantiene rol y grupo alineados incluso si no se ejecutó seed_grupos.
        sincronizar_grupo(form.get_user())
        return super().form_valid(form)


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


@login_required
def roles_lista(request):
    if not _es_admin_sistema(request.user):
        messages.error(request, 'Solo un administrador puede gestionar roles y permisos.')
        return redirect('dashboard:index')

    usuarios = Usuario.objects.order_by('username')
    user_id = request.GET.get('user') or request.POST.get('user_id')
    usuario_obj = None

    if user_id:
        usuario_obj = get_object_or_404(Usuario, pk=user_id)

    if request.method == 'POST' and usuario_obj:
        managed_qs = Permission.objects.none()
        selected_qs = Permission.objects.none()

        for modulo in MODULOS_PERMISOS:
            nivel = request.POST.get(f"perm_{modulo['key']}", 'none')
            acciones = NIVELES_ACCION.get(nivel, [])
            managed_codes = []

            for model_name in modulo['models']:
                for accion in ['add', 'change', 'delete', 'view']:
                    managed_codes.append(f'{accion}_{model_name}')

            module_qs = Permission.objects.filter(
                content_type__app_label=modulo['app_label'],
                codename__in=managed_codes,
            )
            managed_qs = managed_qs | module_qs

            for accion in acciones:
                for model_name in modulo['models']:
                    codename = f'{accion}_{model_name}'
                    selected_qs = selected_qs | Permission.objects.filter(
                        content_type__app_label=modulo['app_label'],
                        codename=codename,
                    )

        usuario_obj.user_permissions.remove(*managed_qs.distinct())
        usuario_obj.user_permissions.add(*selected_qs.distinct())

        messages.success(request, f'Permisos actualizados para {usuario_obj.username}.')
        return redirect(f"{request.path}?user={usuario_obj.pk}")

    modulos_ui = []
    for modulo in MODULOS_PERMISOS:
        nivel_actual = _nivel_usuario_modulo(usuario_obj, modulo) if usuario_obj else 'none'
        modulos_ui.append({**modulo, 'nivel_actual': nivel_actual})

    return render(request, 'accounts/roles_lista.html', {
        'usuarios': usuarios,
        'usuario_obj': usuario_obj,
        'modulos': modulos_ui,
    })

