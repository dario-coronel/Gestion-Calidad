from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.db.models import Count, Avg, F, IntegerField, ExpressionWrapper
import json

from apps.nc.models import NoConformidad, EstadoNC
from apps.proyectos.models import Proyecto, EstadoProyecto


@login_required
def index(request):
    nc_qs = NoConformidad.objects.filter(eliminado=False)
    proyectos_qs = Proyecto.objects.filter(eliminado=False)

    riesgo_expr = ExpressionWrapper(F('probabilidad') * F('impacto'), output_field=IntegerField())
    riesgo_promedio = nc_qs.exclude(probabilidad__isnull=True).exclude(impacto__isnull=True).annotate(
        riesgo=riesgo_expr
    ).aggregate(promedio=Avg('riesgo'))['promedio']

    estado_counts = nc_qs.values('estado').annotate(total=Count('id'))
    estado_map = {item['estado']: item['total'] for item in estado_counts}
    estado_labels = [label for _, label in EstadoNC.choices]
    estado_data = [estado_map.get(value, 0) for value, _ in EstadoNC.choices]

    proyecto_counts = proyectos_qs.values('estado').annotate(total=Count('id'))
    proyecto_map = {item['estado']: item['total'] for item in proyecto_counts}
    proyecto_labels = [label for _, label in EstadoProyecto.choices]
    proyecto_data = [proyecto_map.get(value, 0) for value, _ in EstadoProyecto.choices]

    abiertas = nc_qs.exclude(estado__in=[EstadoNC.CERRADA, EstadoNC.RECHAZADA]).count()
    criticas = nc_qs.filter(prioridad='critica').count()
    proyectos_activos = proyectos_qs.exclude(estado=EstadoProyecto.FINALIZADO).count()

    # ── Matriz de riesgo 5×5 ──────────────────────────────────────
    _matrix = {}
    for nc in nc_qs.filter(probabilidad__isnull=False, impacto__isnull=False).only(
            'pk', 'folio', 'area', 'probabilidad', 'impacto'):
        _matrix.setdefault((nc.probabilidad, nc.impacto), []).append(
            {'folio': nc.folio, 'pk': nc.pk, 'area': nc.area}
        )

    def _nivel(r):
        if r <= 4:  return 'bajo'
        if r <= 9:  return 'medio'
        if r <= 14: return 'alto'
        return 'critico'

    matrix_rows = []
    for prob in range(5, 0, -1):          # filas: prob 5 → 1 (arriba = mayor)
        cells = []
        for imp in range(1, 6):           # cols: impacto 1 → 5 (derecha = mayor)
            r = prob * imp
            ncs = _matrix.get((prob, imp), [])
            cells.append({'prob': prob, 'imp': imp, 'riesgo': r,
                          'nivel': _nivel(r), 'ncs': ncs, 'count': len(ncs)})
        matrix_rows.append({'prob': prob, 'cells': cells})
    # ─────────────────────────────────────────────────────────────

    context = {
        'kpi_total_nc': nc_qs.count(),
        'kpi_nc_abiertas': abiertas,
        'kpi_nc_criticas': criticas,
        'kpi_riesgo_promedio': round(riesgo_promedio or 0, 1),
        'kpi_proyectos_activos': proyectos_activos,
        'kpi_proyectos_finalizados': proyectos_qs.filter(estado=EstadoProyecto.FINALIZADO).count(),
        'estado_labels_json': json.dumps(estado_labels),
        'estado_data_json': json.dumps(estado_data),
        'proyecto_labels_json': json.dumps(proyecto_labels),
        'proyecto_data_json': json.dumps(proyecto_data),
        'ultimas_nc': nc_qs.select_related('responsable').order_by('-fecha')[:6],
        'ultimos_proyectos': proyectos_qs.select_related('responsable').order_by('-fecha_inicio')[:6],
        'matrix_rows': matrix_rows,
        'impacto_labels': ['Muy bajo', 'Bajo', 'Moderado', 'Alto', 'Muy alto'],
    }
    return render(request, 'dashboard/index.html', context)