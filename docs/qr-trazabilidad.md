# Códigos QR y Trazabilidad

## ¿Qué es el Sistema QR?

El sistema de **Códigos QR** permite vincular aspectos del Sistema de Gestión de Calidad (NC, OM, Verificaciones) a códigos de barras que facilitan:

- **Trazabilidad** - Seguimiento de productos/lotes
- **Auditoría rápida** - Escanea para ver historial
- **Control de lotes** - Vinculación a documentación
- **Verificación ágil** - Acceso rápido a datos en planta

## Generar un Código QR

### Desde una No Conformidad

1. Abre la NC
2. Haz clic en **Generar QR**
3. Se crea automáticamente un código único
4. Opciones:
   - **Descargar** - Guarda como imagen PNG
   - **Imprimir** - Para etiquetas
   - **Copiar URL** - Para compartir por email

### Desde una Orden de Mejora

1. Abre la OM
2. Haz clic en **Generar QR**
3. El QR enlazará a la OM específica
4. Escánealo para acceder al estado/detalles

### Desde un Lote de Producto

1. Ve a **QR** → **Mi QR**
2. Haz clic en **+ Nuevo QR**
3. Rellena:
   - **Identificador** - Código de lote o SKU
   - **Descripción** - Qué es (producto, lote, etc.)
   - **Fecha de creación** - Cuándo se produjo
   - **Sector/Proveedor** - Origen
   - **Documentos asociados** - NC, OM, especificaciones
4. Haz clic en **Crear**

El sistema genera automáticamente el código QR.

## Escanear un Código QR

### Con Celular

1. Abre la app de cámara o lector QR
2. Apunta al código
3. Haz clic en el enlace que aparece
4. Se abrirá en el navegador mostrando:
   - Información del recurso (NC, OM, etc.)
   - Estado actual
   - Historial
   - Documentos adjuntos

### Desde Computadora

1. Ve a **QR** → **Escanear**
2. Usa la cámara web de tu computadora
3. O ingresa manualmente el código
4. Se abrirá la información

## Gestión de Códigos QR

### Listar mis QR

1. Ve a **QR** → **Mi QR**
2. Verás todos los códigos generados
3. Para cada código puedes:
   - **Ver** - Detalles y historial
   - **Editar** - Modificar datos
   - **Reasignar** - Cambiar documentos asociados
   - **Deshabilitar** - Dejar de usar (no se borra)

### Buscar un QR

1. Ve a **QR** → **Buscar**
2. Ingresa:
   - Identificador del QR
   - O código de lote
   - O número de NC/OM
3. Haz clic en **Buscar**
4. Se mostrará la información

## Vincular Documentos a QR

Cada código QR puede enlazar a:

- **No Conformidades (NC)** - Problema reportado
- **Órdenes de Mejora (OM)** - Acción correctiva
- **Especificaciones** - Archivo PDF con requisitos
- **Certificados** - Validación de normas
- **Auditorías** - Verificación realizada

### Agregar Vínculo

1. Abre el QR
2. Haz clic en **+ Agregar Vínculo**
3. Selecciona:
   - Tipo (NC, OM, Especificación, etc.)
   - El documento específico
4. Haz clic en **Guardar**

El código QR ahora incluirá este documento.

## Casos de Uso

### Caso 1: Trazabilidad de Lote

1. Produce un lote de producto
2. Crea QR con número de lote
3. Vincula especificación técnica
4. Imprime etiqueta con código
5. Cliente escanea para ver especificaciones

### Caso 2: Auditoría en Planta

1. Auditor encuentra un problema
2. Crea NC desde app móvil
3. Genera QR de la NC
4. Imprime y pega en el área
5. Otros empleados ven qué pasó escaneando

### Caso 3: Seguimiento de OM

1. Crea OM para corregir problema
2. Genera QR de la OM
3. Pega código en el área de trabajo
4. Equipo escanea para ver estado/tareas
5. Actualiza progreso directamente

## Estadísticas de QR

### Ver Uso de QR

1. Ve a **Reportes** → **QR**
2. Datos mostrados:
   - QR generados (total)
   - QR escaneados (total)
   - Escaneos por código
   - Tendencia de uso
   - Códigos más populares

### Analizar Patrones

Los datos ayudan a:
- Identificar problemas recurrentes
- Mejorar procesos
- Entender dónde se necesita más capacitación
- Validar efectividad de acciones

## Características Técnicas

### Información en el QR

Cada código contiene:
- URL única del sistema
- Token de seguridad
- ID del recurso vinculado

### Seguridad

- Los códigos expiran si se deshabilitan
- Solo usuarios autenticados ven detalles sensibles
- Se registra cada escaneo
- Auditoría completa disponible

### Compatibilidad

- Funciona con cualquier lector QR
- Compatible con iOS, Android, Windows
- No requiere app especial
- Acceso desde navegador automáticamente

## Tips

- Genera QR temprano en el proceso (durante creación de NC/OM)
- Imprime en tamaño visible (~5x5cm mínimo)
- Lamina códigos para durabilidad en planta
- Revisa estadísticas regularmente para mejorar procesos
- Vincula siempre especificaciones relevantes

---

[← Volver al inicio](./index.md)
