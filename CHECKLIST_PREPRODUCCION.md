# Checklist Pre-Producción — SGC EDP Agroindustrial
> Fecha: Abril 2026 | Branch: `dev` → `main` | Responsable: Dario Coronel

---

## 1. Entorno y Dependencias

- [ ] Python 3.12 instalado en servidor de producción
- [ ] Virtualenv creado y activado (`python -m venv venv`)
- [ ] Dependencias instaladas (`pip install -r requirements.txt`)
- [ ] Verificar versiones críticas:
  - `django==6.0.4`
  - `django-htmx==1.21.0`
  - `weasyprint==68.1`
  - `whitenoise==6.9.0`
  - `psycopg2-binary` (para PostgreSQL en prod)
- [ ] Archivo `.env` creado en raíz del proyecto (ver sección 2)

---

## 2. Variables de Entorno (`.env`)

Crear el archivo `.env` en producción con los siguientes valores:

```env
# Seguridad
SECRET_KEY=<clave-secreta-larga-y-aleatoria>
DEBUG=False
ALLOWED_HOSTS=<ip-servidor>,<nombre-host>

# Base de datos (PostgreSQL en producción)
DATABASE_URL=postgres://usuario:contraseña@localhost:5432/sgc_db

# Email (para notificaciones a clientes)
EMAIL_HOST=smtp.dominio.com
EMAIL_PORT=587
EMAIL_HOST_USER=notificaciones@edpagroindustrial.com
EMAIL_HOST_PASSWORD=<contraseña-smtp>
EMAIL_USE_TLS=True
DEFAULT_FROM_EMAIL=SGC EDP <notificaciones@edpagroindustrial.com>
```

> **CRÍTICO**: `SECRET_KEY` nunca debe ser el valor por defecto (`django-insecure-...`).
> Generarla con: `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`

---

## 3. Base de Datos

### 3.1 PostgreSQL
- [ ] PostgreSQL instalado y servicio activo
- [ ] Base de datos `sgc_db` creada
- [ ] Usuario con permisos sobre la base de datos
- [ ] Conexión verificada: `psql -U usuario -d sgc_db`

### 3.2 Migraciones
- [ ] `python manage.py migrate` — sin errores
- [ ] Verificar que todas las migraciones estén aplicadas:
  ```
  python manage.py showmigrations
  ```
  Confirmar que todas muestran `[X]` (aplicadas):
  - `core`: 0001_add_sector_fks, 0002_seed_sectores
  - `accounts`: 0001_initial
  - `nc`: 0001_initial, 0002_noconformidad_..., 0003_add_sector_fks
  - `qr`: 0001_initial, 0002_add_gestion_fields, 0003_add_sector_fks
  - `om`: 0001_initial, 0002_add_sector_fks
  - `proyectos`: 0001_initial, 0002_add_sector_and_origin_links, 0003_backfill_sector
  - `verificacion`: 0001_initial
  - `notificaciones`: 0001_initial

### 3.3 Datos iniciales
- [ ] 10 Sectores cargados (migración `core/0002_seed_sectores` los crea automáticamente):
  - Produccion Balanceado, Produccion Aceitera, Produccion Cluster, Acopio,
    Mantenimiento, Administracion, IT, Logistica, Comercial, Laboratorio
- [ ] Superusuario creado: `python manage.py createsuperuser`
- [ ] Al menos un usuario por rol: ADMIN, CALIDAD, OPERARIO, MANAGER

---

## 4. Archivos Estáticos y Multimedia

- [ ] `python manage.py collectstatic --noinput` — sin errores
- [ ] Directorio `staticfiles/` generado correctamente
- [ ] Directorio `media/` creado con permisos de escritura para el servidor web
- [ ] WhiteNoise configurado (ya está en `MIDDLEWARE` y `STORAGES`)

---

## 5. Seguridad

- [ ] `DEBUG=False` en producción
- [ ] `ALLOWED_HOSTS` contiene solo IPs/dominios del servidor interno
- [ ] `SECRET_KEY` es única y segura (no el valor de desarrollo)
- [ ] `python manage.py check --deploy` — revisar advertencias de seguridad
- [ ] HTTPS configurado si aplica (certificado SSL interno)
- [ ] Política de contraseñas activa (ya configurada en `AUTH_PASSWORD_VALIDATORS`)

---

## 6. Servidor Web (Ubuntu Linux)

### 6.1 Gunicorn
- [ ] Gunicorn instalado: `pip install gunicorn`
- [ ] Comando de prueba: `gunicorn sgc.wsgi:application --bind 0.0.0.0:8000`
- [ ] Servicio systemd creado para auto-inicio:

```ini
# /etc/systemd/system/sgc.service
[Unit]
Description=SGC EDP Agroindustrial
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/ruta/al/proyecto
ExecStart=/ruta/al/proyecto/venv/bin/gunicorn \
    --workers 3 \
    --bind 127.0.0.1:8000 \
    sgc.wsgi:application
Restart=always

[Install]
WantedBy=multi-user.target
```

- [ ] `systemctl enable sgc && systemctl start sgc`

### 6.2 Nginx (proxy inverso)
- [ ] Nginx instalado
- [ ] Configuración de virtual host:

```nginx
server {
    listen 80;
    server_name <ip-servidor>;

    location /static/ {
        alias /ruta/al/proyecto/staticfiles/;
    }

    location /media/ {
        alias /ruta/al/proyecto/media/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

- [ ] `nginx -t` — configuración válida
- [ ] `systemctl restart nginx`

---

## 7. Funcionalidad — Smoke Test Manual

### 7.1 Autenticación
- [ ] Login funciona con usuario ADMIN
- [ ] Login funciona con usuario CALIDAD
- [ ] Login funciona con usuario OPERARIO
- [ ] Login funciona con usuario MANAGER
- [ ] Logout redirige a `/accounts/login/`

### 7.2 Dashboard
- [ ] Dashboard carga sin errores
- [ ] Sidebar muestra menú según rol del usuario

### 7.3 No Conformidades (NC)
- [ ] Crear NC con todos los campos (incluye sector FK)
- [ ] Listar NCs con filtro por sector
- [ ] Ver detalle de NC
- [ ] Completar análisis 5 Porqués
- [ ] Adjuntar archivo (PDF o imagen)
- [ ] Marcar Eficacia: verificar que "No Eficaz" genera NC sucesora automáticamente
- [ ] Exportar PDF Resumen
- [ ] Exportar PDF Completo

### 7.4 Quejas y Reclamos (QR)
- [ ] Crear QR con sector FK y nuevos campos (quien_recibe, detalle_visita, etc.)
- [ ] Listar QRs
- [ ] Cambiar estado a CERRADO — verificar que `fecha_cierre` se completa automáticamente

### 7.5 Oportunidades de Mejora (OM)
- [ ] Crear OM con sector FK y nuevos campos
- [ ] Verificar que `fecha_evaluacion` se calcula automáticamente según `rango_evaluacion`
- [ ] Marcar Eficacia: verificar que "No Eficaz" genera OM sucesora automáticamente

### 7.6 Proyectos
- [ ] Crear proyecto desde NC (sector se propaga automáticamente)
- [ ] Crear proyecto desde OM (sector se propaga automáticamente)
- [ ] Crear proyecto manual con sector
- [ ] Agregar subtareas, cambiar estado

### 7.7 Verificación de Eficacia
- [ ] Ver lista de verificaciones pendientes
- [ ] Registrar resultado de verificación
- [ ] Verificar que resultado "No Eficaz" crea NC automáticamente
- [ ] Ver NC generada desde la verificación

### 7.8 Sectores (Admin/Calidad)
- [ ] Listar sectores en `/core/sectores/`
- [ ] Crear nuevo sector
- [ ] Editar sector
- [ ] Desactivar sector

### 7.9 Reportes
- [ ] Dashboard de reportes carga con KPIs
- [ ] Verificar conteos de NC abiertas, QR sin cerrar, OM en progreso, proyectos activos

### 7.10 Admin Django
- [ ] `/admin/` accesible con superusuario
- [ ] Todos los modelos visibles y editables

---

## 8. Email (Notificaciones)

- [ ] Configurar SMTP en `.env` (ver sección 2)
- [ ] Verificar envío de prueba:
  ```python
  python manage.py shell
  from django.core.mail import send_mail
  send_mail('Test SGC', 'Prueba OK', 'from@dominio.com', ['to@dominio.com'])
  ```
- [ ] Campo `notificar_cliente` en NC activa envío de email al cerrar
- [ ] Campo `envio_mail` en QR registra que se notificó al cliente
- [ ] Notificaciones de verificación próximas a vencer (configurado en `VERIFICACION_DIAS_AVISO=90`)

---

## 9. CI/CD y Git

- [ ] GitHub Actions pasando en verde (`dev` branch)
- [ ] PR de `dev` → `main` creado y revisado
- [ ] Code review completado
- [ ] Merge a `main` realizado
- [ ] Tag de versión creado: `git tag v1.0.0 && git push --tags`

---

## 10. Backup y Monitoreo

- [ ] Backup automático de base de datos configurado (cron + pg_dump)
- [ ] Logs de Gunicorn configurados (`--access-logfile`, `--error-logfile`)
- [ ] Logs de Nginx funcionando (`/var/log/nginx/`)
- [ ] Directorio `media/` incluido en plan de backup
- [ ] Contacto definido para soporte técnico en producción

---

## Estado del Proyecto al 26/04/2026

| Módulo | Tests | Estado |
|--------|-------|--------|
| accounts | ✅ | Listo |
| core (Sectores) | ✅ | Listo |
| NC | ✅ | Listo |
| QR | ✅ | Listo |
| OM | ✅ | Listo |
| Proyectos | ✅ | Listo |
| Verificación | ✅ | Listo |
| Reportes | ✅ | Listo |
| **Total** | **13/13 OK** | **Listo para QA** |

---

> Generado automáticamente el 26/04/2026. Actualizar al completar cada ítem.
