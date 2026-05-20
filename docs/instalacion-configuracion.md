# Guía de Instalación y Configuración

## Requisitos Previos

### Servidor

- **OS:** Linux (recomendado: Ubuntu 20.04 LTS o superior)
- **Python:** 3.10+
- **PostgreSQL:** 12+
- **Memoria:** 2GB mínimo (4GB recomendado)
- **Almacenamiento:** 20GB mínimo

### Acceso

- SSH acceso a servidor
- Acceso a base de datos PostgreSQL
- Dominio o dirección IP para acceso web
- Certificado SSL (opcional pero recomendado)

## Instalación Rápida (Docker)

La opción más fácil es usar Docker Compose.

### 1. Clonar el Repositorio

```bash
git clone https://github.com/dario-coronel/Gestion-Calidad.git
cd Gestion-Calidad
git checkout main  # o dev según tu necesidad
```

### 2. Configurar Variables de Entorno

```bash
cp .env.example .env
# Editar .env con tus valores
nano .env
```

Campos importantes:
```
DATABASE_URL=postgres://usuario:password@db:5432/calidad_db
SECRET_KEY=tu_clave_secreta_aqui
DEBUG=False
ALLOWED_HOSTS=tu-dominio.com,localhost
```

### 3. Iniciar Servicios

```bash
docker compose up -d
```

Esto inicia:
- **web** - Aplicación Django (puerto 8002)
- **db** - PostgreSQL (puerto 5432)

### 4. Crear Admin

```bash
docker compose exec web python manage.py createsuperuser
```

Sigue las instrucciones y crea tu cuenta admin.

### 5. Acceder

- **URL:** http://localhost:8002 (o tu dominio)
- **Admin:** http://localhost:8002/admin
- **Usuario:** El que creaste arriba

## Instalación Manual

Si prefieres instalar sin Docker.

### 1. Instalar Dependencias del Sistema

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3.11 python3.11-venv python3-pip postgresql postgresql-contrib
```

### 2. Clonar Repositorio

```bash
git clone https://github.com/dario-coronel/Gestion-Calidad.git
cd Gestion-Calidad
```

### 3. Crear Entorno Virtual

```bash
python3.11 -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

### 4. Instalar Dependencias Python

```bash
pip install -r requirements.txt
```

### 5. Configurar Base de Datos

```bash
# Crear usuario y BD en PostgreSQL
sudo -u postgres psql

CREATE USER usuario_calidad WITH PASSWORD 'tu_password';
CREATE DATABASE calidad_db OWNER usuario_calidad;
GRANT ALL PRIVILEGES ON DATABASE calidad_db TO usuario_calidad;
\q
```

### 6. Configurar Django

```bash
cp .env.example .env
# Editar .env
nano .env
```

### 7. Migrar Base de Datos

```bash
python manage.py migrate
```

### 8. Crear Super Usuario

```bash
python manage.py createsuperuser
```

### 9. Cargar Datos Iniciales (Opcional)

```bash
python manage.py loaddata data/datos_sgc.json
```

### 10. Recopilar Archivos Estáticos

```bash
python manage.py collectstatic
```

### 11. Ejecutar Servidor

**Desarrollo:**
```bash
python manage.py runserver 0.0.0.0:8000
```

**Producción:**
```bash
gunicorn sgc.wsgi:application --bind 0.0.0.0:8002
```

Accede a http://localhost:8002

## Configuración Inicial del Sistema

Una vez instalado, configura:

### 1. Crear Sectores

1. Ve a **Admin** → **Sectores**
2. Crea los sectores de tu empresa:
   - Producción
   - Calidad
   - Logística
   - Etc.

### 2. Agregar Usuarios

1. Ve a **Admin** → **Usuarios**
2. Crea usuarios para cada persona
3. Asigna roles:
   - **Administrador** - Acceso total
   - **Gerente** - Crear/editar reportes
   - **Operario** - Crear NC
   - **Auditor** - Auditorías

### 3. Crear Normas Base

1. Ve a **Admin** → **Normas**
2. Crea las normas principales:
   - ISO 9001:2015 (si aplica)
   - BPM (Buenas Prácticas)
   - Normativas locales
3. Agrega puntos para cada norma

### 4. Configurar Notificaciones (Opcional)

En `settings.py`:
```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'tu_servidor_email.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'tu_email@ejemplo.com'
EMAIL_HOST_PASSWORD = 'tu_password'
```

### 5. Backup Automático

Las copias de seguridad se realizan diariamente. Configura en:

```bash
# Editar crontab
crontab -e

# Agregar línea (ejemplo: 3 AM diariamente)
0 3 * * * /app/manage.py backup
```

## Actualización del Sistema

Para actualizar a la última versión:

### Con Docker

```bash
git pull origin main
docker compose down
docker compose build
docker compose up -d
docker compose exec web python manage.py migrate
```

### Manual

```bash
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
# Reiniciar gunicorn/servidor
```

## Solución de Problemas

### Error: "Connection refused" a la BD

```bash
# Verificar estado de PostgreSQL
sudo systemctl status postgresql

# Reiniciar si es necesario
sudo systemctl restart postgresql
```

### Error: "Static files not found"

```bash
python manage.py collectstatic --clear --noinput
```

### Error: "Module not found"

```bash
# Asegurate de estar en el entorno virtual
source venv/bin/activate

# Reinstala dependencias
pip install -r requirements.txt
```

### Acceso denegado a /admin

Crea un nuevo superusuario:
```bash
python manage.py createsuperuser
```

## Monitoreo y Mantenimiento

### Logs

Con Docker:
```bash
docker compose logs -f web
```

Manual:
```bash
tail -f /var/log/gunicorn/app.log
```

### Backup Manual

```bash
# Exportar BD
pg_dump -U usuario_calidad calidad_db > backup.sql

# Restaurar
psql -U usuario_calidad calidad_db < backup.sql
```

### Limpiar Datos Antiguos

```bash
python manage.py shell
>>> from django.utils import timezone
>>> from datetime import timedelta
>>> from apps.nc.models import NoConformidad
>>> old_date = timezone.now() - timedelta(days=730)
>>> NoConformidad.objects.filter(created_at__lt=old_date).delete()
```

## Seguridad

### Recomendaciones

- ✅ Cambiar `SECRET_KEY` en producción
- ✅ Usar `DEBUG = False`
- ✅ Configurar `ALLOWED_HOSTS`
- ✅ Usar HTTPS/SSL
- ✅ Realizar backups regularmente
- ✅ Actualizar dependencias periódicamente
- ✅ Usar contraseñas fuertes
- ✅ Limitar acceso a dirección IP

### Cambiar SECRET_KEY

```python
# Generar nueva clave
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# Actualizar en .env
SECRET_KEY=tu_nueva_clave_aqui
```

## Soporte

Si encuentras problemas:

1. **Consulta la documentación:** [Documentación Completa](./index.md)
2. **Revisa los logs:** `docker compose logs web`
3. **Contacta al equipo:** IT@edpagro.com.ar
4. **Abre un Issue:** GitHub Issues

---

[← Volver al inicio](./index.md)
