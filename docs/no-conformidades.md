# No Conformidades (NC)

## ¿Qué es una No Conformidad?

Una **No Conformidad (NC)** es un registro de un problema o incumplimiento detectado respecto a los estándares de calidad (normas).

Ejemplos:
- Un producto que no cumple especificación
- Incumplimiento de procedimiento
- Falta de documentación
- Desviación detectada en auditoría

## Estados de una NC

- **Abierta** - Recién reportada, pendiente de análisis
- **En Análisis** - Se está investigando la causa raíz
- **En Cierre** - Se implementó la solución, en validación
- **Cerrada** - Resuelta y verificada

## Crear una No Conformidad

1. Ve a **Gestión** → **No Conformidades**
2. Haz clic en **+ Nueva NC**
3. Rellena los campos:
   - **Título** - Resumen del problema
   - **Descripción** - Detalles completos
   - **Sector** - Área afectada (Producción, Calidad, etc.)
   - **Tipo** - Categoría (Proceso, Producto, Documentación, etc.)
   - **Fecha de detección** - Cuándo se descubrió
   - **Observaciones** - Notas adicionales
4. Haz clic en **Crear**

## Ver Detalles de una NC

1. Desde la lista, haz clic en el número de NC
2. Se abrirá la página de detalles mostrando:
   - Información completa
   - Causa raíz identificada
   - Acciones tomadas
   - Historial de cambios
   - Botón para crear Orden de Mejora (OM)

## Actualizar Estado

1. En la página de detalles de la NC, haz clic en **Editar**
2. Cambia el **Estado** al siguiente paso
3. Si aplica, agrega:
   - **Causa Raíz Identificada** - Por qué pasó
   - **Acciones Tomadas** - Qué se hizo
   - **Responsable** - Quién lidera la resolución
4. Haz clic en **Guardar**

## Vincular a Orden de Mejora

1. Abre la NC
2. Haz clic en **Crear Orden de Mejora**
3. Se generará una OM automáticamente vinculada a esta NC
4. Consulta [Órdenes de Mejora](./ordenes-mejora.md) para más detalles

## Flujo típico

```
Abierta → En Análisis → En Cierre → Cerrada
```

**Abierta a En Análisis:**
- Se asigna investigador
- Se identifica causa raíz

**En Análisis a En Cierre:**
- Se planifica la acción correctiva
- Se crea Orden de Mejora
- Se implementa la solución

**En Cierre a Cerrada:**
- Se verifica que la solución funciona
- Se valida el cierre
- Se archiva la NC

## Búsqueda y Filtros

En la lista de NC puedes:
- **Buscar** por número, título o sector
- **Filtrar** por estado, fecha, responsable
- **Ordenar** por columna (haciendo clic en el encabezado)

## Adjuntos

Cada NC puede tener archivos adjuntos (fotos, documentos, etc.):
- Haz clic en **Agregar Archivo**
- Selecciona el archivo desde tu computadora
- Se guardará junto a la NC

## Cierre de NC

Para cerrar una NC:
1. Todos los campos deben estar completos
2. Debe haber Orden de Mejora vinculada
3. El Estado debe ser "En Cierre"
4. Haz clic en **Cerrar NC**
5. Se pedirá confirmación final

---

[← Volver al inicio](./index.md)
