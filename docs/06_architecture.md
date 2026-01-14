# Architecture Overview

This document describes the backend architecture of the Toy Retail Store API.

The objective of this architecture is to ensure:

* Clear separation of responsibilities
* Maintainability as the system grows
* Predictable business behavior
* Minimal coupling between layers

The backend follows a layered architecture, where each layer has a specific responsibility and well-defined boundaries.

---

## Architectural Principles

* Business rules must be explicit and centralized
* HTTP concerns must not leak into business logic
* Domain rules must not depend on frameworks
* Validation, authorization, and business logic must be separated
* Simplicity is preferred over premature abstraction

---

## Layered Architecture Overview

The system is organized into the following layers:
```
HTTP / API Layer
↓
Serialization & Validation Layer
↓
Service Layer (Business Logic)
↓
Domain Layer (Models)
↓
Persistence Layer (Database)
```

**Each layer may only depend on the layer directly below it.**

---

## API Layer (Views)

### Responsibilities

* Receive HTTP requests
* Trigger authentication and authorization
* Delegate work to the service layer
* Return HTTP responses

### Rules

* Must **NOT** contain business logic
* Must **NOT** perform state transitions
* Must **NOT** modify the database directly
* Must **NOT** implement complex validations

### Implementation

* Django REST Framework
* `APIView` is used for business actions
* `ViewSets` are used only for simple CRUD resources

### Examples of API responsibilities

* Create a sale
* Add an item to a sale
* Confirm a sale
* Pay a sale
* Cancel a sale

---

## Serialization & Validation Layer

### Responsibilities

* Validate incoming request data
* Convert JSON into Python primitives
* Convert Python objects into JSON responses

### Rules

* Must **NOT** contain business rules
* Must **NOT** perform database state changes
* Must **NOT** control workflows

### Serializer Types

* `ModelSerializer` for direct CRUD operations
* `Serializer` for actions and workflows

### Examples

* Login
* Add item to sale
* Confirm sale
* Pay sale

---

## Service Layer (Business Logic)

### Responsibilities

* Enforce business rules
* Control state transitions
* Coordinate multiple domain entities
* Execute transactional logic

### Rules

* Must **NOT** return HTTP responses
* Must **NOT** depend on Django REST Framework
* Must raise domain-specific errors
* Must be callable from multiple entry points

### Examples of Services

* `SaleService.create_sale`
* `SaleService.add_item`
* `SaleService.confirm_sale`
* `SaleService.pay_sale`
* `SaleService.cancel_sale`

---

## Domain Layer

### Responsibilities

* Represent business entities
* Define relationships between entities
* Enforce basic invariants

### Rules

* Must **NOT** know about HTTP
* Must **NOT** know about serializers
* Must **NOT** know about permissions or authentication

### Implementation

* Implemented using Django models
* Complex business logic is delegated to services

---

## Persistence Layer

### Responsibilities

* Store and retrieve data
* Enforce database constraints

### Implementation

* Django ORM
* Relational database

---

## Authentication & Authorization

### Authentication

* JWT-based authentication
* Handled globally by Django REST Framework
* Authentication occurs before view execution

### Authorization

* Implemented via DRF permission classes
* Permissions are evaluated after authentication

### Status Codes

* `401 Unauthorized`: user is not authenticated
* `403 Forbidden`: user is authenticated but lacks permission

---

## Error Handling Strategy

* Business errors are raised in the service layer
* Views translate errors into HTTP responses
* No raw exceptions should reach the client

---

## Project Structure

### Recommended high-level structure
```
project_root/
├── config/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── apps/
│   ├── products/
│   ├── categories/
│   ├── sales/
│   ├── customers/
│   └── users/
├── docs/
├── venv/
└── manage.py
```

### Recommended structure per app
```
app_name/
├── models.py
├── serializers.py
├── services.py
├── views.py
├── permissions.py
├── urls.py
```

---

## What This Architecture Prevents

* Fat views
* Business logic hidden in serializers
* Uncontrolled CRUD endpoints
* Tight coupling between layers
* Fragile codebases

---

## Relationship Between Documents

* **API Contract** defines how clients interact with the system
* **Domain Model** defines business concepts and rules
* **Architecture** defines how the system is implemented

---

## Final Notes

This architecture is designed to support growth without sacrificing clarity.

**Code should only be written after the domain, contracts, and architecture are clearly defined.**