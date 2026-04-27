from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect

from .models import Sector


def _puede_gestionar_sectores(request):
    return request.user.has_perm('core.change_sector')


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

