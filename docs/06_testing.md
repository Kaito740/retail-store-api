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

## Tests implementados

Los tests están en `tests/` (no en `apps/*/tests.py`). A continuación se detalla la cobertura:

### `tests/test_inventory.py`

**Category:**
- ✅ GET categories con token → 200
- ✅ POST category válida → 201
- ✅ POST category sin nombre → 400
- ✅ POST category con nombre corto (<2 chars) → 400

**Product:**
- ✅ GET products con token → 200
- ✅ POST product válido → 201
- ✅ POST product con categoría inactiva → 400
- ✅ POST product con precio negativo → 400
- ✅ POST product inactivo en venta → 400

---

### `tests/test_users.py`

**Customer:**
- ✅ POST customer con datos válidos → 201
- ✅ POST customer sin nombre → default 'ANONIMO'
- ✅ POST customer sin teléfono → default '000000000'
- ✅ POST customer con whitespace → strip aplicado
- ✅ GET customers → 200
- ✅ GET customers con filtro phone → filtra correctamente

**Protección de clientes con ventas:**
- ✅ PUT/PATCH cliente con ventas asociadas → 400
- ✅ DELETE cliente con ventas asociadas → 400

**User:**
- ✅ GET users con token → 200

---

### `tests/test_auth.py`

- ✅ POST login con credenciales válidas → 200 + token
- ✅ POST login sin credenciales → 400
- ✅ POST login con credenciales inválidas → 400
- ✅ POST logout con token → 200
- ✅ POST logout sin token → 401

---

### `tests/test_sales.py`

- ✅ POST sale con datos válidos → 201, stock descontado
- ✅ POST sale sin cliente → usa cliente 'ANONIMO'
- ✅ POST sale con stock insuficiente → 400, stock intacto
- ✅ POST sale con producto inactivo → 400
- ✅ GET sale details → 200 + items
- ✅ PATCH cancel sale → 200, stock restaurado
- ✅ PATCH cancel already cancelled → 400
- ✅ GET sales con filtro status → filtra correctamente

---

## Estructura de un test

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
    Crear una venta debe descontar del stock del producto.
    customer es opcional; si se omite o envía vacío, usa cliente 'ANONIMO'.
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
