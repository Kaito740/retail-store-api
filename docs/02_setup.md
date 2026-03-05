# Instalación y Configuración

## Requisitos previos

- Python 3.10 o superior
- pip

## 1. Clonar el repositorio

```bash
git clone <url-del-repositorio>
cd retail-store-api
```

## 2. Crear y activar el entorno virtual

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux / macOS
source venv/bin/activate
```

## 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

## 4. Configurar variables de entorno

Copiar el archivo de ejemplo y completar los valores:

```bash
cp .env.example .env
```

Editar `.env` con los valores apropiados:

```env
# Clave secreta Django (generar con el comando indicado abajo)
SECRET_KEY=tu-clave-secreta-aqui

# True para desarrollo local, False para producción
DEBUG=True

# Hosts permitidos separados por comas
ALLOWED_HOSTS=localhost,127.0.0.1

# Orígenes CORS permitidos separados por comas
CORS_ALLOWED_ORIGINS=http://localhost:3000

# URL de base de datos (opcional en desarrollo - usa SQLite por defecto)
# DATABASE_URL=sqlite:///db.sqlite3
```

Para generar una `SECRET_KEY` segura:

```bash
python -c "import secrets; print(secrets.token_urlsafe(50))"
```

## 5. Aplicar migraciones

```bash
python manage.py migrate
```

## 6. Crear el superusuario

El superusuario es el administrador principal del sistema. Desde su cuenta se crean todos los empleados.

```bash
python manage.py createsuperuser
```

> **Nota:** Para plataformas sin acceso shell (ej: Render free tier), el proyecto incluye un comando personalizado `create_superuser` que lee las credenciales de variables de entorno. Ver sección de Despliegue.

## 7. Ejecutar el servidor de desarrollo

```bash
python manage.py runserver
```

La API estará disponible en `http://localhost:8000/api/v1/`.
El panel administrativo en `http://localhost:8000/admin/`.

---

## Ejecutar tests

```bash
pytest
```

Con reporte de cobertura:

```bash
pytest --cov=apps
```

---

## Variables de entorno — Referencia completa

| Variable | Requerida | Default | Descripción |
|---|---|---|---|
| `SECRET_KEY` | ✅ Sí | — | Clave secreta de Django. Lanza error si no está definida. |
| `DEBUG` | No | `False` | Activa el modo debug. Usar `True` solo en desarrollo. |
| `ALLOWED_HOSTS` | No | `''` | Hosts permitidos, separados por comas. |
| `CORS_ALLOWED_ORIGINS` | No | — | Orígenes permitidos para CORS, separados por comas. |
| `DATABASE_URL` | No | `sqlite:///db.sqlite3` | URL de conexión a la base de datos. |

---

## Despliegue en producción

### Proveedores compatibles

La aplicación es compatible con cualquier proveedor que soporte Python/Django:
- **Render**
- **Railway**
- **Heroku**
- **Fly.io**
- **VPS con Gunicorn**

### Configuración de base de datos

La aplicación usa `dj-database-url` para parsear la variable `DATABASE_URL`. Esto permite usar diferentes motores de base de datos:

| Motor | DATABASE_URL |
|---|---|
| SQLite | `sqlite:///db.sqlite3` |
| PostgreSQL | `postgresql://user:password@host:5432/dbname` |
| MySQL | `mysql://user:password@host:3306/dbname` |

### Pasos para desplegar

1. **Configurar variables de entorno** en el dashboard del proveedor:

   ```env
   SECRET_KEY=tu-clave-secreta-aqui
   DEBUG=False
   ALLOWED_HOSTS=tudominio.com,www.tudominio.com
   CORS_ALLOWED_ORIGINS=https://tuffrontend.com
   DATABASE_URL=postgresql://user:password@host:5432/dbname
   ```

2. **Ejecutar migraciones:**
   ```bash
   python manage.py migrate
   ```

3. **Recolectar archivos estáticos:**
   ```bash
   python manage.py collectstatic
   ```

4. **Iniciar Gunicorn:**
   ```bash
   gunicorn config.wsgi:application --bind 0.0.0.0:$PORT
   ```

   > En algunos proveedores (como Render), el comando Start puede configurarse directamente en el dashboard.

### Configuración de archivos estáticos

La aplicación usa **WhiteNoise** para servir archivos estáticos en producción. La configuración en `settings.py` incluye:

```python
STATIC_ROOT = BASE_DIR / "staticfiles"

STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}
```

Esto permite que `python manage.py collectstatic` funcione correctamente sin necesidad de un servidor web adicional para servir estáticos.

### Archivos sensibles

**Nunca** agregar el archivo `.env` al repositorio. El `.gitignore` ya incluye esta regla. Usa las variables de entorno del proveedor de hosting para configurar secrets.

---

## Despliegue en plataformas sin acceso shell (Render free tier)

El plan gratuito de **Render** y otras plataformas no incluyen acceso shell, por lo que no se puede ejecutar `createsuperuser` de forma interactiva. El proyecto incluye un comando personalizado para解决这个问题.

### Comando personalizado

El comando `create_superuser` (ubicado en `apps/users/management/commands/`) lee las credenciales de variables de entorno:

```bash
python manage.py create_superuser --username admin --email admin@email.com --password tuPassword123
```

O simplemente configurando las variables de entorno:
- `DJANGO_SUPERUSER_USERNAME`
- `DJANGO_SUPERUSER_EMAIL`
- `DJANGO_SUPERUSER_PASSWORD`

El comando es **idempotente**: si el superusuario ya existe, no crea otro.

### Configuración en Render

1. **Environment Variables:**

| Variable | Ejemplo |
|----------|---------|
| `DJANGO_SUPERUSER_USERNAME` | `admin` |
| `DJANGO_SUPERUSER_EMAIL` | `admin@tuemail.com` |
| `DJANGO_SUPERUSER_PASSWORD` | `tuPassword123` |
| `DATABASE_URL` | `postgresql://...` |
| `ALLOWED_HOSTS` | `tu-proyecto.onrender.com` |

2. **Build Command:**

```bash
pip install -r requirements.txt && python manage.py migrate && python manage.py create_superuser && python manage.py collectstatic --no-input
```

3. **Start Command:**

```bash
gunicorn config.wsgi:application --bind 0.0.0.0:$PORT
```
