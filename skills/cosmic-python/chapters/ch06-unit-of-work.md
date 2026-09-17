# Chapter 6: Unit of Work Pattern

## Core Idea
The Unit of Work (UoW) pattern provides an abstraction over atomic operations and database transactions, using Python's context manager syntax to coordinate repositories, ensure consistency, and roll back uncommitted changes by default.

## Frameworks Introduced
- **The Unit of Work Pattern (UoW)**: The single entry point to persistent storage that tracks business changes and commits them atomically.
  - When to use: When executing a use case that modifies one or more aggregates across one or more repositories within an atomic transaction.
  - How:
    1. Define an `AbstractUnitOfWork` with `__enter__`, `__exit__`, `commit()`, and `rollback()` methods.
    2. Expose repository instances as attributes on the UoW (e.g., `uow.batches`, `uow.products`).
    3. Implement `__exit__` to automatically roll back any uncommitted changes if an exception occurs or if `commit()` was not called.
    4. Pass the UoW into the service layer as a context manager (`with uow:`).
  - Why it works: Decouples the service layer from database sessions, provides a stable transactional snapshot, and guarantees atomic completion.
  - Failure mode: Leaving database connections open or forgetting to close sessions in `__exit__`.

- **Don't Mock What You Don't Own**: A testing and architectural rule of thumb warning against mocking third-party libraries and vendor frameworks.
  - When to use: When interacting with external frameworks, drivers, and databases (SQLAlchemy, Boto3, Stripe, Redis).
  - How:
    1. Wrap the external tool behind a domain-specific abstraction (like `AbstractRepository` or `AbstractUnitOfWork`).
    2. Write a minimal set of integration tests against the real external tool to prove your adapter works.
    3. Test all higher-level application logic using in-memory fakes of your *own* abstraction (`FakeUnitOfWork`).
  - Why it works: Mocking third-party APIs couples tests to external implementation details and creates false confidence; faking your own abstraction tests real application contracts.

- **Rollback by Default / Explicit Commit**:
  - All transactions opened within a UoW context manager must be explicitly committed (`uow.commit()`).
  - Exiting the context block without an explicit commit (due to an error, early return, or exception) automatically triggers a rollback.
  - Prevents partial, corrupted, or accidental writes from reaching persistent storage.

## Key Concepts
- **Atomic Operation (Atomicity)**: An operation where a series of database modifications all succeed together or fail completely, leaving state unchanged.
- **Context Manager**: A Python construct (`with statement`) managing resources through `__enter__` (setup) and `__exit__` (teardown).
- **Session Factory**: A callable (like SQLAlchemy's `sessionmaker`) that produces new database sessions on demand.
- **Collaborator / Object Neighborhood**: A cluster of objects (e.g., `UnitOfWork` and `Repository`) designed to work together to fulfill a cohesive architectural role.
- **FakeUnitOfWork**: An in-memory implementation of the UoW interface holding a `FakeRepository` and tracking `self.committed = True`.

## Mental Models
- **The Safe Deposit Box**: Entering `with uow:` opens the vault door; you read documents, alter them, and replace them; calling `uow.commit()` locks the changes into the vault; leaving without calling commit causes the vault to shred your scratchpad and restore the originals.
- **Single Leash on the Database**: Instead of the web controller, service layer, and repository all holding separate references to the database session, only the Unit of Work touches the database session directly.
- **Transaction as a Scope**: Code within the `with uow:` block operates on a consistent snapshot of state; exit marks the boundary of durability.

## Anti-patterns
- **Mocking SQLAlchemy Sessions**: Patching `session.query()` or `session.commit()` inside unit tests, resulting in unreadable, brittle mocks of someone else's library.
- **Multiple Session Management**: Instantiating and committing separate sessions within a single use case, destroying transaction atomicity.
- **Implicit Commits on Exit**: Automatically committing when exiting the context manager, which accidentally commits half-completed transactions when bugs occur.
- **Direct Database Access in Controllers**: Instantiating database connections and executing queries directly inside HTTP view functions.

## Code Examples

### Abstract Unit of Work Interface

```python
# unit_of_work.py
import abc
import repository

class AbstractUnitOfWork(abc.ABC):
    batches: repository.AbstractRepository

    def __enter__(self) -> "AbstractUnitOfWork":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.rollback()

    @abc.abstractmethod
    def commit(self) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def rollback(self) -> None:
        raise NotImplementedError
```
- **What it demonstrates**: Context manager structure with `rollback()` on exit by default, and abstract `commit()` requirement.

### SQLAlchemy Unit of Work Implementation

```python
# unit_of_work.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
import repository
import config

DEFAULT_SESSION_FACTORY = sessionmaker(
    bind=create_engine(config.get_postgres_uri())
)

class SqlAlchemyUnitOfWork(AbstractUnitOfWork):
    def __init__(self, session_factory=DEFAULT_SESSION_FACTORY):
        self.session_factory = session_factory

    def __enter__(self) -> AbstractUnitOfWork:
        self.session: Session = self.session_factory()
        self.batches = repository.SqlAlchemyRepository(self.session)
        return super().__enter__()

    def __exit__(self, *args) -> None:
        super().__exit__(*args)
        self.session.close()

    def commit(self) -> None:
        self.session.commit()

    def rollback(self) -> None:
        self.session.rollback()
```
- **What it demonstrates**: Concrete adapter managing session lifecycle: opens session and repository on enter, closes session on exit, commits and rolls back.

### Service Layer Refactored with Unit of Work

```python
# services.py
import model
from unit_of_work import AbstractUnitOfWork

class InvalidSku(Exception):
    pass

def allocate(
    orderid: str,
    sku: str,
    qty: int,
    uow: AbstractUnitOfWork,
) -> str:
    line = model.OrderLine(orderid, sku, qty)
    with uow:
        batches = uow.batches.list()
        if not any(b.sku == line.sku for b in batches):
            raise InvalidSku(f"Invalid sku {line.sku}")
        
        batchref = model.allocate(line, batches)
        uow.commit()
        return batchref
```
- **What it demonstrates**: The service layer has exactly one dependency: the abstract UoW. Zero direct database or session references.

## Reference Tables

### Comparing Session Management Approaches

| Approach | Coupling | Testability | Failure Safety |
|---|---|---|---|
| **Direct Session in Views** | High; Presentation tied to DB | Poor; requires database or extreme mocking | Low; partial commits frequent |
| **Session Passed to Service** | Medium; Service tied to ORM session | Moderate; requires `FakeSession` | Medium; commit responsibility ambiguous |
| **Unit of Work Pattern** | Minimal; Service depends on abstract UoW | Excellent; fast in-memory `FakeUnitOfWork` | High; atomic commit with automatic rollback |

## Worked Example

### Testing Services with FakeUnitOfWork

```python
# test_services.py
from repository import AbstractRepository
from unit_of_work import AbstractUnitOfWork
import services
import model
import pytest

class FakeRepository(AbstractRepository):
    def __init__(self, batches=None):
        self._batches = set(batches or [])
    def add(self, batch):
        self._batches.add(batch)
    def get(self, reference):
        return next((b for b in self._batches if b.reference == reference), None)
    def list(self):
        return list(self._batches)

class FakeUnitOfWork(AbstractUnitOfWork):
    def __init__(self):
        self.batches = FakeRepository([])
        self.committed = False

    def commit(self):
        self.committed = True

    def rollback(self):
        pass

def test_allocate_commits_transaction():
    uow = FakeUnitOfWork()
    uow.batches.add(model.Batch("b1", "COMPACT-DESK", 100, eta=None))

    result = services.allocate("o1", "COMPACT-DESK", 10, uow)

    assert result == "b1"
    assert uow.committed is True

def test_rolls_back_on_error():
    uow = FakeUnitOfWork()
    uow.batches.add(model.Batch("b1", "REAL-SKU", 100, eta=None))

    with pytest.raises(services.InvalidSku):
        services.allocate("o1", "NONEXISTENT", 10, uow)

    assert uow.committed is False
```

## Key Takeaways
1. The Unit of Work pattern is the architectural abstraction over atomic database transactions and session lifecycle.
2. Use Python context managers (`__enter__` and `__exit__`) to make the start, commit, and rollback of transactions clean and idiomatic.
3. Apply "Rollback by default": every transaction rolls back upon exit unless `commit()` is called explicitly.
4. "Don't mock what you don't own": abstract messy third-party libraries (SQLAlchemy) behind your own ports, and fake your own ports.
5. The Service Layer depends solely on `AbstractUnitOfWork`, which collaborates with repositories to complete use cases.

## Connects To
- **Ch 02**: Repository Pattern — repositories are exposed as attributes on the Unit of Work.
- **Ch 04**: Service Layer — the primary consumer of the Unit of Work context manager.
- **Ch 07**: Aggregates — the Unit of Work defines the consistency boundary across which changes to aggregates are committed.
