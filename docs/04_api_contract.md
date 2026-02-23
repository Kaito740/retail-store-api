# Contrato de la API

Base URL: `/api/v1/`

Todas las rutas (excepto `POST /api/v1/users/login/` y `POST /api/v1/users/logout/`) requieren autenticación mediante **Token**.

**Header requerido:**
```
Authorization: Token <token>
```

---

## Autenticación

### `POST /api/v1/users/login/`

Login de empleado. Devuelve el token de autenticación.

**Permiso:** Público (no requiere token)

**Request body:**
```json
{
  "username": "empleado1",
  "password": "contraseña123"
}
```

**Response 200 OK:**
```json
{
  "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b",
  "user": {
    "id": 1,
    "username": "empleado1",
    "email": "empleado@tienda.com",
    "first_name": "Juan",
    "last_name": "Pérez"
  }
}
```

**Response 400 Bad Request** (campos faltantes):
```json
{ "error": "Username y password son requeridos" }
```

**Response 400 Bad Request** (credenciales inválidas):
```json
{ "error": "Credenciales inválidas" }
```

### `POST /api/v1/users/logout/`

Logout de empleado. Invalida el token de autenticación.

**Permiso:** Requiere autenticación (Token)

**Request:** No requiere body

**Header requerido:**
```
Authorization: Token <token>
```

**Response 200 OK:**
```json
{ "detail": "Logout exitoso" }
```

---

## Categorías

### `GET /api/v1/inventory/categories/`

Lista todas las categorías ordenadas por nombre.

**Response 200 OK:**
```json
[
  { "id": 1, "name": "Juguetes", "is_active": true },
  { "id": 2, "name": "Electrónica", "is_active": false }
]
```

### `POST /api/v1/inventory/categories/`

Crea una nueva categoría.

**Request body:**
```json
{
  "name": "Juguetes",
  "is_active": true
}
```

**Response 201 Created:**
```json
{ "id": 3, "name": "Juguetes", "is_active": true }
```

### `GET /api/v1/inventory/categories/<id>/`

Obtiene el detalle de una categoría.

### `PUT /api/v1/inventory/categories/<id>/`

Actualización completa de una categoría.

### `PATCH /api/v1/inventory/categories/<id>/`

Actualización parcial de una categoría.

### `DELETE /api/v1/inventory/categories/<id>/`

Elimina una categoría.

> ⚠️ Si la categoría tiene productos asociados, Django lanzará un error de integridad referencial (PROTECT) y la eliminación fallará.

---

## Productos

### `GET /api/v1/inventory/products/`

Lista todos los productos ordenados por nombre.

**Response 200 OK:**
```json
[
  {
    "id": 1,
    "name": "Auto de juguete",
    "barcode": "7891234567890",
    "category": 1,
    "price": "15.99",
    "stock_quantity": 50,
    "is_active": true
  }
]
```

### `POST /api/v1/inventory/products/`

Crea un nuevo producto.

**Validación:** La categoría referenciada debe estar activa (`is_active=True`), de lo contrario se devuelve un error de validación.

**Request body:**
```json
{
  "name": "Auto de juguete",
  "barcode": "7891234567890",
  "category": 1,
  "price": "15.99",
  "stock_quantity": 50,
  "is_active": true
}
```

### `GET /api/v1/inventory/products/<id>/`

Obtiene el detalle de un producto.

### `PUT /api/v1/inventory/products/<id>/`

Actualización completa de un producto.

### `PATCH /api/v1/inventory/products/<id>/`

Actualización parcial de un producto.

### `DELETE /api/v1/inventory/products/<id>/`

Elimina un producto.

> ⚠️ Si el producto tiene ítems de venta asociados, la eliminación fallará (PROTECT).

---

## Clientes

### `GET /api/v1/users/customers/`

Lista todos los clientes ordenados por nombre.

**Filtros opcionales:**

| Parámetro | Descripción |
|---|---|
| `phone` | Búsqueda parcial por teléfono (case-insensitive) |

Ejemplo: `GET /api/v1/users/customers/?phone=099`

**Response 200 OK:**
```json
[
  { "id": 1, "name": "María García", "phone": "0991234567" }
]
```

### `POST /api/v1/users/customers/`

Crea un nuevo cliente. Todos los campos son opcionales; si se omiten, se aplican los valores por defecto (`ANONIMO`, `000000000`).

**Request body:**
```json
{
  "name": "María García",
  "phone": "0991234567"
}
```

### `GET /api/v1/users/customers/<id>/`

Obtiene el detalle de un cliente.

### `PUT /api/v1/users/customers/<id>/`

Actualización completa de un cliente.

### `PATCH /api/v1/users/customers/<id>/`

Actualización parcial de un cliente.

### `DELETE /api/v1/users/customers/<id>/`

Elimina un cliente.

---

## Usuarios (Empleados)

> Los usuarios solo son creados por el superusuario desde el panel administrativo de Django.

### `GET /api/v1/users/`

Lista todos los usuarios (empleados).

**Response 200 OK:**
```json
[
  {
    "id": 1,
    "username": "empleado1",
    "email": "empleado@tienda.com",
    "first_name": "Juan",
    "last_name": "Pérez",
    "date_joined": "2025-01-15T10:00:00Z",
    "is_active": true
  }
]
```

### `GET /api/v1/users/<id>/`

Obtiene el detalle de un usuario.

### `PUT /api/v1/users/<id>/`

Actualiza `first_name`, `last_name` y `email` de un usuario.

### `PATCH /api/v1/users/<id>/`

Actualización parcial de `first_name`, `last_name` y/o `email`.

### `DELETE /api/v1/users/<id>/`

Intenta eliminar el usuario. Si tiene ventas asociadas (PROTECT), en lugar de eliminar lo **desactiva** (`is_active=False`) para preservar la integridad de los datos.

---

## Ventas

### `GET /api/v1/sales/`

Lista todas las ventas ordenadas por fecha de creación descendente.

**Filtros opcionales:**

| Parámetro | Descripción | Ejemplo |
|---|---|---|
| `status` | Filtrar por estado | `?status=PAID` o `?status=CANCELLED` |
| `customer_id` | Filtrar por ID de cliente | `?customer_id=3` |
| `date_from` | Ventas desde esta fecha (YYYY-MM-DD) | `?date_from=2025-01-01` |
| `date_to` | Ventas hasta esta fecha (YYYY-MM-DD) | `?date_to=2025-01-31` |

**Response 200 OK:**
```json
[
  {
    "id": 1,
    "status": "PAID",
    "total_amount": "47.97",
    "customer": 1,
    "customer_name": "María García",
    "created_by": 2,
    "created_by_username": "empleado1",
    "created_at": "2025-01-20T14:30:00Z",
    "items": [
      {
        "id": 1,
        "product": 5,
        "quantity": 3,
        "unit_price": "15.99",
        "subtotal": "47.97"
      }
    ]
  }
]
```

### `POST /api/v1/sales/`

Registra una nueva venta. La venta se crea siempre en estado **PAID**.

El proceso de creación (manejado por `sale_paid` en `services.py`) realiza lo siguiente dentro de una transacción atómica:
1. Verifica que cada producto exista y tenga stock suficiente.
2. Descuenta el stock de cada producto.
3. Crea la venta y sus ítems.
4. Calcula el `total_amount` sumando los subtotales.

**Request body:**
```json
{
  "customer": 1,
  "items": [
    { "product": 5, "quantity": 3 },
    { "product": 8, "quantity": 1 }
  ]
}
```

> - `customer` es opcional. Si se omite, la venta se registra sin cliente.
> - Cada ítem requiere `product` (ID) y `quantity` (entero > 0).

**Validaciones previas al crear:**
- El producto debe existir.
- El producto debe estar activo (`is_active=True`).
- La cantidad debe ser mayor a 0.
- El stock disponible debe ser mayor o igual a la cantidad solicitada.

**Response 201 Created:**
```json
{
  "message": "Venta creada exitosamente",
  "sale_id": 12,
  "total_amount": "63.96",
  "status": "PAID"
}
```

**Response 400 Bad Request** (stock insuficiente, producto inactivo, etc.):
```json
{ "error": "Stock insuficiente para: Auto de juguete. Disponible: 2" }
```

### `GET /api/v1/sales/<id>/`

Obtiene el detalle completo de una venta, incluyendo sus ítems.

### `PATCH /api/v1/sales/<id>/`

Cancela una venta. Requiere el campo `action` con el valor `cancel`.

El proceso de cancelación (manejado por `sale_cancelled` en `services.py`) realiza lo siguiente dentro de una transacción atómica:
1. Verifica que la venta exista.
2. Verifica que la venta no esté ya cancelada.
3. Restaura el stock de cada producto involucrado en la venta.
4. Cambia el estado de la venta a `CANCELLED`.

**Request body:**
```json
{ "action": "cancel" }
```

**Response 200 OK:**
```json
{
  "message": "Venta cancelada exitosamente",
  "sale_id": 12,
  "status": "CANCELLED"
}
```

**Response 400 Bad Request** (ya cancelada u otro error):
```json
{ "error": "Esta venta ya fue cancelada" }
```

---

## Paginación

La API implementa paginación por número de página con un tamaño de página de **20 registros**. Los endpoints de listado devuelven la estructura estándar de DRF:

```json
{
  "count": 45,
  "next": "http://localhost:8000/api/v1/inventory/products/?page=2",
  "previous": null,
  "results": [ ... ]
}
```
