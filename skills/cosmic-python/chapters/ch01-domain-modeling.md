# Chapter 1: Domain Modeling

## Core Idea
The domain model is the pure, infrastructure-free software representation of the business problem space, modeled using Ubiquitous Language and verified through unit tests that directly express business requirements.

## Frameworks Introduced
- **Entity Pattern**: An object with persistent identity that remains continuous across time and state mutations.
  - When to use: When an object represents a business concept whose lifecycle matters and whose identity outlives its attributes (e.g., `Batch`, `Order`, `Customer`).
  - How:
    1. Identify the unique reference attribute (e.g., `reference`, `id`, `uuid`).
    2. Implement equality `__eq__` based solely on that identity attribute.
    3. Control hashing behavior: set `__hash__ = None` for mutable entities, or hash solely on an immutable identity field.
  - Why it works: Two batches with identical quantities, SKUs, and ETAs are distinct physical lots if their references differ.
  - Failure mode: Defining entity equality by comparing all fields, causing identity to be lost when state mutates.

- **Value Object Pattern**: An immutable domain concept identified entirely by the data it holds, lacking independent identity.
  - When to use: For measurements, descriptors, money, quantities, or line items (e.g., `OrderLine`, `Money`, `Sku`).
  - How:
    1. Use `@dataclass(frozen=True)` or `NamedTuple`.
    2. Leverage automatic structural equality (`__eq__`) and hashing (`__hash__`).
    3. Treat value objects as immutable: modifications return new instances rather than mutating in place.
  - Why it works: Makes business logic expressive, prevents accidental side effects, and matches human intuition (two £10 notes are interchangeable).
  - Failure mode: Adding mutable state to a value object, creating unpredictable behavior when shared or stored in sets/dictionaries.

- **Domain Service**: A standalone function representing a business operation that naturally involves multiple entities or does not belong to a single entity.
  - When to use: For cross-entity operations, allocation algorithms, or business calculations (e.g., `allocate(line, batches)`).
  - How:
    1. Define as a pure Python function rather than forcing an artificial "Manager" or "Service" class.
    2. Accept domain entities and value objects as arguments.
    3. Coordinate domain logic and return domain results or raise domain exceptions.
  - Why it works: Avoids polluting a single entity with knowledge of its siblings while avoiding anemic, procedural manager classes.
  - Failure mode: Conflating domain services with application/service-layer services (which handle I/O, database transactions, and user requests).

- **Domain Exceptions**: Custom exception classes expressing specific domain rule violations (e.g., `OutOfStock`).
  - When to use: When a business invariant cannot be satisfied and the model must reject an operation.
  - How: Define explicit domain subclasses of `Exception`, avoiding generic `ValueError` or `RuntimeError`.

## Key Concepts
- **Domain**: The real-world problem space and business workflows an application automates or supports.
- **Domain Model**: The mental map of the business translated into code, consisting of entities, value objects, domain services, and invariants.
- **Ubiquitous Language**: A common, rigorous vocabulary shared between software engineers and business domain experts, reflected directly in code naming.
- **Invariants**: Business rules, constraints, or assertions that must always remain true in a consistent domain model (e.g., available quantity cannot drop below zero).
- **Structural Equality**: Equality based on matching field values rather than memory addresses or database keys.
- **Idempotency**: An operation that yields the exact same state whether invoked once or multiple times (e.g., allocating an already allocated line has no additional effect).
- **ETA Ordering**: Business rule preferring current warehouse stock (`eta=None`) over inbound shipments, and earlier shipping dates over later shipping dates.

## Mental Models
- **Alien Spaceship Jargon**: Complex systems naturally develop precise local jargon to communicate effectively; developers must listen to business experts and translate that jargon into code constructs without dilution.
- **Coins vs. Bank Accounts**: A £10 note is a Value Object (any £10 note is equal to another); your bank account is an Entity (even if its balance fluctuates, it maintains an enduring identity).
- **Dunder Magic as Domain DSL**: Python's data model (`__eq__`, `__gt__`, `__hash__`) allows domain models to integrate with standard Python idioms like `sorted(batches)` or `batch in stock`.

## Anti-patterns
- **Anemic Domain Model**: Modeling domain concepts as dumb data bags with getters/setters while placing all actual business logic in external procedural services.
- **Primitive Obsession**: Using raw strings, tuples, or ints everywhere instead of wrapping them in meaningful value objects or domain types.
- **Silent Invariant Violations**: Allowing methods to fail silently without feedback or failing to validate domain constraints up front.
- **Over-typing with NewType Wrappers**: Wrapping every single string and integer in `NewType` wrappers (e.g., `Reference(str)`), cluttering signatures without commensurate safety.

## Code Examples

### Value Object vs. Entity Implementation

```python
from dataclasses import dataclass
from datetime import date
from typing import Optional, Set

# Value Object: Immutable, structural equality
@dataclass(frozen=True)
class OrderLine:
    orderid: str
    sku: str
    qty: int

# Entity: Persistent identity via reference, mutable internal state
class Batch:
    def __init__(self, ref: str, sku: str, qty: int, eta: Optional[date] = None):
        self.reference = ref
        self.sku = sku
        self.eta = eta
        self._purchased_quantity = qty
        self._allocations: Set[OrderLine] = set()

    def __repr__(self) -> str:
        return f"<Batch {self.reference}>"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Batch):
            return False
        return other.reference == self.reference

    def __hash__(self) -> int:
        return hash(self.reference)

    def __gt__(self, other: "Batch") -> bool:
        if self.eta is None:
            return False
        if other.eta is None:
            return True
        return self.eta > other.eta

    def allocate(self, line: OrderLine) -> None:
        if self.can_allocate(line):
            self._allocations.add(line)

    def deallocate(self, line: OrderLine) -> None:
        if line in self._allocations:
            self._allocations.remove(line)

    @property
    def allocated_quantity(self) -> int:
        return sum(line.qty for line in self._allocations)

    @property
    def available_quantity(self) -> int:
        return self._purchased_quantity - self.allocated_quantity

    def can_allocate(self, line: OrderLine) -> bool:
        return self.sku == line.sku and self.available_quantity >= line.qty
```
- **What it demonstrates**: `OrderLine` has value semantics via `@dataclass(frozen=True)`; `Batch` maintains identity via `reference`, guards internal consistency with properties, and enables `sorted()` via `__gt__`.

### Domain Service and Domain Exception

```python
from typing import List

class OutOfStock(Exception):
    pass

def allocate(line: OrderLine, batches: List[Batch]) -> str:
    try:
        batch = next(b for b in sorted(batches) if b.can_allocate(line))
        batch.allocate(line)
        return batch.reference
    except StopIteration:
        raise OutOfStock(f"Out of stock for sku {line.sku}")
```
- **What it demonstrates**: Standalone functional domain service coordinating multiple entities with idiomatic `sorted()` and `next()`.

## Reference Tables

### Entity vs. Value Object Comparison

| Dimension | Entity | Value Object |
|---|---|---|
| **Identity** | Unique, enduring identity (`reference`, `id`) | No identity; defined solely by value attributes |
| **Equality** | Identity equality (`self.ref == other.ref`) | Structural / value equality (`all fields equal`) |
| **Mutability** | Mutable lifecycle state | Strictly immutable (`frozen=True`) |
| **Python Primitive** | Standard class with custom `__eq__` / `__hash__` | `@dataclass(frozen=True)` or `NamedTuple` |
| **Examples** | `Batch`, `Order`, `Customer`, `Product` | `OrderLine`, `Money`, `Dimensions`, `DateRange` |
| **Lifecycle** | Tracked through transitions across time | Created, passed, replaced, discarded |

## Worked Example

### Test-Driving Allocation Rules

Writing unit tests that directly encode business conversations:

```python
from datetime import date, timedelta
import pytest

today = date.today()
tomorrow = today + timedelta(days=1)
later = today + timedelta(days=10)

def test_allocating_to_a_batch_reduces_the_available_quantity():
    batch = Batch("batch-001", "SMALL-TABLE", qty=20, eta=today)
    line = OrderLine("order-ref", "SMALL-TABLE", 2)
    batch.allocate(line)
    assert batch.available_quantity == 18

def test_can_allocate_if_available_greater_than_required():
    batch = Batch("batch-001", "ELEGANT-LAMP", 20, eta=today)
    line = OrderLine("order-123", "ELEGANT-LAMP", 2)
    assert batch.can_allocate(line) is True

def test_cannot_allocate_if_available_smaller_than_required():
    batch = Batch("batch-001", "ELEGANT-LAMP", 2, eta=today)
    line = OrderLine("order-123", "ELEGANT-LAMP", 20)
    assert batch.can_allocate(line) is False

def test_allocation_is_idempotent():
    batch = Batch("batch-001", "ANGULAR-DESK", 20, eta=today)
    line = OrderLine("order-ref", "ANGULAR-DESK", 2)
    batch.allocate(line)
    batch.allocate(line)
    assert batch.available_quantity == 18

def test_prefers_warehouse_batches_to_shipments():
    in_stock_batch = Batch("in-stock", "RETRO-CLOCK", 100, eta=None)
    shipment_batch = Batch("shipment", "RETRO-CLOCK", 100, eta=tomorrow)
    line = OrderLine("oref", "RETRO-CLOCK", 10)

    allocate(line, [in_stock_batch, shipment_batch])

    assert in_stock_batch.available_quantity == 90
    assert shipment_batch.available_quantity == 100

def test_raises_out_of_stock_exception_if_cannot_allocate():
    batch = Batch("batch1", "SMALL-FORK", 10, eta=today)
    allocate(OrderLine("order1", "SMALL-FORK", 10), [batch])

    with pytest.raises(OutOfStock, match="SMALL-FORK"):
        allocate(OrderLine("order2", "SMALL-FORK", 1), [batch])
```

## Key Takeaways
1. The domain model is the highest-value layer in the architecture; keep it free from database, web framework, and networking concerns.
2. Model concepts using Ubiquitous Language drawn directly from conversations with business experts.
3. Distinguish Entities (persistent identity) from Value Objects (immutable, identified by values).
4. Place business rules (invariants) inside domain objects rather than procedural controller scripts.
5. Use standalone functions for Domain Services when an operation naturally spans multiple entities.
6. Use custom Domain Exceptions to express business failure conditions unambiguously.

## Connects To
- **Ch 00**: Dependency Inversion Principle — why we keep the domain model at the center.
- **Ch 02**: Repository Pattern — persisting domain entities without polluting them with database models.
- **Ch 07**: Aggregates — grouping entities and value objects within consistency boundaries.
