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

---

## Configuración para producción

Para producción se recomienda cambiar la base de datos de SQLite a PostgreSQL. La variable `DATABASE_URL` está preparada en `.env.example` pero la configuración actual en `settings.py` usa SQLite directamente. Para migrar a PostgreSQL se debe ajustar el bloque `DATABASES` en `settings.py` y asegurarse de que `psycopg2-binary` esté instalado (ya incluido en `requirements.txt`).

El servidor de producción recomendado es **Gunicorn** (ya incluido en dependencias):

```bash
gunicorn config.wsgi:application --bind 0.0.0.0:8000
```
