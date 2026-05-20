# Órdenes de Mejora (OM)

## ¿Qué es una Orden de Mejora?

Una **Orden de Mejora (OM)** es una acción correctiva derivada de una No Conformidad. Define qué se debe hacer, quién es responsable y cuándo debe completarse.

## Estados de una OM

- **Por Ejecutar** - Asignada pero no iniciada
- **En Ejecución** - Trabajo en progreso
- **Por Validar** - Completada, pendiente de aprobación
- **Validada** - Aprobada y cierre confirmado

## Crear una Orden de Mejora

### Opción 1: Desde una NC (Recomendado)
1. Abre una No Conformidad
2. Haz clic en **Crear Orden de Mejora**
3. Se pre-llenará automáticamente con datos de la NC
4. Modifica si es necesario y haz clic en **Crear**

### Opción 2: Crear manualmente
1. Ve a **Procesos** → **Órdenes de Mejora**
2. Haz clic en **+ Nueva OM**
3. Rellena:
   - **Descripción** - Qué acción se debe ejecutar
   - **Tipo** - Preventiva o Correctiva
   - **No Conformidad** - Vincula la NC (si existe)
   - **Responsable** - Quién ejecutará
   - **Fecha límite** - Cuándo debe completarse
   - **Prioridad** - Alta, Media, Baja
4. Haz clic en **Crear**

## Ver Detalles de una OM

1. Desde la lista, haz clic en el número de OM
2. Se mostrará:
   - Información completa
   - Estado actual
   - Historial de cambios
   - Responsable y fechas
   - Vinculación a NC

## Actualizar Estado

1. En la página de detalles, haz clic en **Editar Estado**
2. Cambia al siguiente estado:
   - **Por Ejecutar** → **En Ejecución** (cuando inicia el trabajo)
   - **En Ejecución** → **Por Validar** (cuando termina)
   - **Por Validar** → **Validada** (cuando se aprueba)
3. Agrega comentarios si es necesario
4. Haz clic en **Guardar**

## Flujo típico

```
Por Ejecutar → En Ejecución → Por Validar → Validada
```

## Seguimiento de OM

### Mis Órdenes Pendientes
1. Ve a tu perfil o dashboard
2. Verás un resumen de tus OM asignadas
3. Haz clic para actualizar estado

### Reporte de OM
1. Ve a **Reportes** → **Órdenes de Mejora**
2. Puedes filtrar por:
   - Estado
   - Responsable
   - Fecha límite
   - Prioridad
3. Descarga el reporte en PDF o Excel

## Cierre de Orden de Mejora

Para cerrar una OM:
1. Debe estar en estado "Por Validar"
2. Proporciona evidencia de cierre (adjuntos, comentarios)
3. El validador (supervisor) revisa y aprueba
4. Se cambia a "Validada"
5. Se vincula al cierre de la NC asociada

## Retrasos

Si una OM se atrasa:
- Se mostrará en rojo en la lista
- Puedes extender la fecha límite
- Se registra en el historial

---

[← Volver al inicio](./index.md)
