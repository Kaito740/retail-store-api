# Domain Model

## Entities

### Product
Represents an item available for sale.

Attributes:
- id
- name
- barcode
- category
- price
- stock_quantity
- is_active

Rules:
- barcode uniquely identifies a product type
- barcode is immutable once created
- stock is not modified until a sale is PAID

### Category
Represents a product classification.

Attributes:
- id
- name
- is_active

Rules:
- category name must be unique
- inactive categories cannot be assigned to new products


### Sale
Represents a customer purchase transaction.

Attributes:
- id
- status (DRAFT, CONFIRMED, PAID, CANCELLED)
- total_amount
- created_at

Rules:
- a sale must contain at least one product
- a sale cannot be modified once PAID
- stock is reduced only when the sale is PAID

---

### SaleItem
Represents a line item within a sale.

Attributes:
- id
- sale
- product
- quantity
- unit_price
- subtotal

Rules:
- quantity must be greater than zero
- unit_price is captured at sale time
- subtotal = quantity * unit_price

---

### Customer
Represents a customer associated with a sale.

Attributes:
- id
- name
- phone

Rules:
- a sale may exist without a customer
- customer data is optional but persistent

---

### User (Staff)
Represents a system user operating the store.

Attributes:
- id
- email
- role

Rules:
- users are responsible for registering sales
- users are not customers

Note:
User is a system actor, not a business entity.
It is referenced for traceability, not for domain rules.
---

## Value Objects

### SaleStatus
Defines the lifecycle states of a sale.

Values:
- DRAFT
- CONFIRMED
- PAID
- CANCELLED

Rules:
- PAID and CANCELLED are terminal states

---

### Money
Represents a monetary value.

Attributes:
- amount
- currency

Used in:
- Product.price
- SaleItem.unit_price
- SaleItem.subtotal
- Sale.total_amount

Note:
Money is a conceptual value object.
In implementation, amounts are stored as decimals.

---

## Relationships

- A Sale has one or more SaleItems
- A SaleItem references one Product
- A Sale may reference zero or one Customer
- A Sale is registered by one User

---

## Non-Entities (Explicitly Excluded)

The following concepts are not part of the domain model and are handled at the application or infrastructure level:

- Authentication
- JWT tokens
- Permissions
- Reports
- PDF receipts
- Payment gateways