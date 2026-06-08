from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect

from .models import Sector, Clasificacion, Responsable


def _puede_gestionar_sectores(request):
    return request.user.has_perm('core.change_sector')


def _puede_gestionar_clasificaciones(request):
    return request.user.has_perm('core.change_clasificacion')


def _puede_gestionar_responsables(request):
    return request.user.has_perm('core.change_responsable')


@login_required
def sectores_lista(request):
    if not _puede_gestionar_sectores(request):
        messages.error(request, 'Solo el administrador puede gestionar sectores.')
        return redirect('dashboard:index')
    sectores = Sector.objects.all()
    return render(request, 'core/sectores/lista.html', {'sectores': sectores})


@login_required
def sector_crear(request):
    if not _puede_gestionar_sectores(request):
        messages.error(request, 'Solo el administrador puede gestionar sectores.')
        return redirect('core:sectores_lista')
    if request.method == 'POST':
        nombre = request.POST.get('nombre', '').strip()
        if nombre:
            if Sector.objects.filter(nombre__iexact=nombre).exists():
                messages.error(request, f'Ya existe un sector con el nombre "{nombre}".')
            else:
                Sector.objects.create(nombre=nombre)
                messages.success(request, f'Sector "{nombre}" creado.')
                return redirect('core:sectores_lista')
        else:
            messages.error(request, 'El nombre es obligatorio.')
    return render(request, 'core/sectores/form.html', {'titulo': 'Nuevo Sector', 'accion': 'Crear'})


@login_required
def sector_editar(request, pk):
    if not _puede_gestionar_sectores(request):
        messages.error(request, 'Solo el administrador puede gestionar sectores.')
        return redirect('core:sectores_lista')
    sector = get_object_or_404(Sector, pk=pk)
    if request.method == 'POST':
        nombre = request.POST.get('nombre', '').strip()
        activo = request.POST.get('activo') == 'on'
        if nombre:
            if Sector.objects.filter(nombre__iexact=nombre).exclude(pk=pk).exists():
                messages.error(request, f'Ya existe otro sector con el nombre "{nombre}".')
            else:
                sector.nombre = nombre
                sector.activo = activo
                sector.save()
                messages.success(request, f'Sector "{nombre}" actualizado.')
                return redirect('core:sectores_lista')
        else:
            messages.error(request, 'El nombre es obligatorio.')
    return render(request, 'core/sectores/form.html', {
        'titulo': f'Editar Sector: {sector.nombre}',
        'accion': 'Guardar cambios',
        'sector': sector,
    })


@login_required
def sector_eliminar(request, pk):
    if not _puede_gestionar_sectores(request):
        messages.error(request, 'Solo el administrador puede gestionar sectores.')
        return redirect('core:sectores_lista')
    sector = get_object_or_404(Sector, pk=pk)
    if request.method == 'POST':
        nombre = sector.nombre
        sector.delete()
        messages.success(request, f'Sector "{nombre}" eliminado.')
        return redirect('core:sectores_lista')
    return render(request, 'core/sectores/confirmar_eliminar.html', {'sector': sector})


@login_required
def clasificaciones_lista(request):
    if not _puede_gestionar_clasificaciones(request):
        messages.error(request, 'Solo el administrador puede gestionar clasificaciones.')
        return redirect('dashboard:index')
    clasificaciones = Clasificacion.objects.all()
    return render(request, 'core/clasificaciones/lista.html', {'clasificaciones': clasificaciones})


@login_required
def clasificacion_crear(request):
    if not _puede_gestionar_clasificaciones(request):
        messages.error(request, 'Solo el administrador puede gestionar clasificaciones.')
        return redirect('core:clasificaciones_lista')
    if request.method == 'POST':
        nombre = request.POST.get('nombre', '').strip()
        if nombre:
            if Clasificacion.objects.filter(nombre__iexact=nombre).exists():
                messages.error(request, f'Ya existe una clasificación con el nombre "{nombre}".')
            else:
                Clasificacion.objects.create(nombre=nombre)
                messages.success(request, f'Clasificación "{nombre}" creada.')
                return redirect('core:clasificaciones_lista')
        else:
            messages.error(request, 'El nombre es obligatorio.')
    return render(request, 'core/clasificaciones/form.html', {'titulo': 'Nueva Clasificación', 'accion': 'Crear'})


@login_required
def clasificacion_editar(request, pk):
    if not _puede_gestionar_clasificaciones(request):
        messages.error(request, 'Solo el administrador puede gestionar clasificaciones.')
        return redirect('core:clasificaciones_lista')
    clasificacion = get_object_or_404(Clasificacion, pk=pk)
    if request.method == 'POST':
        nombre = request.POST.get('nombre', '').strip()
        activo = request.POST.get('activo') == 'on'
        if nombre:
            if Clasificacion.objects.filter(nombre__iexact=nombre).exclude(pk=pk).exists():
                messages.error(request, f'Ya existe otra clasificación con el nombre "{nombre}".')
            else:
                clasificacion.nombre = nombre
                clasificacion.activo = activo
                clasificacion.save()
                messages.success(request, f'Clasificación "{nombre}" actualizada.')
                return redirect('core:clasificaciones_lista')
        else:
            messages.error(request, 'El nombre es obligatorio.')
    return render(request, 'core/clasificaciones/form.html', {
        'titulo': f'Editar Clasificación: {clasificacion.nombre}',
        'accion': 'Guardar cambios',
        'clasificacion': clasificacion,
    })


@login_required
def clasificacion_eliminar(request, pk):
    if not _puede_gestionar_clasificaciones(request):
        messages.error(request, 'Solo el administrador puede gestionar clasificaciones.')
        return redirect('core:clasificaciones_lista')
    clasificacion = get_object_or_404(Clasificacion, pk=pk)
    if request.method == 'POST':
        nombre = clasificacion.nombre
        clasificacion.delete()
        messages.success(request, f'Clasificación "{nombre}" eliminada.')
        return redirect('core:clasificaciones_lista')
    return render(request, 'core/clasificaciones/confirmar_eliminar.html', {'clasificacion': clasificacion})


@login_required
def responsables_lista(request):
    if not _puede_gestionar_responsables(request):
        messages.error(request, 'Solo el administrador puede gestionar responsables.')
        return redirect('dashboard:index')
    responsables = Responsable.objects.select_related('usuario').all()
    return render(request, 'core/responsables/lista.html', {'responsables': responsables})


@login_required
def responsable_crear(request):
    if not _puede_gestionar_responsables(request):
        messages.error(request, 'Solo el administrador puede gestionar responsables.')
        return redirect('core:responsables_lista')
    if request.method == 'POST':
        nombre = request.POST.get('nombre', '').strip()
        email = request.POST.get('email', '').strip()
        if nombre:
            if Responsable.objects.filter(nombre__iexact=nombre).exists():
                messages.error(request, f'Ya existe un responsable con el nombre "{nombre}".')
            else:
                Responsable.objects.create(nombre=nombre, email=email)
                messages.success(request, f'Responsable "{nombre}" creado.')
                return redirect('core:responsables_lista')
        else:
            messages.error(request, 'El nombre es obligatorio.')
    return render(request, 'core/responsables/form.html', {'titulo': 'Nuevo Responsable', 'accion': 'Crear'})


@login_required
def responsable_editar(request, pk):
    if not _puede_gestionar_responsables(request):
        messages.error(request, 'Solo el administrador puede gestionar responsables.')
        return redirect('core:responsables_lista')
    responsable = get_object_or_404(Responsable, pk=pk)
    if request.method == 'POST':
        nombre = request.POST.get('nombre', '').strip()
        email = request.POST.get('email', '').strip()
        activo = request.POST.get('activo') == 'on'
        if nombre:
            if Responsable.objects.filter(nombre__iexact=nombre).exclude(pk=pk).exists():
                messages.error(request, f'Ya existe otro responsable con el nombre "{nombre}".')
            else:
                responsable.nombre = nombre
                responsable.email = email
                responsable.activo = activo
                responsable.save()
                messages.success(request, f'Responsable "{nombre}" actualizado.')
                return redirect('core:responsables_lista')
        else:
            messages.error(request, 'El nombre es obligatorio.')
    return render(request, 'core/responsables/form.html', {
        'titulo': f'Editar Responsable: {responsable.nombre}',
        'accion': 'Guardar cambios',
        'responsable': responsable,
    })


@login_required
def responsable_eliminar(request, pk):
    if not _puede_gestionar_responsables(request):
        messages.error(request, 'Solo el administrador puede gestionar responsables.')
        return redirect('core:responsables_lista')
    responsable = get_object_or_404(Responsable, pk=pk)
    if request.method == 'POST':
        nombre = responsable.nombre
        responsable.delete()
        messages.success(request, f'Responsable "{nombre}" eliminado.')
        return redirect('core:responsables_lista')
    return render(request, 'core/responsables/confirmar_eliminar.html', {'responsable': responsable})

