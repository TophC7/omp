# Chapter 2: Repository Pattern

## Core Idea
The Repository pattern is an abstraction over persistent data storage that presents the illusion of an in-memory collection, freeing the domain model from database dependencies and enabling rapid testing with in-memory doubles.

## Frameworks Introduced
- **The Repository Pattern**: An architectural adapter sitting between the domain model and persistent storage.
  - When to use: When retrieving or persisting domain model entities without coupling domain logic to database queries, SQL dialects, or ORM mechanics.
  - How:
    1. Define an interface (`AbstractRepository`) with `add(entity)` and `get(id)` methods.
    2. Implement a production adapter (`SqlAlchemyRepository`) backed by a database session.
    3. Implement an in-memory test double (`FakeRepository`) backed by a Python set or dict.
    4. Pass the repository abstraction into application use cases.
  - Why it works: High-level business logic only interacts with collection semantics (`add`, `get`), making the database a pluggable detail and enabling millisecond unit tests without SQLite or PostgreSQL.
  - Failure mode: Adding complex query-builder logic, eager-loading options, or leaking SQL expressions through repository method signatures.

- **Imperative (Classical) ORM Mapping**: Explicitly binding database tables to pure domain classes without having domain classes inherit from ORM base classes.
  - When to use: When using an ORM like SQLAlchemy while preserving pure domain model persistence ignorance.
  - How:
    1. Define domain classes as pure Python classes with no framework imports.
    2. Define database schemas separately using `Table` and `Column` definitions.
    3. Call `mapper_registry.map_imperatively(DomainClass, table)` at application bootstrap.
  - Why it works: Keeps the domain model clean of ORM decorators, foreign key definitions, and table annotations.
  - Failure mode: Modifying domain attributes specifically to satisfy ORM column constraints or relationship configurations.

- **The Fake Repository Pattern**: An in-memory implementation of the repository interface designed specifically for unit testing.
  - When to use: In all unit tests for service layers and business workflows that need to load and save entities.
  - How:
    1. Subclass `AbstractRepository` or conform to the repository protocol.
    2. Store items in a private set (`self._batches = set(items)`).
    3. Implement `add()` with `set.add()` and `get()` with `next((x for x in self._batches if ...), None)`.
  - Why it works: Executes in memory with zero I/O, zero database setup, and instant execution.

## Key Concepts
- **Persistence Ignorance**: The architectural property where domain objects have no awareness of how, where, or whether they are persisted to durable storage.
- **Port (Interface)**: The abstract definition of an external capability (e.g., `AbstractRepository`).
- **Adapter (Implementation)**: A concrete implementation of a port for a specific technology (e.g., `SqlAlchemyRepository` or `FakeRepository`).
- **Collection Illusion**: Designing data access APIs to look like standard Python containers (`list`, `set`, `dict`) where objects are retrieved, modified in memory, and added back.
- **Commit Responsibility**: Keeping transaction commit boundaries (`session.commit()`) outside the repository to allow multiple repository mutations within one atomic unit.
- **Integration Test vs. Unit Test**: Unit tests verify domain logic with fakes; integration tests verify that production repository adapters correctly execute SQL against real database engines.

## Mental Models
- **In-Memory Collection**: Think of a repository as an infinite Python `set` that happens to be backed by a disk; you fetch an object, modify it, and let the system handle persistence.
- **Onion Architecture / Hexagonal Ports & Adapters**: The domain model sits at the center; the database is an outer adapter pointing inward to the repository port.
- **Swap the Abstraction**: You are not adding unnecessary code; you are replacing a complex, vendor-specific abstraction (`session.query(Batch).filter(...)`) with a lean, domain-tailored abstraction (`repo.get(ref)`).

## Anti-patterns
- **Active Record Coupling**: Having domain model entities inherit from an ORM base (like Django `models.Model` or SQLAlchemy `declarative_base()`), entangling business calculations with table definitions.
- **Leaky Repository Queries**: Exposing raw queries, querysets, or SQL criteria across repository methods (e.g., `repo.get_by_filter(filter_expr)`), which leaks relational concerns into callers.
- **Auto-Committing Repositories**: Calling `session.commit()` inside repository `add()` or `get()` methods, preventing atomic transactions across multiple aggregates.
- **Generic CRUD Repository Bloat**: Adding dozens of specialized finder methods (`find_by_sku_and_status_and_created_after`) instead of keeping the repository interface focused on core identity lookup.

## Code Examples

### SQLAlchemy Classical (Imperative) Mapping

Pure domain model (zero database imports):
```python
# model.py - Completely pure Python
from dataclasses import dataclass
from typing import Optional, Set
from datetime import date

@dataclass(frozen=True)
class OrderLine:
    orderid: str
    sku: str
    qty: int

class Batch:
    def __init__(self, ref: str, sku: str, qty: int, eta: Optional[date] = None):
        self.reference = ref
        self.sku = sku
        self.eta = eta
        self._purchased_quantity = qty
        self._allocations: Set[OrderLine] = set()
```

Separated database schema mapping:
```python
# orm.py - Infrastructure layer
from sqlalchemy import Table, MetaData, Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import registry, relationship
import model

mapper_registry = registry()
metadata = MetaData()

order_lines = Table(
    "order_lines",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("sku", String(255)),
    Column("qty", Integer, nullable=False),
    Column("orderid", String(255)),
)

batches = Table(
    "batches",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("reference", String(255)),
    Column("sku", String(255)),
    Column("_purchased_quantity", Integer, nullable=False),
    Column("eta", Date, nullable=True),
)

allocations = Table(
    "allocations",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("orderline_id", Integer, ForeignKey("order_lines.id")),
    Column("batch_id", Integer, ForeignKey("batches.id")),
)

def start_mappers():
    lines_mapper = mapper_registry.map_imperatively(model.OrderLine, order_lines)
    mapper_registry.map_imperatively(
        model.Batch,
        batches,
        properties={
            "_allocations": relationship(
                lines_mapper,
                secondary=allocations,
                collection_class=set,
            )
        },
    )
```
- **What it demonstrates**: The domain class remains 100% agnostic of tables; relationship mapping uses private attribute `_allocations` to bind the secondary join table into a Python set.

### Abstract and Concrete Repositories

```python
# repository.py
import abc
from typing import List, Optional
from sqlalchemy.orm import Session
import model

class AbstractRepository(abc.ABC):
    @abc.abstractmethod
    def add(self, batch: model.Batch) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def get(self, reference: str) -> Optional[model.Batch]:
        raise NotImplementedError

    @abc.abstractmethod
    def list(self) -> List[model.Batch]:
        raise NotImplementedError

class SqlAlchemyRepository(AbstractRepository):
    def __init__(self, session: Session):
        self.session = session

    def add(self, batch: model.Batch) -> None:
        self.session.add(batch)

    def get(self, reference: str) -> Optional[model.Batch]:
        return self.session.query(model.Batch).filter_by(reference=reference).one_or_none()

    def list(self) -> List[model.Batch]:
        return self.session.query(model.Batch).all()
```
- **What it demonstrates**: Concrete implementation delegates directly to SQLAlchemy session while restricting the interface to minimal collection primitives.

## Reference Tables

### Trade-offs of the Repository Pattern

| Pros | Cons |
|---|---|
| Domain model completely decoupled from database schema and SQL | Adds an extra layer of abstraction and code files |
| Easy to write blindingly fast unit tests with `FakeRepository` | Writing mappers for complex nested object graphs requires ORM expertise |
| Seamlessly change storage engine (SQL, MongoDB, CSV) | Maintaining explicit mappers takes extra setup compared to active record |
| Universal design pattern recognizable across DDD practitioners | Easy for junior engineers to accidentally leak queries into repository methods |

## Worked Example

### Building and Testing with FakeRepository

```python
# In-memory test double
class FakeRepository(AbstractRepository):
    def __init__(self, batches=None):
        self._batches = set(batches or [])

    def add(self, batch: model.Batch) -> None:
        self._batches.add(batch)

    def get(self, reference: str) -> Optional[model.Batch]:
        return next((b for b in self._batches if b.reference == reference), None)

    def list(self) -> List[model.Batch]:
        return list(self._batches)

# Service function under test (pure business coordination)
def allocate_service(orderid: str, sku: str, qty: int, repo: AbstractRepository) -> str:
    line = model.OrderLine(orderid, sku, qty)
    batches = repo.list()
    batchref = model.allocate(line, batches)
    return batchref

# Lightning-fast unit test with zero database setup:
def test_allocate_service_with_fake_repository():
    repo = FakeRepository([
        model.Batch("b1", "COMPACT-DESK", 10, eta=None),
        model.Batch("b2", "COMPACT-DESK", 10, eta=None),
    ])
    
    result = allocate_service("order-01", "COMPACT-DESK", 2, repo)
    
    assert result == "b1"
    batch = repo.get("b1")
    assert batch.available_quantity == 8
```

## Key Takeaways
1. The Repository pattern is a simplifying abstraction that hides database complexities behind a collection-like interface.
2. The core repository interface needs only `add()` and `get()` (and occasionally `list()`).
3. Use SQLAlchemy's classical/imperative mapping to bind database tables to domain models without forcing domain classes to inherit from ORM bases.
4. Keep transaction commit responsibility (`session.commit()`) outside the repository to enable multi-aggregate transactions.
5. Create a `FakeRepository` backed by Python sets or dicts to make service-layer unit tests fast, isolated, and deterministic.

## Connects To
- **Ch 01**: Domain Model — the entities loaded and saved via the repository.
- **Ch 04**: Service Layer — the primary consumer of repository instances.
- **Ch 06**: Unit of Work — coordinates multiple repositories and manages the transaction commit boundary.
