# Flujo de Ventas

## Descripción general

El módulo de ventas es el núcleo del sistema. Toda la lógica de negocio está encapsulada en `apps/sales/services.py` y se ejecuta dentro de **transacciones atómicas** para garantizar consistencia de datos.

---

## Crear una venta (`sale_paid`)

```mermaid
sequenceDiagram
    actor Empleado
    participant View as SaleListCreateView
    participant Serializer as SaleSerializer
    participant Service as sale_paid()
    participant DB as Base de Datos

    Empleado->>View: POST /api/v1/sales/
    View->>Serializer: Validar datos (items, customer)
    Serializer->>Serializer: validate_product()<br/>¿producto activo?
    alt Producto inactivo
        Serializer-->>View: ValidationError 400
        View-->>Empleado: 400 Bad Request
    end
    Serializer-->>View: Datos validados

    View->>Service: sale_paid(created_by, products_data, customer)

    note over Service,DB: TRANSACCIÓN ATÓMICA

    Service->>DB: Crear Sale (status=PAID)
    loop Por cada ítem
        Service->>DB: SELECT FOR UPDATE Product
        alt Stock insuficiente
            Service-->>View: ValidationError
            View-->>Empleado: 400 Bad Request
        end
        Service->>DB: product.stock_quantity -= quantity
        Service->>DB: Crear SaleItem (unit_price = precio actual)
    end
    Service->>DB: sale.total_amount = suma de subtotales
    Service-->>View: Sale creada

    View-->>Empleado: 201 Created {sale_id, total_amount, status}
```

---

## Cancelar una venta (`sale_cancelled`)

```mermaid
sequenceDiagram
    actor Empleado
    participant View as SaleDetailView
    participant Service as sale_cancelled()
    participant DB as Base de Datos

    Empleado->>View: PATCH /api/v1/sales/<id>/ {action: cancel}
    View->>Service: sale_cancelled(sale_id)

    Service->>DB: Buscar venta por ID
    alt Venta no existe
        Service-->>View: ValidationError
        View-->>Empleado: 400 Bad Request
    end
    alt Venta ya cancelada
        Service-->>View: ValidationError
        View-->>Empleado: 400 Bad Request
    end

    note over Service,DB: TRANSACCIÓN ATÓMICA

    loop Por cada SaleItem
        Service->>DB: SELECT FOR UPDATE Product
        Service->>DB: product.stock_quantity += item.quantity
    end
    Service->>DB: sale.status = CANCELLED
    Service-->>View: Sale actualizada

    View-->>Empleado: 200 OK {sale_id, status: CANCELLED}
```

---

## Estados de una venta

```mermaid
stateDiagram-v2
    [*] --> PAID : POST /api/v1/sales/
    PAID --> CANCELLED : PATCH con action=cancel
    CANCELLED --> [*]
```

Una venta cancelada **no puede reactivarse**. El sistema no contempla ese flujo.

---

## Integridad transaccional

Ambas operaciones usan `transaction.atomic()` y `select_for_update()` sobre los productos para prevenir condiciones de carrera cuando varios empleados operan simultáneamente.

Si cualquier paso falla (producto inexistente, stock insuficiente, error de validación), **todos los cambios se revierten automáticamente** y la base de datos queda en el estado previo a la operación.
