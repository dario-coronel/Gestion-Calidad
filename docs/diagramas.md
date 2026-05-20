# Diagramas de Flujo

## Flujo General de No Conformidades

```mermaid
flowchart TD
    A[Problema Detectado] --> B[Crear NC]
    B --> C[Asignar Investigador]
    C --> D[Investigar Causa Raíz]
    D --> E{¿Causa Identificada?}
    E -->|No| D
    E -->|Sí| F[Documentar Causa]
    F --> G[Crear Orden de Mejora]
    G --> H[Ejecutar Acciones]
    H --> I[Validar Solución]
    I --> J{¿Solución Efectiva?}
    J -->|No| H
    J -->|Sí| K[Cerrar NC]
    K --> L[Archivar]
    
    style A fill:#ff9999
    style K fill:#99ff99
    style L fill:#99ccff
```

## Flujo de Auditoría y Generación de NC

```mermaid
flowchart TD
    A[Programar Auditoría] --> B[Preparar Criterios]
    B --> C[Ejecutar Auditoría]
    C --> D[Registrar Hallazgos]
    D --> E{¿No Conformidad?}
    E -->|Sí| F[Crear NC Automática]
    E -->|No| G[Observación/Recomendación]
    F --> H[Asignar OM]
    G --> H
    H --> I[Reportar Resultados]
    I --> J[Seguimiento]
    
    style C fill:#fff9c4
    style F fill:#ff9999
    style G fill:#ffffcc
    style J fill:#b3e5fc
```

## Flujo de Proyecto de Mejora

```mermaid
flowchart TD
    A[Idea de Mejora] --> B[Crear Proyecto]
    B --> C[Definir Objetivos]
    C --> D[Desglosar en Subtareas]
    D --> E[Asignar Responsables]
    E --> F[Ejecutar Actividades]
    F --> G[Monitorear Progreso]
    G --> H{¿Completado?}
    H -->|No| F
    H -->|Sí| I[Validar Resultados]
    I --> J{¿Aprobado?}
    J -->|No| K[Revisar y Ajustar]
    K --> F
    J -->|Sí| L[Cerrar Proyecto]
    L --> M[Documentar Lecciones]
    
    style A fill:#c8e6c9
    style L fill:#99ff99
    style M fill:#b3e5fc
```

## Flujo de Órdenes de Mejora

```mermaid
flowchart TD
    A[Crear OM] --> B[Asignar Responsable]
    B --> C[Definir Plazo]
    C --> D{¿Urgencia?}
    D -->|Alta| E[Ejecutar Inmediato]
    D -->|Media/Baja| F[Planificar Ejecución]
    E --> G[Ejecutar Acciones]
    F --> G
    G --> H[Registrar Avance]
    H --> I{¿Completada?}
    I -->|No| G
    I -->|Sí| J[Solicitar Validación]
    J --> K[Validar Efectividad]
    K --> L{¿Aprobada?}
    L -->|No| M[Devolver para Ajustes]
    M --> G
    L -->|Sí| N[Cerrar OM]
    
    style A fill:#fff9c4
    style N fill:#99ff99
```

## Ciclo de Mejora Continua (PDCA)

```mermaid
graph TB
    P["PLAN<br/>Planificar<br/>¿Qué cambiar?"]
    D["DO<br/>Hacer<br/>Implementar cambio"]
    C["CHECK<br/>Verificar<br/>¿Funciona?"]
    A["ACT<br/>Actuar<br/>Estandarizar"]
    
    P --> D
    D --> C
    C --> A
    A --> P
    
    style P fill:#e3f2fd
    style D fill:#fff9c4
    style C fill:#f3e5f5
    style A fill:#c8e6c9
```

## Integración entre Módulos

```mermaid
graph TB
    NC["No Conformidades"]
    OM["Órdenes de Mejora"]
    NORMA["Normas y Puntos"]
    VERIF["Verificaciones"]
    PROY["Proyectos"]
    QR["QR/Trazabilidad"]
    REP["Reportes"]
    
    VERIF -->|Genera| NC
    NC -->|Genera| OM
    NC -->|Vinculada a| NORMA
    OM -->|Genera| PROY
    NC -->|Código QR| QR
    OM -->|Código QR| QR
    PROY -->|Datos para| REP
    OM -->|Datos para| REP
    NC -->|Datos para| REP
    VERIF -->|Datos para| REP
    
    style NC fill:#ffcccc
    style OM fill:#ffffcc
    style NORMA fill:#ccffcc
    style VERIF fill:#ccffff
    style PROY fill:#ffccff
    style QR fill:#ffdbac
    style REP fill:#e0e0e0
```

## Matriz de Trazabilidad

```mermaid
graph LR
    PRODUCTO["Producto/Lote"] -->|QR| ESPECIF["Especificación"]
    ESPECIF -->|Punto| NORMA["Norma"]
    NORMA -->|Verificado por| AUDIT["Auditoría"]
    AUDIT -->|Genera| NC["NC"]
    NC -->|Resuelta por| OM["OM"]
    PRODUCTO -->|Control| QR["Código QR"]
    QR -->|Enlaza a| NC
    QR -->|Enlaza a| AUDIT
    
    style PRODUCTO fill:#c8e6c9
    style QR fill:#ffdbac
    style NC fill:#ffcccc
    style OM fill:#ffffcc
    style AUDIT fill:#ccffff
```

---

[← Volver al inicio](./index.md)
