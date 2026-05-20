from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.db.models import Count, Avg, F, IntegerField, ExpressionWrapper
from django.db.models.functions import TruncMonth
from datetime import timedelta
from django.utils import timezone
import json

from apps.nc.models import NoConformidad, EstadoNC
from apps.qr.models import QuejaReclamo, EstadoQR
from apps.proyectos.models import Proyecto, EstadoProyecto


@login_required
def index(request):
    nc_qs = NoConformidad.objects.filter(eliminado=False)
    qr_qs = QuejaReclamo.objects.filter(eliminado=False)
    proyectos_qs = Proyecto.objects.filter(eliminado=False)

    period = request.GET.get('period', '90d')
    hoy = timezone.localdate()
    period_options = {
        '30d': hoy - timedelta(days=30),
        '90d': hoy - timedelta(days=90),
        '12m': hoy - timedelta(days=365),
        'all': None,
    }
    qr_period_start = period_options.get(period, period_options['90d'])
    qr_period_qs = qr_qs if qr_period_start is None else qr_qs.filter(fecha__gte=qr_period_start)
    qr_period_label = {
        '30d': 'Últimos 30 días',
        '90d': 'Últimos 90 días',
        '12m': 'Últimos 12 meses',
        'all': 'Todo el historial',
    }.get(period, 'Últimos 90 días')

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

    qr_estado_counts = qr_period_qs.values('estado').annotate(total=Count('id'))
    qr_estado_map = {item['estado']: item['total'] for item in qr_estado_counts}
    qr_estado_labels = [label for _, label in EstadoQR.choices]
    qr_estado_data = [qr_estado_map.get(value, 0) for value, _ in EstadoQR.choices]

    qr_trend_qs = qr_period_qs
    qr_trend_data = {}
    for item in qr_trend_qs.annotate(month=TruncMonth('fecha')).values('month').annotate(total=Count('id')).order_by('month'):
        month_value = item['month']
        if hasattr(month_value, 'date'):
            month_value = month_value.date()
        qr_trend_data[month_value] = item['total']
    qr_trend_labels = []
    qr_trend_values = []
    trend_start = hoy.replace(day=1)
    if qr_period_start:
        trend_start = max(qr_period_start.replace(day=1), trend_start - timedelta(days=365))
    months = []
    cursor = trend_start
    while cursor <= hoy:
        months.append(cursor)
        year = cursor.year + (cursor.month // 12)
        month = (cursor.month % 12) + 1
        cursor = cursor.replace(year=year, month=month, day=1)
        if len(months) >= 12:
            break
    if not months:
        months = [hoy.replace(day=1)]
    for month in months:
        qr_trend_labels.append(month.strftime('%b %Y'))
        qr_trend_values.append(qr_trend_data.get(month, 0))

    abiertas = nc_qs.exclude(estado__in=[EstadoNC.CERRADA, EstadoNC.RECHAZADA]).count()
    criticas = nc_qs.filter(prioridad='critica').count()
    proyectos_activos = proyectos_qs.exclude(estado=EstadoProyecto.FINALIZADO).count()
    qr_abiertas = qr_period_qs.exclude(estado__in=[EstadoQR.CERRADO, EstadoQR.RECHAZADO]).count()
    qr_dias_promedio = qr_period_qs.exclude(dias_resolucion__isnull=True).aggregate(
        promedio=Avg('dias_resolucion')
    )['promedio']

    qr_vencidas = 0
    qr_qs_para_vencimiento = qr_period_qs.exclude(estado__in=[EstadoQR.CERRADO, EstadoQR.RECHAZADO]).exclude(
        dias_resolucion__isnull=True
    ).only('fecha', 'dias_resolucion')
    for qr in qr_qs_para_vencimiento:
        if qr.fecha and qr.dias_resolucion and (qr.fecha + timedelta(days=qr.dias_resolucion)) < hoy:
            qr_vencidas += 1

    # ── Matriz de riesgo 5×5 ──────────────────────────────────────
    _matrix = {}
    for nc in nc_qs.filter(probabilidad__isnull=False, impacto__isnull=False).select_related('sector').only(
            'pk', 'folio', 'sector__nombre', 'probabilidad', 'impacto'):
        _matrix.setdefault((nc.probabilidad, nc.impacto), []).append(
            {'folio': nc.folio, 'pk': nc.pk, 'sector': nc.sector.nombre if nc.sector else '—'}
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
        'kpi_total_qr': qr_period_qs.count(),
        'kpi_qr_abiertas': qr_abiertas,
        'kpi_qr_vencidas': qr_vencidas,
        'kpi_qr_dias_promedio': round(qr_dias_promedio or 0, 1),
        'kpi_qr_alerta_vencidas': qr_vencidas > 0,
        'qr_period': period,
        'qr_period_label': qr_period_label,
        'kpi_proyectos_activos': proyectos_activos,
        'kpi_proyectos_finalizados': proyectos_qs.filter(estado=EstadoProyecto.FINALIZADO).count(),
        'estado_labels_json': json.dumps(estado_labels),
        'estado_data_json': json.dumps(estado_data),
        'qr_estado_labels_json': json.dumps(qr_estado_labels),
        'qr_estado_data_json': json.dumps(qr_estado_data),
        'qr_trend_labels_json': json.dumps(qr_trend_labels),
        'qr_trend_values_json': json.dumps(qr_trend_values),
        'proyecto_labels_json': json.dumps(proyecto_labels),
        'proyecto_data_json': json.dumps(proyecto_data),
        'ultimas_nc': nc_qs.select_related('responsable').order_by('-fecha')[:6],
        'ultimas_qr': qr_period_qs.select_related('responsable').order_by('-fecha')[:6],
        'ultimos_proyectos': proyectos_qs.select_related('responsable').order_by('-fecha_inicio')[:6],
        'matrix_rows': matrix_rows,
        'impacto_labels': ['Muy bajo', 'Bajo', 'Moderado', 'Alto', 'Muy alto'],
    }
    return render(request, 'dashboard/index.html', context)