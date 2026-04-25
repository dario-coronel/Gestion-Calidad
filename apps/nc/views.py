from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone

from .models import NoConformidad, CincoPorques, EstadoNC
from .forms import NoConformidadForm, CincoPorquesForm, MatrizRiesgoForm, AdjuntoNCForm


# ── helpers ──────────────────────────────────────────────────────────────────

COLORES_ESTADO = {
    EstadoNC.BORRADOR:          'bg-gray-100 text-gray-700',
    EstadoNC.EN_REVISION:       'bg-warning/10 text-warning',
    EstadoNC.APROBADA:          'bg-primary/10 text-primary',
    EstadoNC.EN_IMPLEMENTACION: 'bg-blue-50 text-blue-700',
    EstadoNC.CERRADA:           'bg-success/10 text-success',
    EstadoNC.RECHAZADA:         'bg-danger/10 text-danger',
}


def _color_riesgo(valor):
    if not valor:
        return ''
    if valor >= 15:
        return 'text-danger font-bold'
    if valor >= 8:
        return 'text-warning font-semibold'
    return 'text-success'


# ── lista ─────────────────────────────────────────────────────────────────────

@login_required
def lista(request):
    qs = NoConformidad.objects.filter(eliminado=False).select_related('responsable')

    # Filtros
    estado = request.GET.get('estado', '')
    prioridad = request.GET.get('prioridad', '')
    area = request.GET.get('area', '')
    q = request.GET.get('q', '')

    if estado:
        qs = qs.filter(estado=estado)
    if prioridad:
        qs = qs.filter(prioridad=prioridad)
    if area:
        qs = qs.filter(area__icontains=area)
    if q:
        qs = qs.filter(folio__icontains=q) | qs.filter(descripcion__icontains=q)

    context = {
        'nc_list': qs,
        'colores_estado': COLORES_ESTADO,
        'estados': EstadoNC.choices,
        'prioridades': NoConformidad._meta.get_field('prioridad').choices,
        'filtros': {'estado': estado, 'prioridad': prioridad, 'area': area, 'q': q},
    }

    # Respuesta parcial para HTMX
    if request.htmx:
        return render(request, 'nc/partials/tabla_nc.html', context)

    return render(request, 'nc/lista.html', context)


# ── crear ─────────────────────────────────────────────────────────────────────

@login_required
def crear(request):
    puede_cargar = request.user.es_operario or request.user.es_calidad or request.user.is_superuser
    if not puede_cargar:
        messages.error(request, 'No tenés permisos para cargar No Conformidades.')
        return redirect('nc:lista')

    if request.method == 'POST':
        form = NoConformidadForm(request.POST)
        adjunto_form = AdjuntoNCForm(request.POST, request.FILES)
        if form.is_valid():
            nc = form.save(commit=False)
            # Lo cargado por operario entra al circuito de revisión de Calidad.
            if request.user.es_operario:
                nc.estado = EstadoNC.EN_REVISION
            nc.creado_por = request.user
            nc.actualizado_por = request.user
            nc.save()
            # Crear 5 Porqués asociados con etapa 1 pre-cargada
            CincoPorques.objects.create(nc=nc, etapa_1=nc.descripcion)
            # Adjunto opcional
            if adjunto_form.is_valid() and request.FILES.get('archivo'):
                adj = adjunto_form.save(commit=False)
                adj.nc = nc
                adj.nombre = request.FILES['archivo'].name
                adj.subido_por = request.user
                adj.save()
            messages.success(request, f'No Conformidad {nc.folio} creada correctamente.')
            return redirect('nc:detalle', pk=nc.pk)
    else:
        form = NoConformidadForm(initial={'fecha': timezone.now().date()})
        adjunto_form = AdjuntoNCForm()

    return render(request, 'nc/form.html', {
        'form': form,
        'adjunto_form': adjunto_form,
        'titulo': 'Nueva No Conformidad',
        'accion': 'Registrar NC',
    })


# ── detalle ───────────────────────────────────────────────────────────────────

@login_required
def detalle(request, pk):
    nc = get_object_or_404(NoConformidad, pk=pk, eliminado=False)
    cinco_p = getattr(nc, 'cinco_porques', None)
    cinco_form = None
    matriz_form = None
    puede_calidad = request.user.es_calidad or request.user.is_superuser
    puede_editar = (
        puede_calidad
        or (request.user.es_operario and nc.responsable_id == request.user.id and nc.estado == EstadoNC.BORRADOR)
    )

    if request.method == 'POST':
        accion = request.POST.get('accion', '')

        # Guardar 5 Porqués (solo calidad/admin)
        if accion == 'guardar_5p' and cinco_p and puede_calidad:
            cinco_form = CincoPorquesForm(request.POST, instance=cinco_p)
            if cinco_form.is_valid():
                cp = cinco_form.save(commit=False)
                cp.completo = bool(cp.causa_raiz and cp.accion_correctiva)
                cp.save()
                nc.actualizado_por = request.user
                nc.save(update_fields=['actualizado_por', 'actualizado_en'])
                messages.success(request, 'Análisis 5 Porqués guardado.')
                return redirect('nc:detalle', pk=pk)

        # Guardar Matriz de Riesgo (solo calidad/admin)
        elif accion == 'guardar_riesgo' and puede_calidad:
            matriz_form = MatrizRiesgoForm(request.POST, instance=nc)
            if matriz_form.is_valid():
                matriz_form.save()
                messages.success(request, 'Matriz de riesgo actualizada.')
                return redirect('nc:detalle', pk=pk)

        # Cambio de estado (solo calidad/admin)
        elif accion == 'cambiar_estado' and puede_calidad:
            nuevo_estado = request.POST.get('nuevo_estado')
            if nuevo_estado in dict(EstadoNC.choices):
                nc.estado = nuevo_estado
                nc.actualizado_por = request.user
                nc.save(update_fields=['estado', 'actualizado_por', 'actualizado_en'])
                messages.success(request, f'Estado actualizado a: {nc.get_estado_display()}')
                return redirect('nc:detalle', pk=pk)

        # Flujo de revisión de calidad: aprobar / rechazar / reenviar al operario
        elif accion == 'revision_calidad' and puede_calidad:
            decision = request.POST.get('decision')
            if decision == 'aprobar':
                nc.estado = EstadoNC.APROBADA
                msg = 'NC aprobada por Calidad.'
            elif decision == 'rechazar':
                nc.estado = EstadoNC.RECHAZADA
                msg = 'NC rechazada por Calidad.'
            elif decision == 'reenviar':
                nc.estado = EstadoNC.BORRADOR
                msg = 'NC reenviada al operario para completar datos.'
            else:
                msg = ''

            if msg:
                nc.actualizado_por = request.user
                nc.save(update_fields=['estado', 'actualizado_por', 'actualizado_en'])
                messages.success(request, msg)
                return redirect('nc:detalle', pk=pk)

    # Solo mostrar form editable a calidad/admin
    if puede_calidad:
        if not cinco_form and cinco_p:
            cinco_form = CincoPorquesForm(instance=cinco_p)
        if not matriz_form:
            matriz_form = MatrizRiesgoForm(instance=nc)

    etapas = [
        ('etapa_1', '¿Por qué? (1º nivel)'),
        ('etapa_2', '¿Por qué? (2º nivel)'),
        ('etapa_3', '¿Por qué? (3º nivel)'),
        ('etapa_4', '¿Por qué? (4º nivel)'),
        ('etapa_5', '¿Por qué? (5º nivel)'),
    ]

    return render(request, 'nc/detalle.html', {
        'nc': nc,
        'cinco_form': cinco_form,
        'matriz_form': matriz_form,
        'cinco_p': cinco_p,
        'etapas': etapas,
        'color_estado': COLORES_ESTADO.get(nc.estado, ''),
        'color_riesgo': _color_riesgo(nc.riesgo_calculado),
        'estados': EstadoNC.choices,
        'puede_calidad': puede_calidad,
        'puede_editar_riesgo': puede_calidad,
        'puede_cambiar_estado': puede_calidad,
        'puede_editar': puede_editar,
    })


# ── editar ────────────────────────────────────────────────────────────────────

@login_required
def editar(request, pk):
    nc = get_object_or_404(NoConformidad, pk=pk, eliminado=False)
    puede_editar = (
        request.user.es_calidad
        or request.user.is_superuser
        or (request.user.es_operario and nc.responsable_id == request.user.id and nc.estado == EstadoNC.BORRADOR)
    )
    if not puede_editar:
        messages.error(request, 'No tenés permisos para editar esta NC.')
        return redirect('nc:detalle', pk=pk)

    if request.method == 'POST':
        form = NoConformidadForm(request.POST, instance=nc)
        if form.is_valid():
            nc = form.save(commit=False)
            # Si el operario corrige una NC devuelta, vuelve a revisión.
            if request.user.es_operario:
                nc.estado = EstadoNC.EN_REVISION
            nc.actualizado_por = request.user
            nc.save()
            messages.success(request, f'{nc.folio} actualizada.')
            return redirect('nc:detalle', pk=pk)
    else:
        form = NoConformidadForm(instance=nc)

    return render(request, 'nc/form.html', {
        'form': form,
        'adjunto_form': AdjuntoNCForm(),
        'nc': nc,
        'titulo': f'Editar {nc.folio}',
        'accion': 'Guardar cambios',
    })

