# Chapter 4: Our First Use Case: Flask API and Service Layer

## Core Idea
The Service Layer (or Application Service Layer) defines the system's use cases by orchestrating workflows—fetching domain objects from repositories, invoking domain rules, and handling persistence—freeing web frameworks from business logic and enabling fast unit testing of complete user stories.

## Frameworks Introduced
- **The Service Layer Pattern (Application Services)**: An architectural layer defining the operational boundary of the application and establishing a set of available operations.
  - When to use: When handling user requests from web endpoints, CLI commands, queue consumers, or scheduled tasks.
  - How:
    1. Extract orchestration code (loading aggregates, validating preconditions, saving changes) from web handlers.
    2. Place functions in a dedicated `services.py` module.
    3. Accept primitive types (`str`, `int`) instead of domain objects to decouple callers from domain models.
    4. Inject abstract dependencies (`repo: AbstractRepository`).
  - Why it works: Web controllers remain thin routing shims; use cases can be executed identically from an API, CLI, or test suite.
  - Failure mode: Leaking business calculations (domain logic) into the service layer, reducing entities to anemic data holders.

- **Domain Services vs. Application Services**:
  - *Domain Service*: Encapsulates a pure business rule or calculation that does not belong to a single entity (e.g., `model.allocate(line, batches)`). Lives in `model.py`, has zero side effects, and knows nothing of repositories or databases.
  - *Application Service (Service Layer)*: Encapsulates a system use case (e.g., `services.allocate(...)`). Lives in `services.py`, orchestrates I/O, loads repositories, coordinates domain services, and manages transaction commits.

- **Primitive-Driven Interfaces**: Designing service layer functions to accept plain Python primitives (`str`, `int`, `dict`) rather than rich domain objects.
  - When to use: On all public entry points of the service layer.
  - How: Pass `orderid: str, sku: str, qty: int` rather than `line: OrderLine`. Let the service instantiate domain objects internally.
  - Why it works: The web/API layer does not need to import or instantiate domain classes, preventing presentation-to-domain coupling.

- **Testing Pyramid Re-alignment**:
  - Replace the inverted "ice-cream cone" test suite (hundreds of slow, flaky E2E tests) with:
    - Broad base: Domain model unit tests (microseconds).
    - Middle tier: Service-layer unit tests with `FakeRepository` (milliseconds, covering all use-case permutations).
    - Tip: Minimal E2E smoke tests (verifying routing, JSON parsing, HTTP status codes).

## Key Concepts
- **Orchestration**: The coordination of external I/O, repository fetching, domain execution, and persistence commits to complete a use case.
- **Use Case**: A sequence of actions performed by the system that yields an observable result of value to an actor.
- **Fat Controller**: An anti-pattern where web routing functions handle authentication, SQL queries, business decisions, JSON parsing, and response formatting in one huge function.
- **Thin Controller**: A web route handler that only parses HTTP requests, calls a service-layer function, and formats the response.
- **FakeSession**: A test double tracking transaction commits (`self.committed = True`) without connecting to a database.
- **Ice-Cream Cone Anti-pattern**: A testing suite dominated by slow, brittle end-to-end and UI tests, with few fast unit tests.

## Mental Models
- **The Conductor of the Orchestra**: The service layer does not play an instrument (it has no business calculations); it directs the musicians (loads from repository, tells domain entities when to act, tells the database when to commit).
- **The Protocol-Agnostic Core**: If your web API were replaced tomorrow by a command-line script or an AMQP queue worker, not a single line of your service layer or domain model should need to change.
- **Primitive Gateway**: The service layer is the border checkpoint where external primitives (JSON strings and integers) are verified and converted into domain citizens (Entities and Value Objects).

## Anti-patterns
- **Fat Controllers / Smart Views**: Writing ORM queries and allocation rules directly inside Flask or Django view functions.
- **Domain Logic Leakage**: Performing business calculations (e.g., subtracting available stock, checking ETAs) inside `services.py` instead of delegating to domain entities.
- **Domain Object Coupling in APIs**: Requiring web route handlers or external callers to construct domain entities (`OrderLine`) before calling service functions.
- **Mocking Repositories in Service Tests**: Using `unittest.mock.patch` to verify `repo.list.assert_called_once()` instead of using a `FakeRepository` with real domain assertions.

## Code Examples

### Thin Flask Route Calling the Service Layer

```python
# flask_app.py - Presentation Layer
from flask import Flask, request, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import repository
import services
import model

app = Flask(__name__)
get_session = sessionmaker(bind=create_engine(config.get_postgres_uri()))

@app.route("/allocate", methods=["POST"])
def allocate_endpoint():
    session = get_session()
    repo = repository.SqlAlchemyRepository(session)

    try:
        # Pass primitives to service layer
        batchref = services.allocate(
            request.json["orderid"],
            request.json["sku"],
            request.json["qty"],
            repo,
            session,
        )
    except (model.OutOfStock, services.InvalidSku) as e:
        return jsonify({"message": str(e)}), 400

    return jsonify({"batchref": batchref}), 201
```
- **What it demonstrates**: The web handler does zero business logic; it extracts JSON primitives, invokes the service layer, and maps exceptions to HTTP status codes.

### Service Layer Implementation with Primitives

```python
# services.py - Application Layer
from typing import Optional
import model
from repository import AbstractRepository

class InvalidSku(Exception):
    pass

def is_valid_sku(sku: str, batches) -> bool:
    return sku in {b.sku for b in batches}

def allocate(
    orderid: str,
    sku: str,
    qty: int,
    repo: AbstractRepository,
    session,
) -> str:
    batches = repo.list()
    if not is_valid_sku(sku, batches):
        raise InvalidSku(f"Invalid sku {sku}")
    
    # Construct domain value object inside the service layer
    line = model.OrderLine(orderid, sku, qty)
    batchref = model.allocate(line, batches)
    session.commit()
    return batchref

def add_batch(
    ref: str,
    sku: str,
    qty: int,
    eta: Optional[str],
    repo: AbstractRepository,
    session,
) -> None:
    repo.add(model.Batch(ref, sku, qty, eta))
    session.commit()
```
- **What it demonstrates**: Service functions accept primitives, coordinate repository loading, invoke the domain model, and manage commits.

## Reference Tables

### Domain Services vs. Application Services

| Dimension | Domain Service (`model.py`) | Application Service (`services.py`) |
|---|---|---|
| **Purpose** | Encapsulates cross-entity business rules | Encapsulates a complete user use case |
| **I/O & Persistence** | Strictly zero I/O; pure memory calculations | Orchestrates I/O, databases, and network adapters |
| **Dependencies** | Domain Entities and Value Objects | Repositories, Database Sessions, Notification Clients |
| **Inputs** | Domain Entities (`Batch`, `OrderLine`) | Primitives (`str`, `int`, `UUID`) |
| **Triggered By** | Application Services | API endpoints, CLI scripts, Message queue consumers |

## Worked Example

### Fast Service-Layer Unit Testing with FakeRepository & FakeSession

```python
# test_services.py - Unit tests for use cases
import pytest
import services
import model
from repository import AbstractRepository

class FakeRepository(AbstractRepository):
    def __init__(self, batches=None):
        self._batches = set(batches or [])

    def add(self, batch):
        self._batches.add(batch)

    def get(self, reference):
        return next((b for b in self._batches if b.reference == reference), None)

    def list(self):
        return list(self._batches)

class FakeSession:
    def __init__(self):
        self.committed = False

    def commit(self):
        self.committed = True

def test_returns_allocation():
    repo = FakeRepository([model.Batch("b1", "COMPACT-DESK", 100, eta=None)])
    session = FakeSession()

    result = services.allocate("o1", "COMPACT-DESK", 10, repo, session)

    assert result == "b1"
    assert session.committed is True

def test_error_for_invalid_sku():
    repo = FakeRepository([model.Batch("b1", "REAL-SKU", 100, eta=None)])
    session = FakeSession()

    with pytest.raises(services.InvalidSku, match="Invalid sku FAKE-SKU"):
        services.allocate("o1", "FAKE-SKU", 10, repo, session)

def test_commits_changes_to_storage():
    repo = FakeRepository([model.Batch("b1", "OMINOUS-MIRROR", 100, eta=None)])
    session = FakeSession()

    services.allocate("o1", "OMINOUS-MIRROR", 10, repo, session)

    assert session.committed is True
```

## Key Takeaways
1. The Service Layer captures application use cases and orchestrates workflows between the outside world and the domain model.
2. Web framework controllers should be thin shims that translate HTTP requests to service calls and service results to HTTP responses.
3. Keep the service layer decoupled from callers by accepting plain primitives (`str`, `int`) instead of requiring domain objects.
4. Clearly separate Domain Services (pure business logic) from Application Services (orchestration and I/O).
5. Use `FakeRepository` and `FakeSession` to push tests down from slow E2E suites to fast, maintainable service-layer unit tests.

## Connects To
- **Ch 02**: Repository Pattern — the storage abstraction consumed by the service layer.
- **Ch 05**: TDD in High Gear and Low Gear — deciding whether to write tests against the service layer or domain model.
- **Ch 06**: Unit of Work Pattern — replacing `FakeSession` with a proper Unit of Work abstraction.
