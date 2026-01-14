# Requirements

## Functional requirements

Products & Inventory
The system must allow creating, updating, listing, and deactivating products.
Each product must have stock quantity tracking.
Stock must not be modified until a sale is paid.

Sales
The system must allow creating a sale in DRAFT state.
A sale must contain one or more products.
A sale must allow modifying products while in DRAFT.
The system must allow confirming a sale.
The system must allow cancelling a sale before payment.
The system must allow marking a sale as PAID.
Once PAID, the sale cannot be modified.

Customers
The system must allow registering customer data.
A sale may exist without a registered customer.

History
The system must keep a permanent record of completed and cancelled sales.

## Non-Funtional requirements

The system must expose a RESTful API.
Authentication must be required for all endpoints.
The system must enforce role-based permissions.
Data integrity must be preserved at all times.
The system must be maintainable and scalable.

## Business rules

The system must expose a RESTful API.
Authentication must be required for all endpoints.
The system must enforce role-based permissions.
Data integrity must be preserved at all times.
The system must be maintainable and scalable.