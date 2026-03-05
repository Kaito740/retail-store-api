# Retail Store API

REST API para la gestión de una tienda minorista local. Permite registrar ventas, administrar el inventario de productos y categorías, y gestionar clientes y empleados.

Construida con **Django 6** y **Django REST Framework**.

---

## Stack

- **Django 6.0.1** + **Django REST Framework 3.16.1**
- **Autenticación** por Token (DRF built-in)
- **Base de datos:** SQLite (desarrollo) / PostgreSQL (producción)
- **CORS:** django-cors-headers 4.9.0
- **Configuración DB:** dj-database-url 3.1.2
- **Static files:** WhiteNoise 6.11.0
- **Testing:** pytest 9.0.2 + pytest-django 4.12.0 + pytest-cov 5.0.0
- **Servidor de producción:** Gunicorn 25.1.0

---

## Instalación

### 1. Clonar el repositorio

```bash
git clone <url-del-repositorio>
cd retail-store-api
```

### 2. Crear entorno virtual e instalar dependencias

```bash
python -m venv venv

# Windows
venv\Scripts\activate
# Linux / macOS
source venv/bin/activate

pip install -r requirements.txt
```

### 3. Configurar variables de entorno

```bash
cp .env.example .env
```

Editar `.env`:

```env
SECRET_KEY=tu-clave-secreta-aqui   # python -c "import secrets; print(secrets.token_urlsafe(50))"
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:3000
```

### 4. Aplicar migraciones y crear superusuario

```bash
python manage.py migrate
python manage.py createsuperuser
```

### 5. Levantar el servidor

```bash
python manage.py runserver
```

API disponible en `http://localhost:8000/api/v1/`  
Panel admin en `http://localhost:8000/admin/`

---

## Tests

La suite de tests usa **pytest** con integración Django. Los tests verifican endpoints de API, validaciones y flujos de negocio.

```bash
# Ejecutar todos los tests
pytest

# Ver detalle
pytest -v

# Con cobertura
pytest --cov=apps
```

**Tests implementados (31 tests):**
- `tests/test_auth.py` - Login y logout
- `tests/test_users.py` - Clientes (CRUD, filtros, defaults)
- `tests/test_inventory.py` - Categorías y productos
- `tests/test_sales.py` - Ventas (crear, cancelar, filtros)

---

## Estructura del proyecto

```
retail-store-api/
├── config/              # Settings, URLs raíz, WSGI/ASGI
├── apps/
│   ├── inventory/       # Categorías y productos
│   ├── users/          # Clientes, empleados y autenticación
│   └── sales/          # Registro y cancelación de ventas
├── docs/               # Documentación detallada
├── .env.example
├── manage.py
├── pytest.ini
└── requirements.txt
```

---

## Modelo de datos

```
Category ◄─── Product ◄─── SaleItem ───► Sale ───► User (empleado)
                                          │
                                          └──► Customer (opcional)
```

- **Category / Product:** inventario con control de stock.
- **Customer:** cliente opcional en una venta.
- **User:** empleados creados exclusivamente por el superusuario en el panel admin.
- **Sale / SaleItem:** cabecera y detalle de cada venta.

---

## Endpoints principales

Base URL: `/api/v1/`  
Todas las rutas requieren `Authorization: Token <token>`, excepto login y logout.

| Método | Ruta | Descripción |
|--------|------|-------------|
| `POST` | `/users/login/` | Login — devuelve token |
| `POST` | `/users/logout/` | Logout — invalida token |
| `GET/POST` | `/inventory/categories/` | Listar / crear categorías |
| `GET/PUT/PATCH/DELETE` | `/inventory/categories/<id>/` | Detalle de categoría |
| `GET/POST` | `/inventory/products/` | Listar / crear productos |
| `GET/PUT/PATCH/DELETE` | `/inventory/products/<id>/` | Detalle de producto |
| `GET/POST` | `/users/customers/` | Listar / crear clientes |
| `GET/PUT/PATCH/DELETE` | `/users/customers/<id>/` | Detalle de cliente |
| `GET` | `/users/` | Listar empleados |
| `GET/PUT/PATCH/DELETE` | `/users/<id>/` | Detalle de empleado |
| `GET/POST` | `/sales/` | Listar / crear ventas |
| `GET/PATCH` | `/sales/<id>/` | Detalle / cancelar venta |

### Crear una venta

```bash
POST /api/v1/sales/
Authorization: Token <token>

{
  "customer": 1,
  "items": [
    { "product": 3, "quantity": 2 },
    { "product": 7, "quantity": 1 }
  ]
}
```

Opcionalmente, omitir `customer` o enviar vacío para usar cliente `ANONIMO`:
```bash
POST /api/v1/sales/
Authorization: Token <token>

{
  "customer": "",
  "items": [
    { "product": 3, "quantity": 2 },
    { "product": 7, "quantity": 1 }
  ]
}
```

> `customer` es opcional. Si se omite o se envía vacío (`""`), la venta se registra con el cliente genérico `ANONIMO`.

La venta se crea en estado `PAID`. El stock se descuenta automáticamente en una transacción atómica.

### Cancelar una venta

```bash
PATCH /api/v1/sales/<id>/
Authorization: Token <token>

{ "action": "cancel" }
```

Cambia el estado a `CANCELLED` y restaura el stock de todos los productos involucrados.

### Filtros disponibles en listados

```
GET /api/v1/inventory/products/?page=2
GET /api/v1/users/customers/?phone=099
GET /api/v1/sales/?status=PAID&date_from=2025-01-01&date_to=2025-01-31&customer_id=3
```

---

## Gestión de usuarios

Los empleados **solo pueden ser creados por el superusuario** desde el panel administrativo de Django (`/admin/`). No existe registro público. El flujo de un empleado es:

1. El superusuario crea su cuenta en el admin.
2. El empleado hace `POST /api/v1/users/login/` para obtener su token.
3. Usa el token en el header `Authorization` para operar la API.

---

## Despliegue en producción

### Requisitos

- Python 3.10+
- PostgreSQL (recomendado) o SQLite
- Gunicorn

### Variables de entorno requeridas

```env
SECRET_KEY=tu-clave-secreta-aqui
DEBUG=False
ALLOWED_HOSTS=tudominio.com,www.tudominio.com
CORS_ALLOWED_ORIGINS=https://tuffrontend.com
DATABASE_URL=postgresql://user:password@host:5432/dbname
```

### Pasos de despliegue

1. **Configurar variables de entorno** en tu proveedor (Render, Railway, Heroku, etc.)

2. **Ejecutar migraciones:**
   ```bash
   python manage.py migrate
   ```

3. **Recolectar archivos estáticos:**
   ```bash
   python manage.py collectstatic
   ```

4. **Ejecutar Gunicorn:**
   ```bash
   gunicorn config.wsgi:application --bind 0.0.0.0:$PORT
   ```

> **Nota:** La configuración de producción usa `dj-database-url` para parsear la variable `DATABASE_URL` y `WhiteNoise` para servir archivos estáticos de forma eficiente.

---

## Documentación detallada

La carpeta `docs/` contiene la documentación completa del proyecto:

| Archivo | Contenido |
|---------|-----------|
| `01_overview.md` | Visión general y stack |
| `02_setup.md` | Instalación y configuración completa |
| `03_domain_model.md` | Modelos, campos y relaciones |
| `04_api_contract.md` | Todos los endpoints con ejemplos |
| `05_sales_flow.md` | Flujo detallado de ventas y cancelaciones |
| `06_testing.md` | Guía de testing y casos a implementar |

---

## Licencia

Ver `LICENSE`.
