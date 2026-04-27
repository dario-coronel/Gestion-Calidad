from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.http import HttpResponse
from django.template.loader import render_to_string

from .models import NoConformidad, CincoPorques, EstadoNC, EficaciaNC
from .forms import NoConformidadForm, CincoPorquesForm, MatrizRiesgoForm, AdjuntoNCForm, EficaciaForm
from apps.core.models import Sector


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
    sector = request.GET.get('sector', '')
    q = request.GET.get('q', '')

    if estado:
        qs = qs.filter(estado=estado)
    if prioridad:
        qs = qs.filter(prioridad=prioridad)
    if sector:
        qs = qs.filter(sector_id=sector)
    if q:
        qs = qs.filter(folio__icontains=q) | qs.filter(descripcion__icontains=q)

    context = {
        'nc_list': qs,
        'colores_estado': COLORES_ESTADO,
        'estados': EstadoNC.choices,
        'prioridades': NoConformidad._meta.get_field('prioridad').choices,
        'sectores': Sector.objects.filter(activo=True).order_by('nombre'),
        'filtros': {'estado': estado, 'prioridad': prioridad, 'sector': sector, 'q': q},
    }

    # Respuesta parcial para HTMX
    if request.htmx:
        return render(request, 'nc/partials/tabla_nc.html', context)

    return render(request, 'nc/lista.html', context)


# ── crear ─────────────────────────────────────────────────────────────────────

@login_required
def crear(request):
    puede_cargar = request.user.has_perm('nc.add_noconformidad')
    if not puede_cargar:
        messages.error(request, 'No tenés permisos para cargar No Conformidades.')
        return redirect('nc:lista')

    if request.method == 'POST':
        form = NoConformidadForm(request.POST)
        adjunto_form = AdjuntoNCForm(request.POST, request.FILES)
        if form.is_valid():
            nc = form.save(commit=False)
            # Lo cargado por operario entra al circuito de revisión de Calidad.
            if not request.user.has_perm('nc.change_noconformidad'):
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
    # Auto-crear 5 Porqués si no existe (NCs importadas, seed, migradas, etc.)
    if cinco_p is None and request.user.has_perm('nc.change_noconformidad'):
        cinco_p = CincoPorques.objects.create(nc=nc, etapa_1=nc.descripcion)
    cinco_form = None
    matriz_form = None
    puede_calidad = request.user.has_perm('nc.change_noconformidad')
    puede_editar = (
        puede_calidad
        or (request.user.has_perm('nc.add_noconformidad') and nc.responsable_id == request.user.id and nc.estado == EstadoNC.BORRADOR)
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

        # Evaluar eficacia de la acción correctiva (solo calidad/admin)
        elif accion == 'marcar_eficacia' and puede_calidad:
            eficacia_form = EficaciaForm(request.POST, instance=nc)
            if eficacia_form.is_valid():
                nc_guardada = eficacia_form.save(commit=False)
                nueva_eficacia = nc_guardada.eficacia

                if nueva_eficacia == EficaciaNC.NO_EFICAZ:
                    # Cerrar NC actual y abrir una nueva vinculada
                    nc_guardada.estado = EstadoNC.CERRADA
                    nc_guardada.actualizado_por = request.user
                    nc_guardada.save()
                    nueva_nc = NoConformidad.objects.create(
                        fecha=timezone.now().date(),
                        sector=nc.sector,
                        responsable=nc.responsable,
                        descripcion=f'Seguimiento de {nc.folio} (No Eficaz): {nc.descripcion}',
                        prioridad=nc.prioridad,
                        clasificacion=nc.clasificacion,
                        origen=nc.origen,
                        qr_relacionada=nc.qr_relacionada,
                        om_relacionada=nc.om_relacionada,
                        nc_origen=nc,
                        estado=EstadoNC.BORRADOR,
                        creado_por=request.user,
                        actualizado_por=request.user,
                    )
                    CincoPorques.objects.create(nc=nueva_nc, etapa_1=nueva_nc.descripcion)
                    messages.warning(
                        request,
                        f'NC marcada como No Eficaz. Se generó la nueva NC {nueva_nc.folio} para seguimiento.'
                    )
                    return redirect('nc:detalle', pk=nueva_nc.pk)
                else:
                    nc_guardada.actualizado_por = request.user
                    nc_guardada.save()
                    messages.success(request, f'Eficacia actualizada: {nc_guardada.get_eficacia_display()}')
                    return redirect('nc:detalle', pk=pk)

    # Solo mostrar form editable a calidad/admin
    eficacia_form = None
    if puede_calidad:
        if not cinco_form and cinco_p:
            cinco_form = CincoPorquesForm(instance=cinco_p)
        if not matriz_form:
            matriz_form = MatrizRiesgoForm(instance=nc)
        eficacia_form = EficaciaForm(instance=nc)

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
        'eficacia_form': eficacia_form,
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
        request.user.has_perm('nc.change_noconformidad')
        or (request.user.has_perm('nc.add_noconformidad') and nc.responsable_id == request.user.id and nc.estado == EstadoNC.BORRADOR)
    )
    if not puede_editar:
        messages.error(request, 'No tenés permisos para editar esta NC.')
        return redirect('nc:detalle', pk=pk)

    if request.method == 'POST':
        form = NoConformidadForm(request.POST, instance=nc)
        if form.is_valid():
            nc = form.save(commit=False)
            # Si el operario corrige una NC devuelta, vuelve a revisión.
            if not request.user.has_perm('nc.change_noconformidad'):
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


# ── PDF ───────────────────────────────────────────────────────────────────────

@login_required
def pdf_resumen(request, pk):
    """Exporta un resumen en PDF de una sola página (datos clave)."""
    nc = get_object_or_404(NoConformidad, pk=pk, eliminado=False)
    try:
        from weasyprint import HTML as WP_HTML
        html_string = render_to_string('nc/pdf_resumen.html', {
            'nc': nc,
            'color_riesgo': _color_riesgo(nc.riesgo_calculado),
        }, request=request)
        pdf_bytes = WP_HTML(string=html_string, base_url=request.build_absolute_uri('/')).write_pdf()
        response = HttpResponse(pdf_bytes, content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="{nc.folio}_resumen.pdf"'
        return response
    except Exception as exc:
        messages.error(request, f'Error al generar PDF: {exc}')
        return redirect('nc:detalle', pk=pk)


@login_required
def pdf_completo(request, pk):
    """Exporta el registro completo de la NC en PDF (todos los campos + 5 Porqués)."""
    nc = get_object_or_404(NoConformidad, pk=pk, eliminado=False)
    cinco_p = getattr(nc, 'cinco_porques', None)
    try:
        from weasyprint import HTML as WP_HTML
        html_string = render_to_string('nc/pdf_completo.html', {
            'nc': nc,
            'cinco_p': cinco_p,
            'color_riesgo': _color_riesgo(nc.riesgo_calculado),
        }, request=request)
        pdf_bytes = WP_HTML(string=html_string, base_url=request.build_absolute_uri('/')).write_pdf()
        response = HttpResponse(pdf_bytes, content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="{nc.folio}_completo.pdf"'
        return response
    except Exception as exc:
        messages.error(request, f'Error al generar PDF: {exc}')
        return redirect('nc:detalle', pk=pk)

