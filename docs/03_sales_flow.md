# Sales flow

## Sales states
A sale can exist in one of the following states:

- DRAFT
- CONFIRMED
- PAID
- CANCELLED

## State transitions
### DRAFT
- The sale is being created.
- Products can be added, removed, or updated.
- Stock is NOT affected.
- The sale can be cancelled.

### CONFIRMED
- The sale is reviewed and confirmed by the cashier.
- No structural changes allowed.
- Awaiting payment.
- Stock is NOT affected.

### PAID
- Payment has been completed.
- Stock is reduced.
- The sale becomes immutable.
- Generates payment receipt.

### CANCELLED
- The sale is aborted.
- No stock changes occur.
- The sale remains in history for audit purposes.

## State responsibilities
Allowed transitions:

- DRAFT → CONFIRMED
- DRAFT → CANCELLED
- CONFIRMED → PAID
- CONFIRMED → CANCELLED

## Invalid transitions
The following transitions are NOT allowed:

- PAID → any state
- CANCELLED → any state
- DRAFT → PAID

## Sales state diagram

DRAFT
  ├── confirm ──▶ CONFIRMED
  ├── cancel ───▶ CANCELLED

CONFIRMED
  ├── back_to_draft ─▶ DRAFT
  ├── pay ──────────▶ PAID
  ├── cancel ───────▶ CANCELLED

PAID (terminal)
CANCELLED (terminal)


```mermaid
stateDiagram-v2
    [*] --> DRAFT
    DRAFT --> CONFIRMED : confirm
    DRAFT --> CANCELLED : cancel

    CONFIRMED --> DRAFT : back_to_draft
    CONFIRMED --> PAID : pay
    CONFIRMED --> CANCELLED : cancel

    PAID --> [*]
    CANCELLED --> [*]