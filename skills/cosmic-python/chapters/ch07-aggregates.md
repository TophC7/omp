# Chapter 7: Aggregates and Consistency Boundaries

## Core Idea
An Aggregate is a cluster of domain objects treated as a single unit for data changes, bounded by an Aggregate Root entity that enforces business invariants and provides the exclusive entry point for state modifications and persistence.

## Frameworks Introduced
- **The Aggregate Pattern**: A group of associated entities and value objects with an explicit consistency boundary, guarded by an Aggregate Root.
  - When to use: When multiple domain objects must maintain shared business invariants (e.g., `Product` guarding a collection of `Batch` entities for a specific SKU).
  - How:
    1. Select an Aggregate Root entity (e.g., `Product`) whose identity identifies the cluster.
    2. Make internal entities and value objects private to the aggregate; external callers cannot mutate internal objects directly.
    3. Expose methods on the root (e.g., `product.allocate(line)`) that execute domain rules and enforce consistency.
    4. Persist and load the entire aggregate together through a single repository.
  - Why it works: Isolates consistency checks to a small, cohesive island of state, avoiding the need to lock massive database tables or entire databases during concurrent transactions.
  - Failure mode: Designing giant aggregates (e.g., putting all products or an entire warehouse inside one aggregate), leading to extreme lock contention and performance bottlenecks.

- **The "One Aggregate = One Repository" Rule**:
  - Repositories should only load and save Aggregate Roots.
  - Never create separate repositories for child entities or value objects (no `BatchRepository`; only `ProductRepository`).
  - Child entities are accessed solely by traversing from the Aggregate Root.

- **Optimistic Concurrency Control (Version Numbers)**:
  - Add a `version_number: int` attribute to the Aggregate Root.
  - On update, execute an atomic compare-and-swap SQL statement:
    `UPDATE products SET version_number = :new_ver WHERE sku = :sku AND version_number = :old_ver`
  - If another transaction modified the aggregate concurrently, zero rows are updated, signaling a concurrency collision that triggers an immediate rollback or retry.

- **Bounded Contexts (Evans / Fowler)**:
  - Different subdomains require different mental models of the same real-world concept.
  - In an allocation subdomain, `Product` has only `sku` and `batches`; in an e-commerce catalog subdomain, `Product` has `price`, `description`, `images`, and `reviews`.
  - Never create a bloated, monolithic enterprise model trying to represent every attribute across all departments.

## Key Concepts
- **Consistency Boundary**: The perimeter enclosing a set of domain objects that must satisfy all business invariants synchronously at the end of every transaction.
- **Aggregate Root**: The single master entity through which all external code interacts with the aggregate's internal state.
- **Invariant**: A business condition or rule that must always hold true whenever an operation completes (e.g., available stock cannot drop below zero).
- **Constraint**: A rule restricting valid system states (e.g., an order line can be allocated to only one batch at a time).
- **Optimistic Locking**: Allowing concurrent operations without locking rows up front, detecting collisions at commit time using version checks.
- **Pessimistic Locking**: Explicitly acquiring database row locks (`SELECT FOR UPDATE`) to block concurrent readers or writers until transaction completion.

## Mental Models
- **Public vs. Private Scope**: Just as a class uses private methods for internal mechanics and public methods for its API, an Aggregate Root is the "public" face of a cluster of otherwise "private" entities.
- **Islands of Consistency**: Systems are composed of small, independent islands of immediate consistency (Aggregates); between islands, consistency is eventual.
- **The Bounded Slice**: Don't model the whole elephant; model only the tail if your subsystem's job is swatting flies.

## Anti-patterns
- **God Aggregates**: Designing aggregates that span thousands of entities (e.g., an `Account` aggregate holding all 10 years of ledger transactions), destroying concurrency and memory efficiency.
- **Bypassing the Root**: Allowing external service code to directly look up, modify, and save child entities without going through the aggregate root.
- **Child Repositories**: Creating standalone repositories for internal entities (e.g., creating a `LineItemRepository` alongside an `OrderRepository`).
- **Monolithic Enterprise Model**: Forcing sales, logistics, billing, and procurement to share a single giant `Product` database model.

## Code Examples

### The Product Aggregate Root

```python
# model.py - Domain Model
from typing import List, Optional
from datetime import date

class OutOfStock(Exception):
    pass

class Product:
    def __init__(self, sku: str, batches: List["Batch"], version_number: int = 0):
        self.sku = sku
        self.batches = batches
        self.version_number = version_number

    def allocate(self, line: "OrderLine") -> str:
        try:
            batch = next(b for b in sorted(self.batches) if b.can_allocate(line))
            batch.allocate(line)
            self.version_number += 1
            return batch.reference
        except StopIteration:
            raise OutOfStock(f"Out of stock for sku {line.sku}")

    def change_batch_quantity(self, ref: str, qty: int) -> None:
        batch = next(b for b in self.batches if b.reference == ref)
        batch.change_purchased_quantity(qty)
        self.version_number += 1
```
- **What it demonstrates**: `Product` acts as the aggregate root, managing a collection of `Batch` entities and maintaining the `version_number` invariant.

### One Aggregate = One Repository

```python
# repository.py
import abc
from typing import Optional
from sqlalchemy.orm import Session
import model

class AbstractProductRepository(abc.ABC):
    @abc.abstractmethod
    def add(self, product: model.Product) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def get(self, sku: str) -> Optional[model.Product]:
        raise NotImplementedError

class SqlAlchemyProductRepository(AbstractProductRepository):
    def __init__(self, session: Session):
        self.session = session

    def add(self, product: model.Product) -> None:
        self.session.add(product)

    def get(self, sku: str) -> Optional[model.Product]:
        return self.session.query(model.Product).filter_by(sku=sku).one_or_none()
```
- **What it demonstrates**: The repository only exposes `Product`. `Batch` instances are loaded and saved automatically via relationships mapped to `Product`.

### Service Layer Operating on the Aggregate

```python
# services.py
from unit_of_work import AbstractUnitOfWork
import model

class InvalidSku(Exception):
    pass

def allocate(orderid: str, sku: str, qty: int, uow: AbstractUnitOfWork) -> str:
    line = model.OrderLine(orderid, sku, qty)
    with uow:
        product = uow.products.get(sku=line.sku)
        if product is None:
            raise InvalidSku(f"Invalid sku {line.sku}")
        
        batchref = product.allocate(line)
        uow.commit()
        return batchref
```
- **What it demonstrates**: The service fetches the aggregate root by SKU and delegates the business operation directly to `product.allocate()`.

## Reference Tables

### Aggregate Sizing Trade-offs

| Aggregate Size | Concurrency & Performance | Invariant Enforcement | Transaction Complexity |
|---|---|---|---|
| **Small (1-5 objects)** | High concurrency; minimal lock conflicts | Easy to reason about within boundary | Simple, isolated database transactions |
| **Medium (e.g. Order + Lines)** | Balanced; standard for business transactions | Natural for parent-child lifecycles | Standard foreign key relational mapping |
| **Large (God Aggregate)** | Catastrophic; frequent deadlocks & timeouts | Enforces massive global rules | High risk of transaction failure and slow queries |

## Worked Example

### Testing Optimistic Concurrency on Product Aggregate

```python
# test_concurrency.py - Testing race condition handling
import threading
import pytest
from unit_of_work import SqlAlchemyUnitOfWork
import services

def run_allocation(sku, orderid, session_factory, exceptions):
    try:
        uow = SqlAlchemyUnitOfWork(session_factory)
        services.allocate(orderid, sku, 1, uow)
    except Exception as e:
        exceptions.append(e)

def test_concurrent_allocations_to_same_product_trigger_retry(session_factory):
    # Setup single batch with 1 quantity
    setup_uow = SqlAlchemyUnitOfWork(session_factory)
    with setup_uow:
        setup_uow.products.add(
            model.Product("RACE-CHAIR", [model.Batch("b1", "RACE-CHAIR", 1, None)])
        )
        setup_uow.commit()

    exceptions = []
    # Spin up two concurrent allocation threads attempting to claim the same unit
    t1 = threading.Thread(target=run_allocation, args=("RACE-CHAIR", "o1", session_factory, exceptions))
    t2 = threading.Thread(target=run_allocation, args=("RACE-CHAIR", "o2", session_factory, exceptions))
    
    t1.start(); t2.start()
    t1.join(); t2.join()

    # One succeeds, one fails with optimistic locking or OutOfStock
    assert len(exceptions) == 1
```

## Key Takeaways
1. An Aggregate is a cluster of domain objects treated as a cohesive unit for data modifications, bounded by an Aggregate Root.
2. The Aggregate Root is the exclusive entry point for modifying internal state and enforcing business invariants.
3. Apply the rule "One Aggregate = One Repository": repositories load and save Aggregate Roots only.
4. Keep aggregates as small as possible to maximize concurrency and minimize database contention.
5. Use version numbers on Aggregate Roots for optimistic concurrency control, preventing concurrent overwrites without table-wide locks.
6. Respect Bounded Contexts: model only the data and behavior needed for your specific domain problem.

## Connects To
- **Ch 01**: Domain Modeling — where entities and value objects are first formed before grouping into aggregates.
- **Ch 06**: Unit of Work — commits aggregate changes atomically and checks version numbers.
- **Ch 08**: Events and the Message Bus — how aggregates communicate state changes to other aggregates without violating consistency boundaries.
