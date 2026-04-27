"""
Management command: seed_demo
Genera datos de prueba variados para testear el SGC de forma manual.

Uso:
    python manage.py seed_demo          # crea ~50 registros variados
    python manage.py seed_demo --flush  # borra datos existentes primero
"""
import random
from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction

from apps.core.models import Sector
from apps.nc.models import (
    NoConformidad, CincoPorques,
    EstadoNC, PrioridadNC, ClasificacionNC, OrigenNC, EficaciaNC,
)
from apps.qr.models import QuejaReclamo, EstadoQR, TipoReclamo
from apps.om.models import (
    OportunidadMejora, EstadoOM, ClasificacionOM, RangoEvaluacion, EficaciaOM,
)
from apps.proyectos.models import (
    Proyecto, Subtarea, EstadoProyecto, PrioridadProyecto, OrigenProyecto,
)
from apps.verificacion.models import VerificacionEficacia, EstadoVerificacion

Usuario = get_user_model()

# ── Datos de ejemplo ─────────────────────────────────────────────────────────

NOMBRES = ['Ana García', 'Luis Romero', 'Carla Díaz', 'Martín López',
           'Sofía Herrera', 'Pablo Núñez', 'Valentina Torres']

DESCRIPCIONES_NC = [
    'Producto terminado fuera de especificación de humedad.',
    'Lote de materia prima rechazado por proveedor habitual.',
    'Temperatura de almacenamiento excedió el límite permitido.',
    'Etiquetado incorrecto detectado por cliente en destino.',
    'Contaminación de aceite en línea de producción balanceado.',
    'Parámetro de pH fuera de rango en laboratorio.',
    'Error de pesaje en formulación de mezcla.',
    'Ruptura de bolsa durante el embalaje final.',
    'Falla en sellado hermético de envases secundarios.',
    'Desvío en granulometría de producto molido.',
    'Contaminación microbiológica detectada en muestras de planta.',
    'Proceso de limpieza CIP no completado correctamente.',
]

CORRECCIONES_NC = [
    'Se aisló el lote y se notificó a calidad.',
    'Se retiró el producto de la línea y se etiquetó como no conforme.',
    'Se ajustó el parámetro de control y se recalibró el equipo.',
    'Se reprocesó el lote bajo supervisión de calidad.',
    'Se descartó el lote afectado previo análisis de riesgo.',
]

DESCRIPCIONES_QR = [
    'Cliente reporta producto con humedad visible al abrir bolsa.',
    'Reclamo por entrega con 2 días de retraso sobre fecha pactada.',
    'Documentación de lote incorrecta enviada junto al despacho.',
    'Cliente informa sabor atípico en muestra de aceite.',
    'Reclamo por cantidad menor a la facturada.',
    'Queja por atención deficiente en recepción de despacho.',
    'Rotura de packaging primario durante transporte.',
]

DESCRIPCIONES_OM = [
    'Implementar sistema de alertas automáticas para vencimiento de lotes.',
    'Digitalizar el proceso de control de recepción de materias primas.',
    'Reducir tiempo de limpieza entre turnos mediante cambio de procedimiento.',
    'Incorporar análisis de riesgo semanal en reunión de calidad.',
    'Automatizar generación de informes de producción diaria.',
    'Mejorar señalización de áreas de cuarentena en planta.',
    'Actualizar procedimiento de calibración de balanzas.',
    'Optimizar ruta de despacho para reducir costos logísticos.',
]

NOMBRES_PROYECTO = [
    'Plan de acción contaminación cruzada L-14',
    'Rediseño de procedimiento de embalaje',
    'Capacitación en BPM para operarios de planta',
    'Implementación de trazabilidad digital lote a lote',
    'Calibración integral de equipos de medición Q2-2026',
    'Revisión de proveedores críticos',
    'Actualización de POES de limpieza y desinfección',
    'Proyecto de mejora de rendimiento línea aceitera',
]

SUBTAREAS = [
    ['Relevamiento inicial', 'Análisis de causas', 'Propuesta de acción', 'Implementación', 'Verificación final'],
    ['Diagnóstico', 'Plan de trabajo', 'Ejecución fase 1', 'Ejecución fase 2', 'Cierre y reporte'],
    ['Reunión de equipo', 'Redacción de procedimiento', 'Aprobación', 'Capacitación', 'Auditoría'],
]

CLIENTES_ID = ['CLI-001 / Molinos SA', 'CLI-002 / Agro Norte SRL', 'CLI-003 / Cooperativa del Sur',
               'CLI-004 / Export Granos SA', 'CLI-005 / Distribuidora Central']


def rand_date(days_back=365, days_forward=0):
    hoy = date.today()
    return hoy - timedelta(days=random.randint(0, days_back)) + timedelta(days=random.randint(0, days_forward))


# ── Command ───────────────────────────────────────────────────────────────────

class Command(BaseCommand):
    help = 'Genera datos de prueba variados para el SGC'

    def add_arguments(self, parser):
        parser.add_argument(
            '--flush', action='store_true',
            help='Elimina los datos existentes antes de generar nuevos'
        )

    @transaction.atomic
    def handle(self, *args, **options):
        if options['flush']:
            self.stdout.write('Eliminando datos existentes...')
            VerificacionEficacia.objects.all().delete()
            Subtarea.objects.all().delete()
            Proyecto.objects.all().delete()
            OportunidadMejora.objects.all().delete()
            QuejaReclamo.objects.all().delete()
            CincoPorques.objects.all().delete()
            NoConformidad.objects.all().delete()
            self.stdout.write(self.style.WARNING('  Datos eliminados.'))

        # ── Usuarios ──────────────────────────────────────────────────────────
        self.stdout.write('Creando usuarios de prueba...')
        roles = [('admin_demo', 'admin'), ('calidad_demo', 'calidad'),
                 ('operario_demo', 'operario'), ('manager_demo', 'manager')]
        usuarios = {}
        for username, rol in roles:
            u, created = Usuario.objects.get_or_create(
                username=username,
                defaults={
                    'email': f'{username}@edpagroindustrial.com',
                    'first_name': username.split('_')[0].capitalize(),
                    'last_name': 'Demo',
                    'rol': rol,
                    'is_staff': rol == 'admin',
                }
            )
            if created:
                u.set_password('Demo1234!')
                u.save()
            usuarios[rol] = u
        self.stdout.write(self.style.SUCCESS(f'  {len(usuarios)} usuarios listos (contraseña: Demo1234!)'))

        # ── Sectores ─────────────────────────────────────────────────────────
        sectores = list(Sector.objects.filter(activo=True))
        if not sectores:
            self.stdout.write(self.style.ERROR('  No hay sectores activos. Ejecutá primero: python manage.py migrate'))
            return

        all_users = list(usuarios.values())

        # ── No Conformidades ─────────────────────────────────────────────────
        self.stdout.write('Generando No Conformidades...')
        ncs_creadas = []
        estados_nc = list(EstadoNC.values)
        prioridades = list(PrioridadNC.values)
        clasificaciones = list(ClasificacionNC.values)

        # NC directas variadas
        configs_nc = [
            # (estado, prioridad, clasificacion, eficacia, con_5porques)
            (EstadoNC.CERRADA,          PrioridadNC.ALTA,    ClasificacionNC.PRODUCTO,  EficaciaNC.EFICAZ,     True),
            (EstadoNC.CERRADA,          PrioridadNC.CRITICA, ClasificacionNC.PROCESO,   EficaciaNC.NO_EFICAZ,  True),
            (EstadoNC.EN_IMPLEMENTACION,PrioridadNC.MEDIA,   ClasificacionNC.MATERIAL_NO_CONFORME, EficaciaNC.PENDIENTE, True),
            (EstadoNC.APROBADA,         PrioridadNC.BAJA,    ClasificacionNC.SISTEMA,   EficaciaNC.PENDIENTE,  False),
            (EstadoNC.EN_REVISION,      PrioridadNC.MEDIA,   ClasificacionNC.LOGISTICA, EficaciaNC.PENDIENTE,  False),
            (EstadoNC.BORRADOR,         PrioridadNC.ALTA,    ClasificacionNC.PRODUCTO,  EficaciaNC.PENDIENTE,  False),
            (EstadoNC.CERRADA,          PrioridadNC.MEDIA,   ClasificacionNC.PROCESO,   EficaciaNC.EFICAZ,     True),
            (EstadoNC.RECHAZADA,        PrioridadNC.BAJA,    ClasificacionNC.SISTEMA,   EficaciaNC.PENDIENTE,  False),
            (EstadoNC.APROBADA,         PrioridadNC.CRITICA, ClasificacionNC.PRODUCTO,  EficaciaNC.PENDIENTE,  True),
            (EstadoNC.EN_IMPLEMENTACION,PrioridadNC.ALTA,    ClasificacionNC.PROCESO,   EficaciaNC.PENDIENTE,  True),
        ]

        for i, (estado, prioridad, clasificacion, eficacia, hacer_5p) in enumerate(configs_nc):
            fecha_nc = rand_date(days_back=180)
            sector = random.choice(sectores)
            responsable = random.choice(all_users)
            desc = DESCRIPCIONES_NC[i % len(DESCRIPCIONES_NC)]

            nc = NoConformidad.objects.create(
                fecha=fecha_nc,
                sector=sector,
                responsable=responsable,
                descripcion=desc,
                prioridad=prioridad,
                clasificacion=clasificacion,
                estado=estado,
                origen=OrigenNC.DIRECTO,
                descripcion_correccion=random.choice(CORRECCIONES_NC),
                probabilidad=random.randint(1, 5),
                impacto=random.randint(1, 5),
                eficacia=eficacia,
                notificar_cliente=(clasificacion == ClasificacionNC.PRODUCTO),
                email_cliente='calidad@cliente.com' if clasificacion == ClasificacionNC.PRODUCTO else '',
                contaminacion_cruzada=(clasificacion == ClasificacionNC.PRODUCTO and random.random() > 0.7),
            )
            ncs_creadas.append(nc)

            if hacer_5p:
                CincoPorques.objects.create(
                    nc=nc,
                    etapa_1=desc,
                    etapa_2=f'Porque no se respetó el procedimiento de {sector.nombre}.',
                    etapa_3='Porque el operario no recibió la capacitación correspondiente.',
                    etapa_4='Porque la planificación de capacitaciones estaba desactualizada.',
                    etapa_5='Porque no existe un proceso formal de revisión periódica.',
                    causa_raiz='Falta de proceso sistemático de capacitación y revisión periódica.',
                    accion_correctiva='Implementar cronograma anual de capacitaciones con registro y auditoría.',
                    completo=(estado in [EstadoNC.CERRADA, EstadoNC.EN_IMPLEMENTACION]),
                )

        self.stdout.write(self.style.SUCCESS(f'  {len(ncs_creadas)} NCs creadas'))

        # ── Quejas y Reclamos ────────────────────────────────────────────────
        self.stdout.write('Generando Quejas y Reclamos...')
        tipos_qr = list(TipoReclamo.values)
        configs_qr = [
            (EstadoQR.CERRADO,       'alta',  TipoReclamo.CALIDAD_PRODUCTO),
            (EstadoQR.EN_SEGUIMIENTO,'media', TipoReclamo.ENTREGA),
            (EstadoQR.EN_REVISION,   'baja',  TipoReclamo.DOCUMENTACION),
            (EstadoQR.CERRADO,       'media', TipoReclamo.ATENCION),
            (EstadoQR.BORRADOR,      'alta',  TipoReclamo.OTRO),
            (EstadoQR.EN_SEGUIMIENTO,'alta',  TipoReclamo.CALIDAD_PRODUCTO),
            (EstadoQR.CERRADO,       'baja',  TipoReclamo.ENTREGA),
        ]

        qrs_creadas = []
        for i, (estado, prioridad, tipo) in enumerate(configs_qr):
            fecha_qr = rand_date(days_back=120)
            sector = random.choice(sectores)
            qr = QuejaReclamo.objects.create(
                fecha=fecha_qr,
                sector=sector,
                responsable=random.choice(all_users),
                id_cliente_pedido=random.choice(CLIENTES_ID),
                tipo_reclamo=tipo,
                descripcion=DESCRIPCIONES_QR[i % len(DESCRIPCIONES_QR)],
                prioridad=prioridad,
                estado=estado,
                quien_recibe=random.choice(NOMBRES),
                detalle_visita_cliente='Visita presencial a planta del cliente el ' + fecha_qr.strftime('%d/%m/%Y'),
                acciones_a_tomar='Investigación interna, análisis de lote afectado y respuesta formal al cliente.',
                resultado='Se determinó causa raíz y se comunicó plan de acción.' if estado == EstadoQR.CERRADO else '',
                envio_mail=(estado == EstadoQR.CERRADO),
                fecha_cierre=fecha_qr + timedelta(days=random.randint(3, 15)) if estado == EstadoQR.CERRADO else None,
                dias_resolucion=random.randint(3, 20),
            )
            qrs_creadas.append(qr)

        self.stdout.write(self.style.SUCCESS(f'  {len(qrs_creadas)} QRs creadas'))

        # ── Oportunidades de Mejora ──────────────────────────────────────────
        self.stdout.write('Generando Oportunidades de Mejora...')
        configs_om = [
            (EstadoOM.CERRADA,          ClasificacionOM.MEJORA_PROCESO,  'alta',  RangoEvaluacion.TRES_MESES, EficaciaOM.EFICAZ),
            (EstadoOM.EN_IMPLEMENTACION,ClasificacionOM.INNOVACION,      'media', RangoEvaluacion.SEIS_MESES, EficaciaOM.PENDIENTE),
            (EstadoOM.APROBADA,         ClasificacionOM.EFICIENCIA,      'alta',  RangoEvaluacion.UN_MES,     EficaciaOM.PENDIENTE),
            (EstadoOM.EN_REVISION,      ClasificacionOM.CALIDAD,         'baja',  RangoEvaluacion.TRES_MESES, EficaciaOM.PENDIENTE),
            (EstadoOM.BORRADOR,         ClasificacionOM.OTRO,            'media', '',                          EficaciaOM.PENDIENTE),
            (EstadoOM.CERRADA,          ClasificacionOM.MEJORA_PROCESO,  'alta',  RangoEvaluacion.SEIS_MESES, EficaciaOM.NO_EFICAZ),
            (EstadoOM.EN_IMPLEMENTACION,ClasificacionOM.EFICIENCIA,      'media', RangoEvaluacion.TRES_MESES, EficaciaOM.PENDIENTE),
            (EstadoOM.APROBADA,         ClasificacionOM.CALIDAD,         'alta',  RangoEvaluacion.UN_MES,     EficaciaOM.PENDIENTE),
        ]

        oms_creadas = []
        for i, (estado, clasificacion, beneficio, rango, eficacia) in enumerate(configs_om):
            fecha_om = rand_date(days_back=150)
            sector = random.choice(sectores)
            desc = DESCRIPCIONES_OM[i % len(DESCRIPCIONES_OM)]
            om = OportunidadMejora.objects.create(
                fecha=fecha_om,
                sector=sector,
                responsable=random.choice(all_users),
                descripcion=desc,
                problema_a_mejorar=f'Ineficiencia detectada en área de {sector.nombre}: {desc[:60]}.',
                beneficio_potencial=beneficio,
                clasificacion=clasificacion,
                estado=estado,
                rango_evaluacion=rango,
                seguimiento='En seguimiento por responsable de área.' if estado != EstadoOM.BORRADOR else '',
                evidencia='Actas de reunión y registros de producción.' if estado == EstadoOM.CERRADA else '',
                eficacia=eficacia,
            )
            oms_creadas.append(om)

        self.stdout.write(self.style.SUCCESS(f'  {len(oms_creadas)} OMs creadas'))

        # ── Proyectos ────────────────────────────────────────────────────────
        self.stdout.write('Generando Proyectos...')
        proyectos_creados = []

        # 3 proyectos independientes
        for i in range(3):
            fecha_inicio = rand_date(days_back=90)
            estado = random.choice([EstadoProyecto.POR_HACER, EstadoProyecto.EN_CURSO, EstadoProyecto.EN_CURSO])
            p = Proyecto.objects.create(
                nombre=NOMBRES_PROYECTO[i],
                sector=random.choice(sectores),
                prioridad=random.choice(list(PrioridadProyecto.values)),
                proveedor='Interno',
                fecha_inicio=fecha_inicio,
                dias_ejecucion=random.choice([30, 45, 60, 90]),
                responsable=random.choice(all_users),
                estado=estado,
                origen=OrigenProyecto.INDEPENDIENTE,
            )
            proyectos_creados.append(p)
            # Subtareas
            subtareas_lista = random.choice(SUBTAREAS)
            for j, nombre_sub in enumerate(subtareas_lista):
                completada = (estado == EstadoProyecto.EN_CURSO and j < random.randint(1, 3))
                Subtarea.objects.create(
                    proyecto=p,
                    descripcion=nombre_sub,
                    completada=completada,
                    orden=j + 1,
                )

        # 3 proyectos desde NC aprobadas
        ncs_aprobadas = [nc for nc in ncs_creadas if nc.estado in [EstadoNC.APROBADA, EstadoNC.EN_IMPLEMENTACION, EstadoNC.CERRADA]]
        for i, nc in enumerate(ncs_aprobadas[:3]):
            # Solo crear si no existe ya
            if hasattr(nc, 'proyecto') and nc.proyecto:
                proyectos_creados.append(nc.proyecto)
                continue
            fecha_inicio = nc.fecha + timedelta(days=random.randint(3, 10))
            estado = EstadoProyecto.FINALIZADO if nc.estado == EstadoNC.CERRADA else EstadoProyecto.EN_CURSO
            p = Proyecto.objects.create(
                nombre=f'Correctivo: {nc.descripcion[:60]}',
                sector=nc.sector,
                prioridad=PrioridadProyecto.ALTA if nc.prioridad in ['alta', 'critica'] else PrioridadProyecto.MEDIA,
                proveedor='Interno',
                fecha_inicio=fecha_inicio,
                dias_ejecucion=random.choice([30, 60, 90]),
                responsable=nc.responsable,
                estado=estado,
                origen=OrigenProyecto.NC,
                nc=nc,
            )
            proyectos_creados.append(p)
            subtareas_lista = random.choice(SUBTAREAS)
            for j, nombre_sub in enumerate(subtareas_lista):
                completada = (estado == EstadoProyecto.FINALIZADO or
                              (estado == EstadoProyecto.EN_CURSO and j < 2))
                Subtarea.objects.create(
                    proyecto=p,
                    descripcion=nombre_sub,
                    completada=completada,
                    orden=j + 1,
                )

        # 2 proyectos desde OM
        oms_aprobadas = [om for om in oms_creadas if om.estado in [EstadoOM.APROBADA, EstadoOM.EN_IMPLEMENTACION]]
        for om in oms_aprobadas[:2]:
            fecha_inicio = om.fecha + timedelta(days=random.randint(5, 15))
            p = Proyecto.objects.create(
                nombre=f'Mejora: {om.descripcion[:60]}',
                sector=om.sector,
                prioridad=PrioridadProyecto.MEDIA,
                proveedor='Interno',
                fecha_inicio=fecha_inicio,
                dias_ejecucion=random.choice([45, 60]),
                responsable=om.responsable,
                estado=EstadoProyecto.EN_CURSO,
                origen=OrigenProyecto.OM,
                om=om,
            )
            proyectos_creados.append(p)
            for j, nombre_sub in enumerate(SUBTAREAS[0]):
                Subtarea.objects.create(
                    proyecto=p,
                    descripcion=nombre_sub,
                    completada=(j < 2),
                    orden=j + 1,
                )

        self.stdout.write(self.style.SUCCESS(f'  {len(proyectos_creados)} proyectos creados'))

        # ── Verificaciones de Eficacia ───────────────────────────────────────
        self.stdout.write('Generando Verificaciones de Eficacia...')
        verificaciones_creadas = 0
        proyectos_finalizados = [p for p in proyectos_creados if p.estado == EstadoProyecto.FINALIZADO]

        for p in proyectos_finalizados:
            # Evitar duplicados si ya existe
            if VerificacionEficacia.objects.filter(proyecto=p).exists():
                continue
            fecha_cierre = p.fecha_inicio + timedelta(days=p.dias_ejecucion)
            fecha_obj = fecha_cierre + timedelta(days=90)
            estado_v = random.choice([EstadoVerificacion.PENDIENTE, EstadoVerificacion.EFICAZ, EstadoVerificacion.EN_REVISION])
            v = VerificacionEficacia.objects.create(
                proyecto=p,
                fecha_cierre_proyecto=fecha_cierre,
                fecha_objetivo=fecha_obj,
                estado=estado_v,
                responsable=p.responsable,
                fecha_realizada=fecha_cierre + timedelta(days=random.randint(80, 95)) if estado_v == EstadoVerificacion.EFICAZ else None,
                resultado_descripcion='La acción correctiva resultó eficaz según los indicadores relevados.' if estado_v == EstadoVerificacion.EFICAZ else '',
            )
            verificaciones_creadas += 1

        self.stdout.write(self.style.SUCCESS(f'  {verificaciones_creadas} verificaciones creadas'))

        # ── Resumen final ────────────────────────────────────────────────────
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('=' * 55))
        self.stdout.write(self.style.SUCCESS('  DATOS DE PRUEBA GENERADOS EXITOSAMENTE'))
        self.stdout.write(self.style.SUCCESS('=' * 55))
        self.stdout.write(f'  NCs:            {NoConformidad.objects.count()}')
        self.stdout.write(f'  QRs:            {QuejaReclamo.objects.count()}')
        self.stdout.write(f'  OMs:            {OportunidadMejora.objects.count()}')
        self.stdout.write(f'  Proyectos:      {Proyecto.objects.count()}')
        self.stdout.write(f'  Subtareas:      {Subtarea.objects.count()}')
        self.stdout.write(f'  Verificaciones: {VerificacionEficacia.objects.count()}')
        self.stdout.write('')
        self.stdout.write('  Usuarios de prueba:')
        self.stdout.write('    admin_demo / Demo1234!   (rol: admin)')
        self.stdout.write('    calidad_demo / Demo1234! (rol: calidad)')
        self.stdout.write('    operario_demo / Demo1234!(rol: operario)')
        self.stdout.write('    manager_demo / Demo1234! (rol: manager)')
        self.stdout.write('')
        self.stdout.write('  App corriendo en: http://127.0.0.1:8000/')
        self.stdout.write(self.style.SUCCESS('=' * 55))
