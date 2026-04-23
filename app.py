import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import streamlit.components.v1 as components
import json
import os
from io import BytesIO
from datetime import date, timedelta
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image as RLImage

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="SGC - EDP Agroindustrial", layout="wide")
DATA_FILE = "data/datos_sgc.json"

# --- 2. INICIALIZACIÓN DE DATOS (SESSION STATE) ---
def get_demo_df_nc():
    return pd.DataFrame([
        {'id': 'NC-2026-N01', 'tipo': 'Proceso', 'gravedad': 'Mayor', 'riesgo': 'Alta', 'estado': 'Abierta', 'sector': 'Producción', 'fecha_in': date(2026, 1, 3), 'proyecto_asociado': ''},
        {'id': 'NC-2026-N02', 'tipo': 'Producto', 'gravedad': 'Menor', 'riesgo': 'Media', 'estado': 'En análisis', 'sector': 'Calidad', 'fecha_in': date(2026, 1, 15), 'proyecto_asociado': 'PRY-2026-N01'},
        {'id': 'NC-2026-N03', 'tipo': 'Logística', 'gravedad': 'Mayor', 'riesgo': 'Alta', 'estado': 'Cerrada', 'sector': 'Logística', 'fecha_in': date(2026, 2, 1), 'proyecto_asociado': ''},
        {'id': 'NC-2026-N04', 'tipo': 'Sistema', 'gravedad': 'Crítica', 'riesgo': 'Alta', 'estado': 'Abierta', 'sector': 'IT', 'fecha_in': date(2026, 2, 17), 'proyecto_asociado': ''},
        {'id': 'NC-2026-N05', 'tipo': 'Proceso', 'gravedad': 'Menor', 'riesgo': 'Baja', 'estado': 'Cerrada', 'sector': 'Administración', 'fecha_in': date(2026, 2, 25), 'proyecto_asociado': ''},
        {'id': 'NC-2026-N06', 'tipo': 'Producto', 'gravedad': 'Mayor', 'riesgo': 'Media', 'estado': 'En implementación', 'sector': 'Producción', 'fecha_in': date(2026, 3, 8), 'proyecto_asociado': ''},
        {'id': 'NC-2026-N07', 'tipo': 'Sistema', 'gravedad': 'Menor', 'riesgo': 'Baja', 'estado': 'Cerrada', 'sector': 'Comercial', 'fecha_in': date(2026, 3, 19), 'proyecto_asociado': ''},
        {'id': 'NC-2026-N08', 'tipo': 'Logística', 'gravedad': 'Crítica', 'riesgo': 'Alta', 'estado': 'Abierta', 'sector': 'Logística', 'fecha_in': date(2026, 4, 2), 'proyecto_asociado': ''}
    ])


def get_demo_df_qyr():
    return pd.DataFrame([
        {'id': 'QYR-2026-N01', 'cliente': 'Fedea S.A [30-68514149-4]', 'producto': '20359 Fedea-1.2%',
         'sector': 'Logística', 'estado': 'Cerrado', 'dias_res': 2, 'fecha_in': date(2026, 1, 5)},
        {'id': 'QYR-2026-N02', 'cliente': 'AgroNorte SRL [30-71112233-9]', 'producto': 'Iniciador Bovino 18%',
         'sector': 'Comercial', 'estado': 'Abierto', 'dias_res': 5, 'fecha_in': date(2026, 1, 18)},
        {'id': 'QYR-2026-N03', 'cliente': 'Coop. El Trigal [30-69887766-1]', 'producto': 'Núcleo Lechero 4%',
         'sector': 'Producto', 'estado': 'En seguimiento', 'dias_res': 7, 'fecha_in': date(2026, 2, 2)},
        {'id': 'QYR-2026-N04', 'cliente': 'Granja Los Pinos [30-70444999-7]', 'producto': 'Premix Engorde 2%',
         'sector': 'Manejo', 'estado': 'Cerrado', 'dias_res': 3, 'fecha_in': date(2026, 2, 21)},
        {'id': 'QYR-2026-N05', 'cliente': 'Campo Sur SA [30-68999444-2]', 'producto': 'Fedea-1.2% - Adaptación',
         'sector': 'Logística', 'estado': 'Abierto', 'dias_res': 6, 'fecha_in': date(2026, 3, 4)},
        {'id': 'QYR-2026-N06', 'cliente': 'Est. Don Emilio [20-22111999-0]', 'producto': 'Concentrado Porcino 35%',
         'sector': 'Producto', 'estado': 'Cerrado', 'dias_res': 4, 'fecha_in': date(2026, 3, 12)},
        {'id': 'QYR-2026-N07', 'cliente': 'BioFeed SAS [30-73335555-8]', 'producto': 'Mineral Ovino Plus',
         'sector': 'Comercial', 'estado': 'En seguimiento', 'dias_res': 8, 'fecha_in': date(2026, 3, 29)},
        {'id': 'QYR-2026-N08', 'cliente': 'Fedea S.A [30-68514149-4]', 'producto': '20359 Fedea-1.2%',
         'sector': 'Logística', 'estado': 'Cerrado', 'dias_res': 2, 'fecha_in': date(2026, 4, 6)}
    ])


def get_demo_df_om():
    return pd.DataFrame([
        {'id': 'OM-2026-N01', 'sector': 'Producción', 'oportunidad': 'Estandarizar checklist de arranque de línea',
         'estado': 'En Implementación', 'responsable': 'Tercero Kanofer', 'fecha_in': date(2026, 1, 7), 'proyecto_asociado': 'PRY-2026-N02'},
        {'id': 'OM-2026-N02', 'sector': 'Comercial', 'oportunidad': 'Plantilla única para respuesta a reclamos frecuentes',
         'estado': 'Nuevo', 'responsable': 'Laura M.', 'fecha_in': date(2026, 1, 22), 'proyecto_asociado': ''},
        {'id': 'OM-2026-N03', 'sector': 'Logística', 'oportunidad': 'Trazabilidad por QR en despacho y recepción',
         'estado': 'En Implementación', 'responsable': 'Javier R.', 'fecha_in': date(2026, 2, 6), 'proyecto_asociado': 'PRY-2026-N03'},
        {'id': 'OM-2026-N04', 'sector': 'Administración', 'oportunidad': 'Digitalización de firmas de conformidad',
         'estado': 'Cerrado', 'responsable': 'Paula G.', 'fecha_in': date(2026, 2, 20), 'proyecto_asociado': ''},
        {'id': 'OM-2026-N05', 'sector': 'IT', 'oportunidad': 'Alertas automáticas por desvío de KPI crítico',
         'estado': 'Nuevo', 'responsable': 'Dario (IT)', 'fecha_in': date(2026, 3, 3), 'proyecto_asociado': ''},
        {'id': 'OM-2026-N06', 'sector': 'Producción', 'oportunidad': 'Tablero visual de mermas por turno',
         'estado': 'Cerrado', 'responsable': 'Miguel T.', 'fecha_in': date(2026, 3, 14), 'proyecto_asociado': ''},
        {'id': 'OM-2026-N07', 'sector': 'Comercial', 'oportunidad': 'Encuesta post-entrega para clientes clave',
         'estado': 'En Implementación', 'responsable': 'Carla P.', 'fecha_in': date(2026, 3, 30), 'proyecto_asociado': ''},
        {'id': 'OM-2026-N08', 'sector': 'Logística', 'oportunidad': 'Control preventivo de estiba en ruta larga',
         'estado': 'Nuevo', 'responsable': 'Ramiro V.', 'fecha_in': date(2026, 4, 5), 'proyecto_asociado': ''}
    ])


def get_demo_df_proyectos():
    return pd.DataFrame([
        {
            'id': 'PRY-2026-N01',
            'nombre': 'Plan de mejoras proveedor logístico',
            'prioridad': 'Alta',
            'area': 'Logística',
            'proveedor': 'Transporte Ruta Sur',
            'fecha_inicio': date(2026, 1, 20),
            'dias_ejecucion': 30,
            'fecha_fin': date(2026, 2, 19),
            'responsable': 'Laura M.',
            'estado': 'En curso',
            'seguimiento': 'Relevar desvíos actuales\nCoordinar reunión con proveedor\nImplementar plan piloto',
            'origen_tipo': 'No Conformidad',
            'origen_id': 'NC-2026-N02'
        },
        {
            'id': 'PRY-2026-N02',
            'nombre': 'Checklist digital de arranque',
            'prioridad': 'Media',
            'area': 'Producción',
            'proveedor': 'Kanofer',
            'fecha_inicio': date(2026, 1, 10),
            'dias_ejecucion': 45,
            'fecha_fin': date(2026, 2, 24),
            'responsable': 'Tercero Kanofer',
            'estado': 'Finalizado',
            'seguimiento': 'Definir formato\nCapacitar supervisores\nLiberar versión final',
            'origen_tipo': 'Oportunidad de Mejora',
            'origen_id': 'OM-2026-N01'
        },
        {
            'id': 'PRY-2026-N03',
            'nombre': 'Trazabilidad QR en logística',
            'prioridad': 'Alta',
            'area': 'Logística',
            'proveedor': 'QR Solutions',
            'fecha_inicio': date(2026, 2, 8),
            'dias_ejecucion': 60,
            'fecha_fin': date(2026, 4, 9),
            'responsable': 'Javier R.',
            'estado': 'En curso',
            'seguimiento': 'Seleccionar proveedor\nConfigurar puntos de lectura\nPrueba en despacho',
            'origen_tipo': 'Oportunidad de Mejora',
            'origen_id': 'OM-2026-N03'
        },
        {
            'id': 'PRY-2026-N04',
            'nombre': 'Proyecto independiente de tablero de indicadores',
            'prioridad': 'Baja',
            'area': 'IT',
            'proveedor': 'Interno',
            'fecha_inicio': date(2026, 4, 1),
            'dias_ejecucion': 20,
            'fecha_fin': date(2026, 4, 21),
            'responsable': 'Dario (IT)',
            'estado': 'Por hacer',
            'seguimiento': 'Definir KPIs\nDiseñar vistas\nValidar con gerencia',
            'origen_tipo': 'Independiente',
            'origen_id': ''
        }
    ])


def get_demo_responsables():
    return [
        'Tercero Kanofer',
        'Laura M.',
        'Javier R.',
        'Paula G.',
        'Dario (IT)',
        'Miguel T.',
        'Carla P.',
        'Ramiro V.'
    ]


def get_empty_df_nc():
    return pd.DataFrame(columns=['id', 'tipo', 'gravedad', 'riesgo', 'estado', 'sector', 'fecha_in', 'proyecto_asociado'])


def get_empty_df_qyr():
    return pd.DataFrame(columns=['id', 'cliente', 'producto', 'sector', 'estado', 'dias_res', 'fecha_in'])


def get_empty_df_om():
    return pd.DataFrame(columns=['id', 'sector', 'oportunidad', 'estado', 'responsable', 'fecha_in', 'proyecto_asociado'])


def get_empty_df_proyectos():
    return pd.DataFrame(columns=[
        'id', 'nombre', 'prioridad', 'area', 'proveedor', 'fecha_inicio', 'dias_ejecucion', 'fecha_fin',
        'responsable', 'estado', 'seguimiento', 'origen_tipo', 'origen_id'
    ])


def cargar_datos_demo():
    st.session_state.df_nc = get_demo_df_nc()
    st.session_state.df_qyr = get_demo_df_qyr()
    st.session_state.df_om = get_demo_df_om()
    st.session_state.df_proyectos = get_demo_df_proyectos()
    st.session_state.responsables = get_demo_responsables()
    guardar_datos_persistentes()


def limpiar_datos():
    st.session_state.df_nc = get_empty_df_nc()
    st.session_state.df_qyr = get_empty_df_qyr()
    st.session_state.df_om = get_empty_df_om()
    st.session_state.df_proyectos = get_empty_df_proyectos()
    guardar_datos_persistentes()


def cerrar_aplicacion():
    # Marca la sesión como cerrada para evitar cortar el servidor y mostrar error de conexión.
    st.session_state.app_cerrada = True


def detener_servidor():
    guardar_datos_persistentes()
    os._exit(0)


def asegurar_columna(df_key, column_name, default_value=""):
    if column_name not in st.session_state[df_key].columns:
        st.session_state[df_key][column_name] = default_value


def _df_to_serializable_records(df, date_columns):
    df_ser = df.copy()
    for col in date_columns:
        if col in df_ser.columns:
            df_ser[col] = pd.to_datetime(df_ser[col], errors='coerce').dt.strftime('%Y-%m-%d')
    return df_ser.where(pd.notnull(df_ser), None).to_dict(orient='records')


def _records_to_df(records, empty_df_fn, date_columns):
    base_df = empty_df_fn()
    if not records:
        return base_df

    df = pd.DataFrame(records)
    for col in base_df.columns:
        if col not in df.columns:
            df[col] = ''
    df = df[base_df.columns]

    for col in date_columns:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce').dt.date
    return df


def guardar_datos_persistentes():
    payload = {
        'nc': _df_to_serializable_records(st.session_state.df_nc, ['fecha_in']),
        'qyr': _df_to_serializable_records(st.session_state.df_qyr, ['fecha_in']),
        'om': _df_to_serializable_records(st.session_state.df_om, ['fecha_in']),
        'proyectos': _df_to_serializable_records(st.session_state.df_proyectos, ['fecha_inicio', 'fecha_fin']),
        'responsables': list(st.session_state.responsables),
    }
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)


def cargar_datos_persistentes():
    if not os.path.exists(DATA_FILE):
        return False

    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            payload = json.load(f)

        st.session_state.df_nc = _records_to_df(payload.get('nc', []), get_empty_df_nc, ['fecha_in'])
        st.session_state.df_qyr = _records_to_df(payload.get('qyr', []), get_empty_df_qyr, ['fecha_in'])
        st.session_state.df_om = _records_to_df(payload.get('om', []), get_empty_df_om, ['fecha_in'])
        st.session_state.df_proyectos = _records_to_df(payload.get('proyectos', []), get_empty_df_proyectos, ['fecha_inicio', 'fecha_fin'])
        st.session_state.responsables = payload.get('responsables', get_demo_responsables())
        return True
    except Exception:
        return False


def calcular_fecha_fin(fecha_inicio, dias_ejecucion):
    return fecha_inicio + timedelta(days=int(dias_ejecucion))


def registrar_responsable(nombre):
    nombre_limpio = nombre.strip()
    if nombre_limpio and nombre_limpio not in st.session_state.responsables:
        st.session_state.responsables = sorted(st.session_state.responsables + [nombre_limpio])
        guardar_datos_persistentes()


def crear_proyecto(nombre, prioridad, area, proveedor, fecha_inicio, dias_ejecucion, responsable, estado, seguimiento, origen_tipo, origen_id):
    registrar_responsable(responsable)
    proyecto_id = f"PRY-2026-N{len(st.session_state.df_proyectos) + 1:02d}"
    nuevo_proyecto = {
        'id': proyecto_id,
        'nombre': nombre,
        'prioridad': prioridad,
        'area': area,
        'proveedor': proveedor,
        'fecha_inicio': fecha_inicio,
        'dias_ejecucion': int(dias_ejecucion),
        'fecha_fin': calcular_fecha_fin(fecha_inicio, dias_ejecucion),
        'responsable': responsable,
        'estado': estado,
        'seguimiento': seguimiento,
        'origen_tipo': origen_tipo,
        'origen_id': origen_id,
    }
    st.session_state.df_proyectos = pd.concat(
        [st.session_state.df_proyectos, pd.DataFrame([nuevo_proyecto])],
        ignore_index=True
    )
    guardar_datos_persistentes()
    return proyecto_id


def actualizar_proyecto(proyecto_id, datos):
    idx = st.session_state.df_proyectos.index[st.session_state.df_proyectos['id'] == proyecto_id]
    if len(idx) == 0:
        return False

    row_idx = idx[0]
    for col, val in datos.items():
        st.session_state.df_proyectos.at[row_idx, col] = val
    guardar_datos_persistentes()
    return True


def eliminar_proyecto(proyecto_id):
    st.session_state.df_proyectos = st.session_state.df_proyectos[
        st.session_state.df_proyectos['id'] != proyecto_id
    ].reset_index(drop=True)

    if 'proyecto_asociado' in st.session_state.df_nc.columns:
        st.session_state.df_nc.loc[st.session_state.df_nc['proyecto_asociado'] == proyecto_id, 'proyecto_asociado'] = ''
    if 'proyecto_asociado' in st.session_state.df_om.columns:
        st.session_state.df_om.loc[st.session_state.df_om['proyecto_asociado'] == proyecto_id, 'proyecto_asociado'] = ''

    guardar_datos_persistentes()


def selector_responsable(label, key_prefix, default_value=""):
    opciones = list(st.session_state.responsables)
    opciones_select = opciones + ["Otro..."]
    if default_value and default_value not in opciones:
        index_default = len(opciones_select) - 1
    elif default_value in opciones:
        index_default = opciones.index(default_value)
    else:
        index_default = 0 if opciones else len(opciones_select) - 1

    responsable = st.selectbox(label, opciones_select, index=index_default, key=f"{key_prefix}_responsable")
    if responsable == "Otro...":
        return st.text_input("Nuevo responsable", value=default_value if default_value not in opciones else "", key=f"{key_prefix}_responsable_nuevo")
    return responsable


def capturar_datos_proyecto(
    key_prefix,
    nombre_default="",
    responsable_default="",
    fecha_inicio_default=None,
    estado_default="Por hacer",
    prioridad_default="Media",
    area_default="Producción",
    proveedor_default="Interno",
    dias_ejecucion_default=30,
    seguimiento_default=""
):
    if fecha_inicio_default is None:
        fecha_inicio_default = date.today()

    c1, c2, c3 = st.columns(3)
    with c1:
        nombre = st.text_input("Nombre del proyecto", value=nombre_default, key=f"{key_prefix}_nombre")
        prioridades = ["Alta", "Media", "Baja"]
        prioridad_idx = prioridades.index(prioridad_default) if prioridad_default in prioridades else 1
        prioridad = st.selectbox("Prioridad", prioridades, index=prioridad_idx, key=f"{key_prefix}_prioridad")
        areas = ["Producción", "Comercial", "Logística", "Administración", "IT", "Calidad"]
        area_idx = areas.index(area_default) if area_default in areas else 0
        area = st.selectbox("Área", areas, index=area_idx, key=f"{key_prefix}_area")
        proveedor = st.text_input("Proveedor", value=proveedor_default, key=f"{key_prefix}_proveedor")
    with c2:
        fecha_inicio = st.date_input("Fecha de inicio", value=fecha_inicio_default, key=f"{key_prefix}_fecha_inicio")
        dias_ejecucion = st.number_input("Días de ejecución", min_value=1, value=int(dias_ejecucion_default), step=1, key=f"{key_prefix}_dias")
        fecha_fin = calcular_fecha_fin(fecha_inicio, dias_ejecucion)
        st.text_input("Fecha final estimada", value=str(fecha_fin), disabled=True, key=f"{key_prefix}_fecha_fin")
    with c3:
        responsable = selector_responsable("Responsable", key_prefix, default_value=responsable_default)
        estados = ["Por hacer", "En curso", "Finalizado"]
        estado_idx = estados.index(estado_default) if estado_default in estados else 0
        estado = st.selectbox("Estado", estados, index=estado_idx, key=f"{key_prefix}_estado")

    seguimiento = st.text_area(
        "Seguimiento del proyecto (una tarea por línea)",
        value=seguimiento_default,
        key=f"{key_prefix}_seguimiento"
    )
    st.caption("Cada línea del seguimiento se mostrará como un checklist visual del proyecto.")

    return {
        'nombre': nombre,
        'prioridad': prioridad,
        'area': area,
        'proveedor': proveedor,
        'fecha_inicio': fecha_inicio,
        'dias_ejecucion': dias_ejecucion,
        'fecha_fin': fecha_fin,
        'responsable': responsable,
        'estado': estado,
        'seguimiento': seguimiento,
    }


def mostrar_checklist_seguimiento(seguimiento, key_prefix):
    items = [item.strip() for item in str(seguimiento).splitlines() if item.strip()]
    if not items:
        st.caption('Sin tareas de seguimiento cargadas.')
        return
    for idx, item in enumerate(items, start=1):
        st.checkbox(item, value=False, disabled=True, key=f'{key_prefix}_{idx}')


def limpiar_filtros_proyectos():
    st.session_state.q_pry_texto = ""
    st.session_state.q_pry_estado = []
    st.session_state.q_pry_prioridad = []
    st.session_state.q_pry_area = []
    if not st.session_state.df_proyectos.empty and 'fecha_inicio' in st.session_state.df_proyectos.columns:
        fechas = pd.to_datetime(st.session_state.df_proyectos['fecha_inicio'], errors='coerce').dropna()
        if not fechas.empty:
            st.session_state.q_pry_fecha_desde = fechas.min().date()
            st.session_state.q_pry_fecha_hasta = fechas.max().date()


if 'datos_inicializados' not in st.session_state:
    if not cargar_datos_persistentes():
        st.session_state.df_nc = get_demo_df_nc()
        st.session_state.df_qyr = get_demo_df_qyr()
        st.session_state.df_om = get_demo_df_om()
        st.session_state.df_proyectos = get_demo_df_proyectos()
        st.session_state.responsables = get_demo_responsables()
    st.session_state.datos_inicializados = True

if 'df_nc' not in st.session_state:
    st.session_state.df_nc = get_empty_df_nc()
if 'df_qyr' not in st.session_state:
    st.session_state.df_qyr = get_empty_df_qyr()
if 'df_om' not in st.session_state:
    st.session_state.df_om = get_empty_df_om()
if 'df_proyectos' not in st.session_state:
    st.session_state.df_proyectos = get_empty_df_proyectos()
if 'responsables' not in st.session_state:
    st.session_state.responsables = get_demo_responsables()

asegurar_columna('df_nc', 'proyecto_asociado')
asegurar_columna('df_om', 'proyecto_asociado')
asegurar_columna('df_proyectos', 'area', 'Producción')

if st.session_state.get('app_cerrada', False):
    st.title("Aplicación cerrada")
    st.info("Podés cerrar esta pestaña. El servidor sigue activo en segundo plano.")
    st.stop()

# --- 3. FUNCIONES DE EXPORTACIÓN ---
def to_excel(df_nc, df_qyr, df_om, df_proyectos):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df_nc.to_excel(writer, sheet_name='No Conformidades', index=False)
        df_qyr.to_excel(writer, sheet_name='Quejas y Reclamos', index=False)
        df_om.to_excel(writer, sheet_name='Oportunidades Mejora', index=False)
        df_proyectos.to_excel(writer, sheet_name='Proyectos', index=False)
    return output.getvalue()


def to_excel_single(df, sheet_name):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name=sheet_name, index=False)
    return output.getvalue()


def _normalize_for_report(df):
    df_rep = df.copy()
    if not df_rep.empty:
        for col in df_rep.columns:
            if pd.api.types.is_datetime64_any_dtype(df_rep[col]):
                df_rep[col] = pd.to_datetime(df_rep[col], errors='coerce').dt.strftime('%Y-%m-%d')
    return df_rep.fillna('')


def dataframe_to_pdf_bytes(title, subtitle, df):
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        leftMargin=22,
        rightMargin=22,
        topMargin=22,
        bottomMargin=22
    )
    styles = getSampleStyleSheet()
    story = [
        Paragraph(title, styles['Title']),
        Paragraph(subtitle, styles['Normal']),
        Spacer(1, 10)
    ]

    df_rep = _normalize_for_report(df)
    if df_rep.empty:
        story.append(Paragraph('Sin datos para exportar.', styles['Normal']))
    else:
        table_data = [list(df_rep.columns)] + df_rep.astype(str).values.tolist()
        table = Table(table_data, repeatRows=1)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4e79')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('GRID', (0, 0), (-1, -1), 0.3, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f3f7fb')]),
        ]))
        story.append(table)

    doc.build(story)
    return buffer.getvalue()


def plotly_figure_to_png_bytes(fig, width=1100, height=500, scale=2):
    try:
        return fig.to_image(format='png', width=width, height=height, scale=scale)
    except Exception:
        return None


def dashboard_to_pdf_bytes(df_nc, df_qyr, df_om, fig_pie, fig_m, fig_qyr, fig_gantt=None, fig_torta_pry=None):
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        leftMargin=22,
        rightMargin=22,
        topMargin=22,
        bottomMargin=22
    )
    styles = getSampleStyleSheet()
    story = [
        Paragraph('Dashboard Gerencial - SGC', styles['Title']),
        Paragraph(f'Fecha de reporte: {date.today()}', styles['Normal']),
        Spacer(1, 10)
    ]

    reclamos_activos = len(df_qyr[df_qyr['estado'] != 'Cerrado']) if 'estado' in df_qyr.columns else 0
    kpi_rows = [
        ['KPI', 'Valor'],
        ['NC Totales', str(len(df_nc))],
        ['Eficiencia Respuesta', '94%'],
        ['Reclamos Activos', str(reclamos_activos)],
        ['Mejoras Scada/Kanofer', 'Activa'],
    ]
    tabla_kpi = Table(kpi_rows, repeatRows=1)
    tabla_kpi.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4e79')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 0.3, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f3f7fb')]),
    ]))
    story.append(tabla_kpi)
    story.append(Spacer(1, 10))
    story.append(Paragraph('Gráficos del tablero (capturados tal como se visualizan)', styles['Heading3']))
    story.append(Spacer(1, 6))

    # Replica el layout de pantalla: fila superior en 2 columnas (1 : 1.2) y fila inferior completa.
    pie_png = plotly_figure_to_png_bytes(fig_pie, width=900, height=520, scale=2)
    matrix_png = plotly_figure_to_png_bytes(fig_m, width=1080, height=520, scale=2)
    if pie_png and matrix_png:
        pie_img = RLImage(BytesIO(pie_png), width=300, height=190)
        matrix_img = RLImage(BytesIO(matrix_png), width=360, height=190)

        row1 = Table([[pie_img, matrix_img]], colWidths=[320, 420])
        row1.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ]))
        story.append(Paragraph('Fila superior: Distribución de NC y Matriz de Riesgo', styles['Heading4']))
        story.append(row1)
        story.append(Spacer(1, 8))
    else:
        story.append(Paragraph('No se pudieron incrustar los gráficos superiores en este PDF (error de exportación de imagen).', styles['Normal']))
        story.append(Spacer(1, 8))

    bar_png = plotly_figure_to_png_bytes(fig_qyr, width=1400, height=500, scale=2)
    if bar_png:
        bar_img = RLImage(BytesIO(bar_png), width=740, height=210)
        story.append(Paragraph('Fila inferior: Promedio de Días de Resolución por Sector', styles['Heading4']))
        story.append(bar_img)
        story.append(Spacer(1, 8))
    else:
        story.append(Paragraph('No se pudo incrustar el gráfico de resolución por sector en este PDF.', styles['Normal']))
        story.append(Spacer(1, 8))

    if fig_gantt is not None:
        gantt_png = plotly_figure_to_png_bytes(fig_gantt, width=1400, height=520, scale=2)
        if gantt_png:
            gantt_img = RLImage(BytesIO(gantt_png), width=740, height=220)
            story.append(Paragraph('Cronograma de Proyectos por Prioridad', styles['Heading4']))
            story.append(gantt_img)
            story.append(Spacer(1, 8))
        else:
            story.append(Paragraph('No se pudo incrustar el gráfico Gantt en este PDF.', styles['Normal']))
            story.append(Spacer(1, 8))

    if fig_torta_pry is not None:
        torta_pry_png = plotly_figure_to_png_bytes(fig_torta_pry, width=700, height=500, scale=2)
        if torta_pry_png:
            torta_pry_img = RLImage(BytesIO(torta_pry_png), width=300, height=210)
            story.append(Paragraph('Estado de Proyectos', styles['Heading4']))
            story.append(torta_pry_img)
            story.append(Spacer(1, 8))
        else:
            story.append(Paragraph('No se pudo incrustar el gráfico de estado de proyectos en este PDF.', styles['Normal']))
            story.append(Spacer(1, 8))

    story.append(Paragraph(f'Total de oportunidades de mejora: {len(df_om)}', styles['Normal']))
    doc.build(story)
    return buffer.getvalue()


def build_printable_html(title, df):
    df_rep = _normalize_for_report(df)
    table_html = df_rep.to_html(index=False, border=0)
    return f"""
<!DOCTYPE html>
<html lang=\"es\">
<head>
  <meta charset=\"UTF-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\" />
  <title>{title}</title>
  <style>
    body {{ font-family: Segoe UI, Arial, sans-serif; margin: 24px; color: #1f2937; }}
    h1 {{ margin: 0 0 8px; color: #12395b; }}
    p.meta {{ margin: 0 0 16px; color: #4b5563; }}
    table {{ border-collapse: collapse; width: 100%; font-size: 12px; }}
    th {{ background: #1f4e79; color: #fff; text-align: left; }}
    th, td {{ border: 1px solid #d1d5db; padding: 6px; vertical-align: top; }}
    tr:nth-child(even) td {{ background: #f8fafc; }}
    .actions {{ margin-bottom: 12px; }}
    .btn {{ background: #1f4e79; color: white; border: 0; padding: 8px 12px; cursor: pointer; border-radius: 6px; }}
    @media print {{
      .actions {{ display: none; }}
      body {{ margin: 8mm; }}
      @page {{ size: A4 landscape; margin: 8mm; }}
    }}
  </style>
</head>
<body>
  <div class=\"actions\"><button class=\"btn\" onclick=\"window.print()\">Imprimir / Guardar PDF</button></div>
  <h1>{title}</h1>
  <p class=\"meta\">Generado: {date.today()}</p>
  {table_html}
</body>
</html>
"""


def render_print_section(title, df, key_prefix):
    html_doc = build_printable_html(title, df)
    st.download_button(
        label="🧾 Descargar vista imprimible (HTML)",
        data=html_doc.encode('utf-8'),
        file_name=f"{key_prefix}_{date.today()}.html",
        mime="text/html"
    )
    if st.button("🖨️ Ver versión imprimible", key=f"btn_print_{key_prefix}"):
        components.html(html_doc, height=650, scrolling=True)


def filtrar_texto(df, columnas, texto):
    if not texto:
        return df
    patron = texto.strip()
    if not patron:
        return df
    mascara = False
    for col in columnas:
        mascara = mascara | df[col].astype(str).str.contains(patron, case=False, na=False)
    return df[mascara]


def limpiar_filtros_nc():
    st.session_state.q_nc_texto = ""
    st.session_state.q_nc_estado = []
    st.session_state.q_nc_tipo = []
    if not st.session_state.df_nc.empty and 'fecha_in' in st.session_state.df_nc.columns:
        fechas = pd.to_datetime(st.session_state.df_nc['fecha_in'], errors='coerce').dropna()
        if not fechas.empty:
            st.session_state.q_nc_fecha_desde = fechas.min().date()
            st.session_state.q_nc_fecha_hasta = fechas.max().date()


def limpiar_filtros_qyr():
    st.session_state.q_qyr_texto = ""
    st.session_state.q_qyr_sector = []
    st.session_state.q_qyr_estado = []
    if not st.session_state.df_qyr.empty:
        fechas = pd.to_datetime(st.session_state.df_qyr['fecha_in'], errors='coerce').dropna()
        if not fechas.empty:
            st.session_state.q_qyr_fecha_desde = fechas.min().date()
            st.session_state.q_qyr_fecha_hasta = fechas.max().date()


def limpiar_filtros_om():
    st.session_state.q_om_texto = ""
    st.session_state.q_om_sector = []
    st.session_state.q_om_estado = []
    if not st.session_state.df_om.empty and 'fecha_in' in st.session_state.df_om.columns:
        fechas = pd.to_datetime(st.session_state.df_om['fecha_in'], errors='coerce').dropna()
        if not fechas.empty:
            st.session_state.q_om_fecha_desde = fechas.min().date()
            st.session_state.q_om_fecha_hasta = fechas.max().date()

# --- 4. BARRA LATERAL (SIDEBAR) ---
with st.sidebar:
    try:
        st.image("edp.jpg", width="stretch")
    except:
        st.info("📌 Logo EDP Agro")
    
    st.title("🛡️ Panel de Control SGC")
    st.subheader("Gestión de Mejora Continua")
    seleccion = st.radio("Módulos:", ["Dashboard Gerencial", "Gestión de NC", "Quejas y Reclamos", "Oportunidad de Mejora", "Proyectos"])
    
    st.divider()
    st.subheader("📥 Exportar Datos")
    excel_file = to_excel(st.session_state.df_nc, st.session_state.df_qyr, st.session_state.df_om, st.session_state.df_proyectos)
    st.download_button(label="📊 Descargar Reporte Excel", data=excel_file, 
                       file_name=f'Reporte_Calidad_{date.today()}.xlsx')
    st.divider()
    st.subheader("👥 Responsables")
    nuevo_responsable = st.text_input("Agregar responsable", key="nuevo_responsable")
    if st.button("Sumar responsable", width="stretch"):
        registrar_responsable(nuevo_responsable)
    if st.session_state.responsables:
        st.caption("Lista compartida")
        st.write(", ".join(st.session_state.responsables))
    st.divider()
    st.subheader("🧪 Datos de Demo")
    c_demo1, c_demo2 = st.columns(2)
    with c_demo1:
        st.button("Cargar Demo", on_click=cargar_datos_demo, width="stretch")
    with c_demo2:
        st.button("Limpiar Todo", on_click=limpiar_datos, width="stretch")
    st.divider()
    st.subheader("💾 Persistencia")
    if st.button("Guardar datos ahora", width="stretch"):
        guardar_datos_persistentes()
        st.success("Datos guardados en disco.")
    st.caption(f"Archivo: {DATA_FILE}")
    st.divider()
    st.subheader("🚪 Salida")
    st.button("Cerrar vista", on_click=cerrar_aplicacion, width="stretch", type="secondary")
    confirmar_detener = st.checkbox("Confirmar detener servidor", key="confirmar_detener")
    st.button("Detener servidor", on_click=detener_servidor, disabled=not confirmar_detener, width="stretch", type="secondary")
    st.info("Demo v1.0 - Dario (IT)")

# --- 5. LÓGICA DE MÓDULOS ---

# --- A. DASHBOARD GERENCIAL ---
if seleccion == "Dashboard Gerencial":
    st.header("📊 Tablero de Toma de Decisiones")
    fig_gantt = None
    fig_torta_pry = None
    
    # KPIs Superiores
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("NC Totales", len(st.session_state.df_nc))
    c2.metric("Eficiencia Respuesta", "94%", "+2%")
    c3.metric("Reclamos Activos", len(st.session_state.df_qyr[st.session_state.df_qyr['estado'] != 'Cerrado']))
    c4.metric("Mejoras Scada/Kanofer", "Activa", border=True)

    st.divider()

    col_izq, col_der = st.columns([1, 1.2])
    
    with col_izq:
        fig_pie = px.pie(
            st.session_state.df_nc,
            names='tipo',
            title="Distribución de NC por Origen",
            hole=0.4,
            color='tipo',
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        fig_pie.update_traces(textinfo='percent+label')
        fig_pie.update_layout(
            paper_bgcolor='white',
            plot_bgcolor='white',
            font=dict(color='#1f2937')
        )
        st.plotly_chart(fig_pie, width="stretch")

    with col_der:
        st.subheader("⚠️ Matriz de Riesgo Dinámica (NC)")
        df_p = st.session_state.df_nc.copy()
        m_r, m_g = {'Baja': 0, 'Media': 1, 'Alta': 2}, {'Menor': 0, 'Mayor': 1, 'Crítica': 2}
        
        # Jitter para evitar solapamiento de diamantes
        df_p['x'] = df_p['riesgo'].map(m_r) + np.random.uniform(-0.1, 0.1, len(df_p))
        df_p['y'] = df_p['gravedad'].map(m_g) + np.random.uniform(-0.1, 0.1, len(df_p))

        fig_m = go.Figure(data=go.Heatmap(
            z=[[1, 4, 7], [2, 5, 8], [3, 6, 9]],
            x=[0, 1, 2], y=[0, 1, 2],
            colorscale=[[0, 'green'], [0.5, 'yellow'], [1, 'red']],
            showscale=False, hoverinfo='skip'
        ))
        fig_m.add_trace(go.Scatter(x=df_p['x'], y=df_p['y'], mode='markers+text',
                                   marker=dict(color='black', size=15, symbol='diamond', line=dict(width=2, color='white')),
                                   text=df_p['id'], textposition="top center"))
        fig_m.update_xaxes(tickvals=[0, 1, 2], ticktext=['Baja', 'Media', 'Alta'], range=[-0.5, 2.5])
        fig_m.update_yaxes(tickvals=[0, 1, 2], ticktext=['Menor', 'Mayor', 'Crítica'], range=[-0.5, 2.5])
        st.plotly_chart(fig_m, width="stretch")

    st.divider()
    st.subheader("📋 Resumen de Quejas y Reclamos por Sector")
    df_resumen_qyr = (
        st.session_state.df_qyr
        .groupby('sector', as_index=False)['dias_res']
        .mean()
        .sort_values('dias_res', ascending=False)
    )
    fig_qyr = px.bar(
        df_resumen_qyr,
        x='sector',
        y='dias_res',
        color='sector',
        color_discrete_sequence=px.colors.qualitative.Safe,
        text='dias_res',
        title='Promedio de Días de Resolución por Sector'
    )
    fig_qyr.update_traces(texttemplate='%{text:.1f}', textposition='outside')
    fig_qyr.update_layout(
        xaxis_title=None,
        yaxis_title='Días',
        xaxis_tickangle=0,
        yaxis=dict(rangemode='tozero'),
        showlegend=False,
        paper_bgcolor='white',
        plot_bgcolor='white',
        font=dict(color='#1f2937')
    )
    st.plotly_chart(fig_qyr, width="stretch")
    st.divider()
    st.subheader("🗂️ Cronograma de Proyectos (Gantt)")
    df_gantt = st.session_state.df_proyectos.copy()
    if df_gantt.empty:
        st.info("No hay proyectos cargados para mostrar el cronograma.")
    else:
        prioridad_orden = {'Alta': 0, 'Media': 1, 'Baja': 2}
        df_gantt['fecha_inicio'] = pd.to_datetime(df_gantt['fecha_inicio'], errors='coerce')
        df_gantt['fecha_fin'] = pd.to_datetime(df_gantt['fecha_fin'], errors='coerce')
        df_gantt = df_gantt.dropna(subset=['fecha_inicio', 'fecha_fin']).copy()

        if df_gantt.empty:
            st.info("Los proyectos no tienen fechas válidas para graficar.")
        else:
            df_gantt['orden_prioridad'] = df_gantt['prioridad'].map(prioridad_orden).fillna(99)
            df_gantt = df_gantt.sort_values(['orden_prioridad', 'fecha_inicio', 'nombre'])
            df_gantt['proyecto_gantt'] = df_gantt['nombre'] + " (" + df_gantt['id'] + ")"

            fig_gantt = px.timeline(
                df_gantt,
                x_start='fecha_inicio',
                x_end='fecha_fin',
                y='proyecto_gantt',
                color='prioridad',
                color_discrete_map={'Alta': '#d62728', 'Media': '#ff7f0e', 'Baja': '#2ca02c'},
                category_orders={'proyecto_gantt': df_gantt['proyecto_gantt'].tolist()},
                hover_data=['id', 'area', 'estado', 'responsable', 'proveedor', 'origen_tipo', 'origen_id'],
                title='Línea de tiempo de ejecución por prioridad'
            )
            fig_gantt.update_traces(text=df_gantt['area'], textposition='inside')
            fig_gantt.update_yaxes(autorange='reversed', title=None)
            fig_gantt.update_xaxes(title='Fecha')
            fig_gantt.update_layout(
                legend_title_text='Prioridad',
                paper_bgcolor='white',
                plot_bgcolor='white',
                font=dict(color='#1f2937')
            )
            st.plotly_chart(fig_gantt, width="stretch")

    st.divider()
    st.subheader("� Estado de Proyectos")
    df_pry_estado = st.session_state.df_proyectos.copy()
    if df_pry_estado.empty:
        st.info("No hay proyectos cargados para mostrar el estado.")
    else:
        conteo_estado = df_pry_estado['estado'].value_counts().reset_index()
        conteo_estado.columns = ['estado', 'cantidad']
        fig_torta_pry = px.pie(
            conteo_estado,
            names='estado',
            values='cantidad',
            title="Distribución de Proyectos por Estado",
            hole=0.4,
            color='estado',
            color_discrete_map={
                'Por Hacer': '#636EFA',
                'En Proceso': '#ff7f0e',
                'Finalizado': '#2ca02c',
            },
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        fig_torta_pry.update_traces(textinfo='percent+label+value')
        fig_torta_pry.update_layout(
            paper_bgcolor='white',
            plot_bgcolor='white',
            font=dict(color='#1f2937')
        )
        st.plotly_chart(fig_torta_pry, width="stretch")

    st.divider()
    st.subheader("📄 Reporte del Dashboard")
    try:
        dashboard_pdf = dashboard_to_pdf_bytes(
            st.session_state.df_nc,
            st.session_state.df_qyr,
            st.session_state.df_om,
            fig_pie,
            fig_m,
            fig_qyr,
            fig_gantt,
            fig_torta_pry
        )
        st.download_button(
            label="📄 Descargar Dashboard en PDF",
            data=dashboard_pdf,
            file_name=f"Dashboard_SGC_{date.today()}.pdf",
            mime="application/pdf"
        )
    except Exception:
        st.warning("No se pudo generar el PDF del Dashboard en esta ejecución. El tablero y el Gantt siguen disponibles en pantalla.")

# --- B. GESTIÓN DE NC (CON 5 PORQUÉS) ---
elif seleccion == "Gestión de NC":
    st.header("📝 Análisis de No Conformidad")
    with st.form("form_nc_completo"):
        c1, c2, c3 = st.columns(3)
        with c1:
            id_nc = st.text_input("Código NC", value=f"NC-2026-N{len(st.session_state.df_nc)+1}")
            origen = st.selectbox("Origen", ["Auditoria Interna", "Observaciones Internas", "Externa"])
        with c2:
            tipo = st.selectbox("Tipo de NC", ["Proceso", "Producto", "Logística", "Sistema"])
            sector = st.selectbox("Sector Afectado", ["Producción", "Comercial", "Logística", "Administración"])
        with c3:
            grav = st.selectbox("Gravedad", ["Crítica", "Mayor", "Menor"])
            ries = st.selectbox("Probabilidad (Riesgo)", ["Alta", "Media", "Baja"])

        fecha_nc = st.date_input("Fecha de Ingreso", value=date.today(), key="fecha_in_nc")
        
        st.divider()
        st.subheader("🔍 Análisis de Causa Raíz (5 Porqués)")
        p1 = st.text_input("1. ¿Por qué ocurre?")
        p2 = st.text_input("2. ¿Por qué?")
        p3 = st.text_input("3. ¿Por qué?")
        p4 = st.text_input("4. ¿Por qué?")
        p5 = st.text_input("5. ¿Por qué? (Causa Raíz)")
        
        acciones = st.text_area("Acciones Correctivas")
        st.divider()
        st.subheader("📁 Asociación a Proyecto")
        proyectos_disponibles_nc = ['Sin asociar'] + st.session_state.df_proyectos['id'].astype(str).tolist()
        proyecto_existente_nc = st.selectbox("Proyecto existente", proyectos_disponibles_nc, key="nc_proyecto_existente")
        crear_proyecto_desde_nc = st.checkbox("Crear un nuevo proyecto a partir de esta NC", key="nc_crear_proyecto")
        datos_proyecto_nc = None
        if crear_proyecto_desde_nc:
            datos_proyecto_nc = capturar_datos_proyecto(
                "nc_proyecto",
                nombre_default=f"Plan de acción {id_nc}",
                fecha_inicio_default=fecha_nc,
                estado_default="Por hacer"
            )
        
        if st.form_submit_button("💾 Guardar y Actualizar Matriz"):
            errores = []
            proyecto_asociado_nc = "" if proyecto_existente_nc == 'Sin asociar' else proyecto_existente_nc

            if crear_proyecto_desde_nc:
                if not datos_proyecto_nc['nombre'].strip():
                    errores.append("Ingresá un nombre para el proyecto asociado a la NC.")
                if not str(datos_proyecto_nc['responsable']).strip():
                    errores.append("Ingresá un responsable para el proyecto asociado a la NC.")

            if errores:
                for error in errores:
                    st.error(error)
            else:
                if crear_proyecto_desde_nc:
                    proyecto_asociado_nc = crear_proyecto(
                        datos_proyecto_nc['nombre'],
                        datos_proyecto_nc['prioridad'],
                        datos_proyecto_nc['area'],
                        datos_proyecto_nc['proveedor'],
                        datos_proyecto_nc['fecha_inicio'],
                        datos_proyecto_nc['dias_ejecucion'],
                        datos_proyecto_nc['responsable'],
                        datos_proyecto_nc['estado'],
                        datos_proyecto_nc['seguimiento'],
                        'No Conformidad',
                        id_nc
                    )

                new_nc = {
                    'id': id_nc,
                    'tipo': tipo,
                    'gravedad': grav,
                    'riesgo': ries,
                    'estado': 'Abierta',
                    'sector': sector,
                    'fecha_in': fecha_nc,
                    'proyecto_asociado': proyecto_asociado_nc,
                }
                st.session_state.df_nc = pd.concat([st.session_state.df_nc, pd.DataFrame([new_nc])], ignore_index=True)
                guardar_datos_persistentes()
                st.success("NC registrada correctamente.")
                st.balloons()

    st.divider()
    st.subheader("🔎 Consulta de No Conformidades")
    c1, c2, c3 = st.columns(3)
    with c1:
        texto_nc = st.text_input("Buscar por Código o Sector", key="q_nc_texto")
    with c2:
        estados_nc = st.multiselect(
            "Filtrar por Estado",
            sorted(st.session_state.df_nc['estado'].dropna().unique()),
            key="q_nc_estado"
        )
    with c3:
        tipos_nc = st.multiselect(
            "Filtrar por Tipo",
            sorted(st.session_state.df_nc['tipo'].dropna().unique()),
            key="q_nc_tipo"
        )

    fechas_nc = pd.to_datetime(st.session_state.df_nc.get('fecha_in'), errors='coerce').dropna()
    if not fechas_nc.empty:
        fecha_min_nc = fechas_nc.min().date()
        fecha_max_nc = fechas_nc.max().date()
    else:
        fecha_min_nc = date.today()
        fecha_max_nc = date.today()

    st.caption("Rango de Fecha de Ingreso")
    c4, c5 = st.columns(2)
    with c4:
        fecha_desde_nc = st.date_input(
            "Fecha ingreso desde",
            value=fecha_min_nc,
            min_value=fecha_min_nc,
            max_value=fecha_max_nc,
            key="q_nc_fecha_desde"
        )
    with c5:
        fecha_hasta_nc = st.date_input(
            "Fecha ingreso hasta",
            value=fecha_max_nc,
            min_value=fecha_min_nc,
            max_value=fecha_max_nc,
            key="q_nc_fecha_hasta"
        )

    df_nc_consulta = filtrar_texto(st.session_state.df_nc.copy(), ['id', 'sector'], texto_nc)
    if estados_nc:
        df_nc_consulta = df_nc_consulta[df_nc_consulta['estado'].isin(estados_nc)]
    if tipos_nc:
        df_nc_consulta = df_nc_consulta[df_nc_consulta['tipo'].isin(tipos_nc)]
    if 'fecha_in' in df_nc_consulta.columns:
        fechas_consulta_nc = pd.to_datetime(df_nc_consulta['fecha_in'], errors='coerce')
        df_nc_consulta = df_nc_consulta[
            (fechas_consulta_nc >= pd.to_datetime(fecha_desde_nc)) &
            (fechas_consulta_nc <= pd.to_datetime(fecha_hasta_nc))
        ]

    st.caption(f"Resultados: {len(df_nc_consulta)}")
    st.dataframe(df_nc_consulta, width="stretch", hide_index=True)
    cbtn1, cbtn2 = st.columns([1, 2])
    with cbtn1:
        st.button("🧹 Limpiar filtros", on_click=limpiar_filtros_nc)
    with cbtn2:
        st.download_button(
            label="📥 Exportar consulta NC",
            data=to_excel_single(df_nc_consulta, "Consulta NC"),
            file_name=f"Consulta_NC_{date.today()}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    st.divider()
    st.subheader("🖨️ Impresión y PDF")
    st.download_button(
        label="📄 Descargar consulta NC en PDF",
        data=dataframe_to_pdf_bytes("Consulta de No Conformidades", f"Generado: {date.today()}", df_nc_consulta),
        file_name=f"Consulta_NC_{date.today()}.pdf",
        mime="application/pdf"
    )
    render_print_section("Consulta de No Conformidades", df_nc_consulta, "consulta_nc")

# --- C. QUEJAS Y RECLAMOS ---
elif seleccion == "Quejas y Reclamos":
    st.header("📢 Registro de Reclamos (Foco Cliente)")
    with st.form("form_qyr"):
        c1, c2 = st.columns(2)
        with c1:
            clie = st.text_input("Cliente", placeholder="Ej: Fedea S.A")
            prod = st.text_input("Producto", placeholder="Ej: Fedea-1.2% - Adaptación")
            modo = st.selectbox("Modo", ["Telefonicamente", "Email", "WhatsApp"])
        with c2:
            sect = st.selectbox("Sector Responsable", ["Logistica", "Comercial", "Producto", "Manejo"])
            f_in = st.date_input("Fecha Inicio")
            f_ci = st.date_input("Fecha Cierre Estimada")
        
        motivo = st.text_area("Motivo del Reclamo (Detalle de Estibado/Transporte)")
        
        if st.form_submit_button("💾 Registrar Reclamo"):
            d_res = (f_ci - f_in).days
            new_q = {'id': f'QYR-{len(st.session_state.df_qyr)+1}', 'cliente': clie, 'producto': prod, 
                     'sector': sect, 'estado': 'Abierto', 'dias_res': d_res, 'fecha_in': f_in}
            st.session_state.df_qyr = pd.concat([st.session_state.df_qyr, pd.DataFrame([new_q])], ignore_index=True)
            guardar_datos_persistentes()
            st.success("Reclamo registrado correctamente.")
            st.balloons()

    st.divider()
    st.subheader("🔎 Consulta de Quejas y Reclamos")
    c1, c2, c3 = st.columns(3)
    with c1:
        texto_qyr = st.text_input("Buscar por ID, Cliente o Producto", key="q_qyr_texto")
    with c2:
        sectores_qyr = st.multiselect(
            "Filtrar por Sector",
            sorted(st.session_state.df_qyr['sector'].dropna().unique()),
            key="q_qyr_sector"
        )
    with c3:
        estados_qyr = st.multiselect(
            "Filtrar por Estado",
            sorted(st.session_state.df_qyr['estado'].dropna().unique()),
            key="q_qyr_estado"
        )

    fechas_qyr = pd.to_datetime(st.session_state.df_qyr['fecha_in'], errors='coerce').dropna()
    if not fechas_qyr.empty:
        fecha_min = fechas_qyr.min().date()
        fecha_max = fechas_qyr.max().date()
    else:
        fecha_min = date.today()
        fecha_max = date.today()

    st.caption("Rango de Fecha de Ingreso")
    c4, c5 = st.columns(2)
    with c4:
        fecha_desde = st.date_input(
            "Fecha ingreso desde",
            value=fecha_min,
            min_value=fecha_min,
            max_value=fecha_max,
            key="q_qyr_fecha_desde"
        )
    with c5:
        fecha_hasta = st.date_input(
            "Fecha ingreso hasta",
            value=fecha_max,
            min_value=fecha_min,
            max_value=fecha_max,
            key="q_qyr_fecha_hasta"
        )

    df_qyr_consulta = filtrar_texto(st.session_state.df_qyr.copy(), ['id', 'cliente', 'producto'], texto_qyr)
    if sectores_qyr:
        df_qyr_consulta = df_qyr_consulta[df_qyr_consulta['sector'].isin(sectores_qyr)]
    if estados_qyr:
        df_qyr_consulta = df_qyr_consulta[df_qyr_consulta['estado'].isin(estados_qyr)]

    if 'fecha_in' in df_qyr_consulta.columns:
        fechas_consulta = pd.to_datetime(df_qyr_consulta['fecha_in'], errors='coerce')
        df_qyr_consulta = df_qyr_consulta[
            (fechas_consulta >= pd.to_datetime(fecha_desde)) &
            (fechas_consulta <= pd.to_datetime(fecha_hasta))
        ]

    st.caption(f"Resultados: {len(df_qyr_consulta)}")
    st.dataframe(df_qyr_consulta, width="stretch", hide_index=True)
    cbtn1, cbtn2 = st.columns([1, 2])
    with cbtn1:
        st.button("🧹 Limpiar filtros", on_click=limpiar_filtros_qyr)
    with cbtn2:
        st.download_button(
            label="📥 Exportar consulta QyR",
            data=to_excel_single(df_qyr_consulta, "Consulta QyR"),
            file_name=f"Consulta_QyR_{date.today()}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    st.divider()
    st.subheader("🖨️ Impresión y PDF")
    st.download_button(
        label="📄 Descargar consulta QyR en PDF",
        data=dataframe_to_pdf_bytes("Consulta de Quejas y Reclamos", f"Generado: {date.today()}", df_qyr_consulta),
        file_name=f"Consulta_QyR_{date.today()}.pdf",
        mime="application/pdf"
    )
    render_print_section("Consulta de Quejas y Reclamos", df_qyr_consulta, "consulta_qyr")

# --- D. OPORTUNIDAD DE MEJORA ---
elif seleccion == "Oportunidad de Mejora":
    st.header("💡 Registro de Oportunidades de Mejora")
    with st.form("form_om"):
        c1, c2 = st.columns(2)
        with c1:
            desc = st.text_area("Descripción de la oportunidad")
            sec = st.selectbox("Sector", ["Producción", "Comercial", "Logística", "Administración", "IT"])
        with c2:
            resp = selector_responsable("Responsable", "om", default_value="Tercero Kanofer")
            est = st.selectbox("Estado", ["Nuevo", "En Implementación", "Cerrado"])

        fecha_om = st.date_input("Fecha de Ingreso", value=date.today(), key="fecha_in_om")
        st.divider()
        st.subheader("📁 Asociación a Proyecto")
        proyectos_disponibles_om = ['Sin asociar'] + st.session_state.df_proyectos['id'].astype(str).tolist()
        proyecto_existente_om = st.selectbox("Proyecto existente", proyectos_disponibles_om, key="om_proyecto_existente")
        crear_proyecto_desde_om = st.checkbox("Crear un nuevo proyecto a partir de esta oportunidad", key="om_crear_proyecto")
        datos_proyecto_om = None
        if crear_proyecto_desde_om:
            datos_proyecto_om = capturar_datos_proyecto(
                "om_proyecto",
                nombre_default=f"Implementación {sec}",
                responsable_default=resp,
                fecha_inicio_default=fecha_om,
                estado_default="Por hacer"
            )

        if st.form_submit_button("💾 Registrar Oportunidad"):
            errores = []
            proyecto_asociado_om = "" if proyecto_existente_om == 'Sin asociar' else proyecto_existente_om
            om_id = f'OM-2026-N{len(st.session_state.df_om)+1}'

            if not str(resp).strip():
                errores.append("Ingresá un responsable para la oportunidad de mejora.")
            if crear_proyecto_desde_om:
                if not datos_proyecto_om['nombre'].strip():
                    errores.append("Ingresá un nombre para el proyecto asociado a la oportunidad.")
                if not str(datos_proyecto_om['responsable']).strip():
                    errores.append("Ingresá un responsable para el proyecto asociado a la oportunidad.")

            if errores:
                for error in errores:
                    st.error(error)
            else:
                registrar_responsable(resp)
                if crear_proyecto_desde_om:
                    proyecto_asociado_om = crear_proyecto(
                        datos_proyecto_om['nombre'],
                        datos_proyecto_om['prioridad'],
                        datos_proyecto_om['area'],
                        datos_proyecto_om['proveedor'],
                        datos_proyecto_om['fecha_inicio'],
                        datos_proyecto_om['dias_ejecucion'],
                        datos_proyecto_om['responsable'],
                        datos_proyecto_om['estado'],
                        datos_proyecto_om['seguimiento'],
                        'Oportunidad de Mejora',
                        om_id
                    )

                new_om = {
                    'id': om_id,
                    'sector': sec,
                    'oportunidad': desc,
                    'estado': est,
                    'responsable': resp,
                    'fecha_in': fecha_om,
                    'proyecto_asociado': proyecto_asociado_om,
                }
                st.session_state.df_om = pd.concat([st.session_state.df_om, pd.DataFrame([new_om])], ignore_index=True)
                guardar_datos_persistentes()
                st.success("Oportunidad registrada correctamente.")

    st.divider()
    st.subheader("🔎 Consulta de Oportunidades de Mejora")
    c1, c2, c3 = st.columns(3)
    with c1:
        texto_om = st.text_input("Buscar por ID, Oportunidad o Responsable", key="q_om_texto")
    with c2:
        sectores_om = st.multiselect(
            "Filtrar por Sector",
            sorted(st.session_state.df_om['sector'].dropna().unique()),
            key="q_om_sector"
        )
    with c3:
        estados_om = st.multiselect(
            "Filtrar por Estado",
            sorted(st.session_state.df_om['estado'].dropna().unique()),
            key="q_om_estado"
        )

    fechas_om = pd.to_datetime(st.session_state.df_om.get('fecha_in'), errors='coerce').dropna()
    if not fechas_om.empty:
        fecha_min_om = fechas_om.min().date()
        fecha_max_om = fechas_om.max().date()
    else:
        fecha_min_om = date.today()
        fecha_max_om = date.today()

    st.caption("Rango de Fecha de Ingreso")
    c4, c5 = st.columns(2)
    with c4:
        fecha_desde_om = st.date_input(
            "Fecha ingreso desde",
            value=fecha_min_om,
            min_value=fecha_min_om,
            max_value=fecha_max_om,
            key="q_om_fecha_desde"
        )
    with c5:
        fecha_hasta_om = st.date_input(
            "Fecha ingreso hasta",
            value=fecha_max_om,
            min_value=fecha_min_om,
            max_value=fecha_max_om,
            key="q_om_fecha_hasta"
        )

    df_om_consulta = filtrar_texto(st.session_state.df_om.copy(), ['id', 'oportunidad', 'responsable'], texto_om)
    if sectores_om:
        df_om_consulta = df_om_consulta[df_om_consulta['sector'].isin(sectores_om)]
    if estados_om:
        df_om_consulta = df_om_consulta[df_om_consulta['estado'].isin(estados_om)]
    if 'fecha_in' in df_om_consulta.columns:
        fechas_consulta_om = pd.to_datetime(df_om_consulta['fecha_in'], errors='coerce')
        df_om_consulta = df_om_consulta[
            (fechas_consulta_om >= pd.to_datetime(fecha_desde_om)) &
            (fechas_consulta_om <= pd.to_datetime(fecha_hasta_om))
        ]

    st.caption(f"Resultados: {len(df_om_consulta)}")
    st.dataframe(df_om_consulta, width="stretch", hide_index=True)
    cbtn1, cbtn2 = st.columns([1, 2])
    with cbtn1:
        st.button("🧹 Limpiar filtros", on_click=limpiar_filtros_om)
    with cbtn2:
        st.download_button(
            label="📥 Exportar consulta OM",
            data=to_excel_single(df_om_consulta, "Consulta OM"),
            file_name=f"Consulta_OM_{date.today()}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    st.divider()
    st.subheader("🖨️ Impresión y PDF")
    st.download_button(
        label="📄 Descargar consulta OM en PDF",
        data=dataframe_to_pdf_bytes("Consulta de Oportunidades de Mejora", f"Generado: {date.today()}", df_om_consulta),
        file_name=f"Consulta_OM_{date.today()}.pdf",
        mime="application/pdf"
    )
    render_print_section("Consulta de Oportunidades de Mejora", df_om_consulta, "consulta_om")

# --- E. PROYECTOS ---
elif seleccion == "Proyectos":
    st.header("📁 Gestión de Proyectos")
    with st.form("form_proyectos"):
        datos_proyecto = capturar_datos_proyecto(
            "proyecto_independiente",
            nombre_default=f"Proyecto {len(st.session_state.df_proyectos) + 1}",
            estado_default="Por hacer"
        )

        if st.form_submit_button("💾 Registrar Proyecto"):
            errores = []
            if not datos_proyecto['nombre'].strip():
                errores.append("Ingresá un nombre para el proyecto.")
            if not str(datos_proyecto['responsable']).strip():
                errores.append("Ingresá un responsable para el proyecto.")

            if errores:
                for error in errores:
                    st.error(error)
            else:
                proyecto_id = crear_proyecto(
                    datos_proyecto['nombre'],
                    datos_proyecto['prioridad'],
                    datos_proyecto['area'],
                    datos_proyecto['proveedor'],
                    datos_proyecto['fecha_inicio'],
                    datos_proyecto['dias_ejecucion'],
                    datos_proyecto['responsable'],
                    datos_proyecto['estado'],
                    datos_proyecto['seguimiento'],
                    'Independiente',
                    ''
                )
                st.success(f"Proyecto {proyecto_id} registrado correctamente.")
                st.balloons()

    st.divider()
    st.subheader("🔎 Consulta de Proyectos")
    c1, c2, c3 = st.columns(3)
    with c1:
        texto_pry = st.text_input("Buscar por ID, nombre, proveedor o responsable", key="q_pry_texto")
    with c2:
        estados_pry = st.multiselect(
            "Filtrar por Estado",
            sorted(st.session_state.df_proyectos['estado'].dropna().unique()),
            key="q_pry_estado"
        )
    with c3:
        prioridades_pry = st.multiselect(
            "Filtrar por Prioridad",
            sorted(st.session_state.df_proyectos['prioridad'].dropna().unique()),
            key="q_pry_prioridad"
        )
    areas_pry = st.multiselect(
        "Filtrar por Área",
        sorted(st.session_state.df_proyectos['area'].dropna().unique()),
        key="q_pry_area"
    )

    fechas_pry = pd.to_datetime(st.session_state.df_proyectos.get('fecha_inicio'), errors='coerce').dropna()
    if not fechas_pry.empty:
        fecha_min_pry = fechas_pry.min().date()
        fecha_max_pry = fechas_pry.max().date()
    else:
        fecha_min_pry = date.today()
        fecha_max_pry = date.today()

    st.caption("Rango de Fecha de Inicio")
    c4, c5 = st.columns(2)
    with c4:
        fecha_desde_pry = st.date_input(
            "Fecha inicio desde",
            value=fecha_min_pry,
            min_value=fecha_min_pry,
            max_value=fecha_max_pry,
            key="q_pry_fecha_desde"
        )
    with c5:
        fecha_hasta_pry = st.date_input(
            "Fecha inicio hasta",
            value=fecha_max_pry,
            min_value=fecha_min_pry,
            max_value=fecha_max_pry,
            key="q_pry_fecha_hasta"
        )

    df_proyectos_consulta = filtrar_texto(
        st.session_state.df_proyectos.copy(),
        ['id', 'nombre', 'area', 'proveedor', 'responsable', 'origen_id'],
        texto_pry
    )
    if estados_pry:
        df_proyectos_consulta = df_proyectos_consulta[df_proyectos_consulta['estado'].isin(estados_pry)]
    if prioridades_pry:
        df_proyectos_consulta = df_proyectos_consulta[df_proyectos_consulta['prioridad'].isin(prioridades_pry)]
    if areas_pry:
        df_proyectos_consulta = df_proyectos_consulta[df_proyectos_consulta['area'].isin(areas_pry)]
    if 'fecha_inicio' in df_proyectos_consulta.columns:
        fechas_consulta_pry = pd.to_datetime(df_proyectos_consulta['fecha_inicio'], errors='coerce')
        df_proyectos_consulta = df_proyectos_consulta[
            (fechas_consulta_pry >= pd.to_datetime(fecha_desde_pry)) &
            (fechas_consulta_pry <= pd.to_datetime(fecha_hasta_pry))
        ]

    st.caption(f"Resultados: {len(df_proyectos_consulta)}")
    st.dataframe(df_proyectos_consulta, width="stretch", hide_index=True)
    cbtn1, cbtn2 = st.columns([1, 2])
    with cbtn1:
        st.button("🧹 Limpiar filtros", on_click=limpiar_filtros_proyectos)
    with cbtn2:
        st.download_button(
            label="📥 Exportar consulta Proyectos",
            data=to_excel_single(df_proyectos_consulta, "Consulta Proyectos"),
            file_name=f"Consulta_Proyectos_{date.today()}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    st.divider()
    st.subheader("✏️ Edición y eliminación")
    if st.session_state.df_proyectos.empty:
        st.info("No hay proyectos para editar o eliminar.")
    else:
        proyecto_admin_id = st.selectbox(
            "Seleccionar proyecto para administrar",
            st.session_state.df_proyectos['id'].tolist(),
            key="proyecto_admin_id"
        )
        proyecto_admin = st.session_state.df_proyectos[
            st.session_state.df_proyectos['id'] == proyecto_admin_id
        ].iloc[0]

        with st.form("form_editar_proyecto"):
            datos_edicion = capturar_datos_proyecto(
                "proyecto_edicion",
                nombre_default=str(proyecto_admin['nombre']),
                responsable_default=str(proyecto_admin['responsable']),
                fecha_inicio_default=pd.to_datetime(proyecto_admin['fecha_inicio'], errors='coerce').date() if pd.notna(proyecto_admin['fecha_inicio']) else date.today(),
                estado_default=str(proyecto_admin['estado']),
                prioridad_default=str(proyecto_admin['prioridad']),
                area_default=str(proyecto_admin['area']) if pd.notna(proyecto_admin['area']) else "Producción",
                proveedor_default=str(proyecto_admin['proveedor']),
                dias_ejecucion_default=int(proyecto_admin['dias_ejecucion']) if pd.notna(proyecto_admin['dias_ejecucion']) else 30,
                seguimiento_default=str(proyecto_admin['seguimiento']) if pd.notna(proyecto_admin['seguimiento']) else ""
            )
            guardar_edicion = st.form_submit_button("💾 Guardar cambios")

            if guardar_edicion:
                if not datos_edicion['nombre'].strip() or not str(datos_edicion['responsable']).strip():
                    st.error("Nombre y responsable son obligatorios para guardar cambios.")
                else:
                    registrar_responsable(datos_edicion['responsable'])
                    ok = actualizar_proyecto(
                        proyecto_admin_id,
                        {
                            'nombre': datos_edicion['nombre'],
                            'prioridad': datos_edicion['prioridad'],
                            'area': datos_edicion['area'],
                            'proveedor': datos_edicion['proveedor'],
                            'fecha_inicio': datos_edicion['fecha_inicio'],
                            'dias_ejecucion': int(datos_edicion['dias_ejecucion']),
                            'fecha_fin': datos_edicion['fecha_fin'],
                            'responsable': datos_edicion['responsable'],
                            'estado': datos_edicion['estado'],
                            'seguimiento': datos_edicion['seguimiento'],
                        }
                    )
                    if ok:
                        st.success(f"Proyecto {proyecto_admin_id} actualizado.")

        confirmar_eliminar = st.checkbox("Confirmar eliminación del proyecto seleccionado", key="confirmar_eliminar_proyecto")
        if st.button("🗑️ Eliminar proyecto", type="secondary", disabled=not confirmar_eliminar):
            eliminar_proyecto(proyecto_admin_id)
            st.success(f"Proyecto {proyecto_admin_id} eliminado.")

    st.divider()
    st.subheader("✅ Seguimiento")
    if df_proyectos_consulta.empty:
        st.info("No hay proyectos para mostrar en el seguimiento.")
    else:
        proyecto_detalle_id = st.selectbox(
            "Seleccionar proyecto para ver el checklist",
            df_proyectos_consulta['id'].tolist(),
            key="proyecto_detalle"
        )
        proyecto_detalle = df_proyectos_consulta[df_proyectos_consulta['id'] == proyecto_detalle_id].iloc[0]
        m1, m2, m3 = st.columns(3)
        m1.metric("Estado", proyecto_detalle['estado'])
        m2.metric("Fecha final", str(proyecto_detalle['fecha_fin']))
        origen_texto = proyecto_detalle['origen_tipo']
        if str(proyecto_detalle['origen_id']).strip():
            origen_texto = f"{proyecto_detalle['origen_tipo']} - {proyecto_detalle['origen_id']}"
        m3.metric("Origen", origen_texto)
        st.write(f"**Responsable:** {proyecto_detalle['responsable']}")
        st.write(f"**Área:** {proyecto_detalle['area']}")
        st.write(f"**Proveedor:** {proyecto_detalle['proveedor']}")
        mostrar_checklist_seguimiento(proyecto_detalle['seguimiento'], f"seguimiento_{proyecto_detalle_id}")

    st.divider()
    st.subheader("🖨️ Impresión y PDF")
    st.download_button(
        label="📄 Descargar consulta Proyectos en PDF",
        data=dataframe_to_pdf_bytes("Consulta de Proyectos", f"Generado: {date.today()}", df_proyectos_consulta),
        file_name=f"Consulta_Proyectos_{date.today()}.pdf",
        mime="application/pdf"
    )
    render_print_section("Consulta de Proyectos", df_proyectos_consulta, "consulta_proyectos")