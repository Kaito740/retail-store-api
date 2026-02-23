# Testing

## Estado actual

Los tests están implementados en `tests/` (directorio raíz). Los archivos en cada app (`apps/*/tests.py`) están vacíos.

Tests implementados:
- `tests/test_auth.py` - Autenticación (login, logout)
- `tests/test_users.py` - Customers (CRUD, filtros, defaults)
- `tests/test_inventory.py` - Categories y Products
- `tests/test_sales.py` - Ventas (crear, cancelar, filtros)

---

## Configuración de pytest

El archivo `pytest.ini` en la raíz del proyecto configura la integración con Django:

```ini
[pytest]
DJANGO_SETTINGS_MODULE = config.settings
python_files = tests.py test_*.py *_tests.py
```

Para ejecutar pytest, el archivo `.env` debe estar presente con al menos `SECRET_KEY` definida (el settings lanza un `ValueError` si no está definida).

---

## Ejecutar la suite de tests

```bash
# Ejecutar todos los tests
pytest

# Con reporte de cobertura
pytest --cov=apps

# Con reporte HTML de cobertura
pytest --cov=apps --cov-report=html

# Ejecutar tests de una app específica
pytest apps/inventory/
pytest apps/sales/
pytest apps/users/
```

---

## Guía para implementar tests

A continuación se describen los tests que **deberían** implementarse para cubrir la lógica del proyecto.

### `apps/inventory/tests.py`

**Category:**
- Crear una categoría válida (nombre ≥ 2 chars, is_active=True/False).
- Intentar crear una categoría con nombre duplicado → debe fallar.
- Intentar crear una categoría con nombre muy corto (< 2 chars) → debe fallar.

**Product:**
- Crear un producto con categoría activa → debe funcionar.
- Intentar crear un producto con categoría inactiva → debe fallar (`ValidationError`).
- Verificar que el barcode es único.
- Intentar crear un producto con precio negativo → debe fallar.

**Endpoints (API):**
- `GET /api/v1/inventory/categories/` sin token → 401.
- `GET /api/v1/inventory/categories/` con token → 200 + lista.
- `POST /api/v1/inventory/categories/` con datos válidos → 201.
- `POST /api/v1/inventory/products/` con categoría inactiva → 400.

---

### `apps/users/tests.py`

**Customer:**
- Crear cliente con nombre y teléfono → guarda correctamente con strip.
- Crear cliente sin nombre → nombre queda como `'ANONIMO'`.
- Crear cliente sin teléfono → teléfono queda como `'000000000'`.

**Login:**
- `POST /api/v1/users/login/` con credenciales válidas → 200 + token.
- `POST /api/v1/users/login/` con contraseña incorrecta → 401.
- `POST /api/v1/users/login/` sin campos → 400.

**Clientes (API):**
- `GET /api/v1/users/customers/?phone=099` → filtra correctamente.
- `POST /api/v1/users/customers/` sin campos → crea con valores por defecto.

---

### `apps/sales/tests.py`

**Servicio `sale_paid`:**
- Crear venta con un producto activo con stock suficiente → venta en PAID, stock descontado.
- Intentar crear venta con producto sin stock suficiente → ValidationError, sin cambios en BD.
- Verificar que `unit_price` en `SaleItem` refleja el precio del producto al momento de la venta.
- Crear venta sin cliente → `customer` es `None`.
- Verificar que `total_amount` se calcula correctamente (suma de subtotales).

**Servicio `sale_cancelled`:**
- Cancelar una venta PAID → estado cambia a CANCELLED, stock restaurado.
- Intentar cancelar una venta ya cancelada → ValidationError.
- Intentar cancelar una venta inexistente → ValidationError.

**Endpoints (API):**
- `POST /api/v1/sales/` con producto inactivo → 400.
- `POST /api/v1/sales/` con stock insuficiente → 400.
- `GET /api/v1/sales/?status=PAID` → solo devuelve ventas PAID.
- `GET /api/v1/sales/?date_from=2025-01-01&date_to=2025-01-31` → filtra por fechas.
- `PATCH /api/v1/sales/<id>/` con `action=cancel` → 200 + venta cancelada.
- `PATCH /api/v1/sales/<id>/` con acción inválida → 400.

---

## Ejemplo de estructura base para un test

```python
import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from apps.inventory.models import Category, Product


@pytest.fixture
def authenticated_client(db):
    user = User.objects.create_user(username='empleado', password='pass123')
    token = Token.objects.create(user=user)
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
    return client


@pytest.fixture
def active_category(db):
    return Category.objects.create(name='Juguetes', is_active=True)


@pytest.fixture
def inactive_category(db):
    return Category.objects.create(name='Electronica', is_active=False)


@pytest.fixture
def active_product(db, active_category):
    return Product.objects.create(
        name='Auto de juguete',
        barcode='7891234567890',
        category=active_category,
        price='10.00',
        stock_quantity=100,
        is_active=True
    )


@pytest.fixture
def inactive_product(db, active_category):
    return Product.objects.create(
        name='Producto inactivo',
        barcode='1111111111111',
        category=active_category,
        price='5.00',
        stock_quantity=50,
        is_active=False
    )


@pytest.mark.django_db
def test_create_sale_discounts_stock(authenticated_client, active_product):
    """
    Crear una venta debe descontar el stock del producto.
    customer es opcional; si se omite, la venta queda sin cliente.
    """
    payload = {
        'items': [{'product': active_product.id, 'quantity': 3}]
    }
    response = authenticated_client.post('/api/v1/sales/', payload, format='json')

    assert response.status_code == 201

    active_product.refresh_from_db()
    assert active_product.stock_quantity == 97  # 100 - 3


@pytest.mark.django_db
def test_create_sale_insufficient_stock_returns_400(authenticated_client, active_product):
    payload = {
        'items': [{'product': active_product.id, 'quantity': 999}]
    }
    response = authenticated_client.post('/api/v1/sales/', payload, format='json')

    assert response.status_code == 400
    active_product.refresh_from_db()
    assert active_product.stock_quantity == 100  # sin cambios
```
