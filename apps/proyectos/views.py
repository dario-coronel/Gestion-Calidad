from datetime import date as date_cls
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone

from .models import Proyecto, EstadoProyecto, Subtarea
from .forms import ProyectoForm, SubtareaForm


COLORES_ESTADO = {
    EstadoProyecto.POR_HACER:  'bg-gray-100 text-gray-700',
    EstadoProyecto.EN_CURSO:   'bg-blue-50 text-blue-700',
    EstadoProyecto.FINALIZADO: 'bg-success/10 text-success',
}

COLORES_PRIORIDAD_GANTT = {
    'alta':  '#ef4444',   # red-500
    'media': '#eab308',   # yellow-500
    'baja':  '#22c55e',   # green-500
}


def _build_gantt(proyectos_list):
    """Devuelve (gantt_items, gantt_header, total_width_px, today_px, show_today) listos para el template."""
    all_dates = []
    for p in proyectos_list:
        if p.fecha_inicio:
            all_dates.append(p.fecha_inicio)
        if p.fecha_fin:
            all_dates.append(p.fecha_fin)

    if not all_dates:
        return [], [], 0, 0, False

    min_d = min(all_dates)
    max_d = max(all_dates)
    total_days = max((max_d - min_d).days, 1)

    # Píxeles por día según rango total → barras proporcionadas a fechas reales
    if total_days <= 30:
        px_per_day = 24
    elif total_days <= 90:
        px_per_day = 14
    elif total_days <= 180:
        px_per_day = 8
    elif total_days <= 365:
        px_per_day = 4
    else:
        px_per_day = 2

    total_width_px = total_days * px_per_day

    items = []
    for p in proyectos_list:
        if not (p.fecha_inicio and p.fecha_fin):
            continue
        offset_px  = (p.fecha_inicio - min_d).days * px_per_day
        width_px   = max(p.dias_ejecucion * px_per_day, 6)
        avance_px  = round(width_px * p.porcentaje_avance / 100)
        items.append({
            'pk':        p.pk,
            'nombre':    f'{p.folio} · {p.nombre[:45]}',
            'offset_px': offset_px,
            'width_px':  width_px,
            'avance_px': avance_px,
            'color':     COLORES_PRIORIDAD_GANTT.get(p.prioridad, '#6b7280'),
            'prioridad': p.get_prioridad_display(),
            'estado':    p.get_estado_display(),
            'avance':    p.porcentaje_avance,
            'inicio':    p.fecha_inicio.strftime('%d/%m/%Y'),
            'fin':       p.fecha_fin.strftime('%d/%m/%Y'),
        })

    # Marcadores de mes en el eje X
    header = []
    cur = date_cls(min_d.year, min_d.month, 1)
    while cur <= max_d:
        header.append({
            'label':     cur.strftime('%b %Y'),
            'offset_px': max((cur - min_d).days * px_per_day, 0),
        })
        cur = date_cls(cur.year + (cur.month // 12), (cur.month % 12) + 1, 1)

    # Línea de "hoy"
    today = date_cls.today()
    show_today = min_d <= today <= max_d
    today_px = (today - min_d).days * px_per_day if show_today else 0

    return items, header, total_width_px, today_px, show_today


@login_required
def lista(request):
    qs = Proyecto.objects.filter(eliminado=False).select_related('responsable', 'sector', 'nc', 'om')

    estado = request.GET.get('estado', '')
    q = request.GET.get('q', '')

    if estado:
        qs = qs.filter(estado=estado)
    if q:
        qs = qs.filter(folio__icontains=q) | qs.filter(nombre__icontains=q)

    proyectos_list = list(qs)
    gantt_items, gantt_header, gantt_total_width, gantt_today_px, gantt_show_today = _build_gantt(proyectos_list)

    return render(request, 'proyectos/lista.html', {
        'proyectos':         proyectos_list,
        'colores_estado':    COLORES_ESTADO,
        'estados':           EstadoProyecto.choices,
        'filtros':           {'estado': estado, 'q': q},
        'gantt_items':       gantt_items,
        'gantt_header':      gantt_header,
        'gantt_total_width': gantt_total_width,
        'gantt_today_px':    gantt_today_px,
        'gantt_show_today':  gantt_show_today,
    })


@login_required
def crear(request):
    puede_gestionar = request.user.has_perm('proyectos.add_proyecto')
    if not puede_gestionar:
        messages.error(request, 'Solo el área de Calidad puede crear proyectos.')
        return redirect('proyectos:lista')

    if request.method == 'POST':
        form = ProyectoForm(request.POST)
        if form.is_valid():
            p = form.save(commit=False)
            p.creado_por = request.user
            p.actualizado_por = request.user
            p.save()
            messages.success(request, f'{p.folio} creado correctamente.')
            return redirect('proyectos:detalle', pk=p.pk)
    else:
        form = ProyectoForm(initial={'fecha_inicio': timezone.now().date()})

    return render(request, 'proyectos/form.html', {
        'form': form,
        'titulo': 'Nuevo Proyecto',
        'accion': 'Crear Proyecto',
    })


@login_required
def detalle(request, pk):
    proyecto = get_object_or_404(Proyecto.objects.select_related('sector', 'nc', 'om', 'verificacion_eficacia'), pk=pk, eliminado=False)
    puede_gestionar = request.user.has_perm('proyectos.change_proyecto')
    subtarea_form = SubtareaForm()

    if request.method == 'POST':
        accion = request.POST.get('accion', '')

        if accion == 'agregar_subtarea' and puede_gestionar:
            subtarea_form = SubtareaForm(request.POST)
            if subtarea_form.is_valid():
                st = subtarea_form.save(commit=False)
                st.proyecto = proyecto
                st.orden = proyecto.subtareas.count() + 1
                st.save()
                messages.success(request, 'Tarea agregada.')
                return redirect('proyectos:detalle', pk=pk)

        elif accion == 'toggle_subtarea':
            if not request.user.has_perm('proyectos.change_subtarea'):
                messages.error(request, 'No tenés permisos para modificar tareas.')
                return redirect('proyectos:detalle', pk=pk)
            st_id = request.POST.get('subtarea_id')
            try:
                st = proyecto.subtareas.get(pk=st_id)
                st.completada = not st.completada
                if st.completada:
                    st.completada_en = timezone.now()
                    st.completada_por = request.user
                else:
                    st.completada_en = None
                    st.completada_por = None
                st.save()
            except Subtarea.DoesNotExist:
                pass
            return redirect('proyectos:detalle', pk=pk)

        elif accion == 'cambiar_estado' and puede_gestionar:
            nuevo_estado = request.POST.get('nuevo_estado')
            if nuevo_estado in dict(EstadoProyecto.choices):
                proyecto.estado = nuevo_estado
                proyecto.actualizado_por = request.user
                proyecto.save(update_fields=['estado', 'actualizado_por', 'actualizado_en'])
                messages.success(request, f'Estado actualizado a: {proyecto.get_estado_display()}')
                return redirect('proyectos:detalle', pk=pk)

    return render(request, 'proyectos/detalle.html', {
        'proyecto': proyecto,
        'subtareas_completadas': proyecto.subtareas.filter(completada=True).count(),
        'subtarea_form': subtarea_form,
        'color_estado': COLORES_ESTADO.get(proyecto.estado, ''),
        'estados': EstadoProyecto.choices,
        'puede_gestionar': puede_gestionar,
    })


@login_required
def editar(request, pk):
    proyecto = get_object_or_404(Proyecto, pk=pk, eliminado=False)
    puede_gestionar = request.user.has_perm('proyectos.change_proyecto')
    if not puede_gestionar:
        messages.error(request, 'No tenés permiso para editar este proyecto.')
        return redirect('proyectos:detalle', pk=pk)

    if request.method == 'POST':
        form = ProyectoForm(request.POST, instance=proyecto)
        if form.is_valid():
            p = form.save(commit=False)
            p.actualizado_por = request.user
            p.save()
            messages.success(request, f'{p.folio} actualizado.')
            return redirect('proyectos:detalle', pk=pk)
    else:
        form = ProyectoForm(instance=proyecto)

    return render(request, 'proyectos/form.html', {
        'form': form,
        'titulo': f'Editar {proyecto.folio}',
        'accion': 'Guardar cambios',
        'proyecto': proyecto,
    })

