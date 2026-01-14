# API Contract

This document defines the public REST API of the Toy Retail Store system.
It describes how clients (frontend, mobile, integrations) interact with the backend.

**Base URL:** `/api/v1/`

---

## 🛠 General Conventions

* **All requests and responses use JSON.**
* **Authentication via token** (DRF Token Authentication).
* **Dates use ISO 8601 format.**
* **Prices use local currency** (e.g. PEN).
* **Stock is never modified directly by the frontend.**

---

## 🔐 Authentication

### POST `/auth/login/`

Authenticates a system user (cashier or admin).

#### Request
```json
{
  "username": "cashier1",
  "password": "password123"
}
```

#### Response – 200 OK
```json
{
  "token": "abc123token"
}
```

#### Errors

* `401 Unauthorized` → Invalid credentials

---

## 🧸 Products

Products represent items available for sale.

### GET `/products/`

Returns the list of active products.

#### Response – 200 OK
```json
[
  {
    "id": 1,
    "name": "Toy Car",
    "barcode": "7501234567890",
    "price": 50.00,
    "stock_quantity": 20,
    "is_active": true
  }
]
```

### POST `/products/`

Creates a new product.

#### Request
```json
{
  "name": "Doll",
  "barcode": "7509876543210",
  "price": 80.00,
  "stock_quantity": 15
}
```

#### Rules

* `barcode` must be unique.
* `barcode` is immutable after creation.

#### Response – 201 Created
```json
{
  "id": 2,
  "name": "Doll",
  "barcode": "7509876543210",
  "price": 80.00,
  "stock_quantity": 15,
  "is_active": true
}
```

---

## 👥 Customers

Customers are optional. A sale can exist without an associated customer.

### POST `/customers/`

Creates a customer.

#### Request
```json
{
  "name": "Juan Perez",
  "phone": "987654321"
}
```

#### Rules

* At least one field must be provided.
* Phone number should be unique when present.

#### Response – 201 Created
```json
{
  "id": 5,
  "name": "Juan Perez",
  "phone": "987654321"
}
```

### GET `/customers/by-phone/{phone}/`

Finds a customer by phone number.

#### Response – 200 OK
```json
{
  "id": 5,
  "name": "Juan Perez",
  "phone": "987654321"
}
```

---

## 💰 Sales

Sales are the core business entity of the system.

### Sale States

A sale can be in one of the following states:

* **DRAFT**: Sale in progress (editable).
* **CONFIRMED**: Customer confirmed, not paid yet.
* **PAID**: Sale completed and paid (Final).
* **CANCELLED**: Sale cancelled (Final).

### State Rules

* Only **DRAFT** sales can be modified.
* **CONFIRMED** can return to **DRAFT**.
* **PAID** cannot be modified or cancelled.
* Stock is reduced only when a sale is **PAID**.

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/sales/` | Creates a new sale in DRAFT state. |
| GET | `/sales/{id}/` | Returns full sale details. |
| POST | `/sales/{id}/items/` | Adds a product to a sale (only in DRAFT). |
| DELETE | `/sales/{id}/items/{item_id}/` | Removes an item from a sale (only in DRAFT). |
| POST | `/sales/{id}/assign-customer/` | Associates a customer with the sale. |
| POST | `/sales/{id}/confirm/` | Moves a sale from DRAFT to CONFIRMED. |
| POST | `/sales/{id}/back-to-draft/` | Moves a sale from CONFIRMED back to DRAFT. |
| POST | `/sales/{id}/pay/` | Completes the sale (Changes state to PAID, reduces stock). |
| POST | `/sales/{id}/cancel/` | Cancels a sale (DRAFT or CONFIRMED only). |

### Example JSON Responses

#### GET `/sales/{id}/`
```json
{
  "id": 10,
  "status": "DRAFT",
  "customer": null,
  "items": [
    {
      "id": 1,
      "product_id": 1,
      "product_name": "Toy Car",
      "quantity": 2,
      "unit_price": 50.00,
      "subtotal": 100.00
    }
  ],
  "total_amount": 100.00
}
```

#### POST `/sales/{id}/items/`

**Request**
```json
{
  "barcode": "7501234567890",
  "quantity": 2
}
```

---

## ⚠️ Error Codes

* `400 Bad Request` → Business rule violation.
* `401 Unauthorized` → Not authenticated.
* `403 Forbidden` → Not authorized.
* `404 Not Found` → Resource not found.

---

## 🏗 Design Principles

* **Not all endpoints are CRUD**: Actions like `/pay/` or `/confirm/` represent business operations.
* **Backend Enforcement**: Business rules are enforced strictly in the backend.
* **Explicit Transitions**: State transitions are explicit via dedicated endpoints.
* **Frontend Restriction**: Frontend never modifies stock directly.
* **Lifecycle Driven**: The sale lifecycle drives the entire system logic.