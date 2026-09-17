# Chapter 5: TDD in High Gear and Low Gear

## Core Idea
Automated tests act as structural glue: low-level tests against domain models offer rich design feedback but resist refactoring, while high-level tests against the service layer provide high coverage with low coupling; shifting between "low gear" (domain exploration) and "high gear" (service-layer features) balances rapid iteration with architectural freedom.

## Frameworks Introduced
- **The Bicycle Gears Metaphor (High Gear vs. Low Gear TDD)**:
  - *Low Gear (Domain Model Tests)*:
    - When to use: When starting a new project, exploring an unfamiliar business domain, or solving a gnarly algorithmic problem.
    - How: Write fine-grained unit tests directly against domain entities, value objects, and domain services (`test_batches.py`).
    - Characteristics: Fast feedback, tight design guidance, living documentation; high coupling to domain signatures.
  - *High Gear (Service-Layer Tests)*:
    - When to use: When adding standard features, expanding existing use cases, or fixing bugs in an established domain.
    - How: Write tests exclusively against the service layer using primitives and `FakeRepository` (`test_services.py`).
    - Characteristics: Low coupling to internal model structures, freedom to radically refactor domain entities without breaking tests.

- **The Test Glue Principle**:
  - Every assertion and line of setup code in a test binds the system to an exact structural shape.
  - Tests written against internal entity attributes freeze implementation details and penalize future refactoring.
  - Prefer testing observable behavior through public service-layer APIs to minimize accidental coupling.

- **Driving Service Tests Through Services (Complete Decoupling)**:
  - Instead of instantiating domain models (`Batch(...)`) to set up test state, invoke service-layer functions (`services.add_batch(...)`).
  - The test suite interacts with the application strictly as an external client using primitives, making the domain model an internal implementation detail.

- **Test Pyramid Rules of Thumb**:
  1. *One E2E smoke test per feature*: Verify routing, HTTP codes, and database wiring.
  2. *Bulk of tests at the Service Layer*: Fast unit tests using `FakeRepository` covering happy paths, edge cases, and validation rules.
  3. *Domain tests for complex invariants*: Retain low-gear unit tests for intricate business algorithms that benefit from fine-grained specification.
  4. *Integration tests for adapters*: Dedicated tests verifying that SQLAlchemy mappers and repositories correctly interact with the real database.

## Key Concepts
- **Test Glue**: The degree to which automated tests freeze internal code structures, making refactoring expensive.
- **Design Feedback**: The guidance test-driven development provides about API ergonomics, responsibility boundaries, and code smells.
- **System Coverage**: The breadth of application subsystems (routing, services, domain, persistence) exercised by a single test.
- **Living Documentation**: Executable unit tests written in domain language that illustrate system rules for engineers.
- **Setup Decoupling**: Structuring test fixtures so changes to domain entity constructors do not ripple across dozens of service tests.

## Mental Models
- **Shifting Bicycle Gears**: Climb steep, difficult hills of unknown business logic in low gear (domain tests); cruise smoothly and quickly on open roads in high gear (service tests).
- **Ice-Cream Cone vs. Pyramid**: Invert the fragile ice-cream cone (thousands of slow E2E tests, few unit tests) into a stable pyramid (many fast service/domain tests, few E2E tests).
- **The Black Box Boundary**: Treat the service layer as the boundary of a black box; everything inside (domain entities, aggregates, relationships) can be re-architected freely as long as the service API contract holds.

## Anti-patterns
- **Over-testing Internal Domain Details**: Writing hundreds of micro-tests asserting on private attributes or temporary helper methods, creating a massive barrier to domain refactoring.
- **Domain Coupling in Service Test Fixtures**: Instantiating domain entities directly in service-layer tests, causing changes in domain constructors to break unrelated service tests.
- **Mock-Driven High Gear**: Attempting high-gear testing by patching repositories with mocks instead of using real `FakeRepository` implementations.
- **E2E Obsession**: Writing full-stack HTTP tests for every edge case and validation error, resulting in multi-hour CI pipelines and flaky test runs.

## Code Examples

### Shifting from Low Gear to High Gear

Low Gear: Directly testing domain entities (tightly coupled to `Batch` attributes):
```python
# test_batches.py (Low Gear)
def test_allocating_to_a_batch_reduces_available_quantity():
    batch = Batch("batch-001", "RETRO-LAMP", qty=20, eta=date.today())
    line = OrderLine("order-123", "RETRO-LAMP", 2)
    batch.allocate(line)
    assert batch.available_quantity == 18
```
- **Trade-off**: High feedback during initial design; breaks if `Batch` internal structure changes.

High Gear: Testing use case through service layer with primitives:
```python
# test_services.py (High Gear)
def test_allocating_reduces_available_quantity():
    repo = FakeRepository()
    session = FakeSession()

    # Setup via service layer (pure primitives)
    services.add_batch("batch-001", "RETRO-LAMP", 20, None, repo, session)

    # Action via service layer
    services.allocate("order-123", "RETRO-LAMP", 2, repo, session)

    # Assertion on observable state
    batch = repo.get("batch-001")
    assert batch.available_quantity == 18
```
- **Trade-off**: Lower coupling to constructor details; verifies the complete use case end-to-end in memory.

### Fully Decoupled Service-Layer Tests

```python
# test_services.py - Driving tests completely via services API
import pytest
import services
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

def test_allocate_returns_allocation():
    repo, session = FakeRepository(), FakeSession()
    services.add_batch("b1", "COMPLICATED-LAMP", 100, None, repo, session)

    result = services.allocate("o1", "COMPLICATED-LAMP", 10, repo, session)

    assert result == "b1"

def test_allocate_errors_for_invalid_sku():
    repo, session = FakeRepository(), FakeSession()
    services.add_batch("b1", "AREALSKU", 100, None, repo, session)

    with pytest.raises(services.InvalidSku, match="Invalid sku NONEXISTENTSKU"):
        services.allocate("o1", "NONEXISTENTSKU", 10, repo, session)
```
- **What it demonstrates**: Zero domain classes are imported or instantiated in the test; tests remain valid even if `Batch` is drastically refactored.

## Reference Tables

### Testing Gears Comparison Matrix

| Dimension | Low Gear (Domain Tests) | High Gear (Service Tests) | End-to-End (E2E Tests) |
|---|---|---|---|
| **Target** | `model.py` entities & methods | `services.py` use cases | HTTP API endpoints / Web views |
| **Speed** | Sub-millisecond (instant) | 1–5 milliseconds | 100–1000 milliseconds |
| **Coupling** | High (tied to domain classes) | Low (tied to primitives & service API) | Minimal (tied to HTTP & JSON) |
| **Design Feedback** | Excellent; guides domain modeling | Good; guides workflow design | Poor; black-box only |
| **Refactoring Freedom** | Low; changing models breaks tests | High; domain models can change freely | Maximum; entire backend can change |
| **Ideal Quantity** | For core algorithmic rules | Bulk of test suite | 1 per endpoint / feature |

## Worked Example

### Refactoring Domain Model Without Breaking High-Gear Tests

Suppose we refactor `Batch` to track available quantity via an internal ledger rather than calculated properties.

Because our High-Gear service tests were written in terms of services:
```python
def test_preference_for_warehouse_stock():
    repo, session = FakeRepository(), FakeSession()
    services.add_batch("in-stock", "RETRO-CLOCK", 100, None, repo, session)
    services.add_batch("shipment", "RETRO-CLOCK", 100, "2026-05-01", repo, session)

    allocated_batch = services.allocate("oref", "RETRO-CLOCK", 10, repo, session)

    assert allocated_batch == "in-stock"
```

Result:
- If we refactor `Batch.__init__` or change private allocation sets, this test continues to pass without a single edit.
- If we had 15 low-level domain tests calling `Batch(...)` with old constructor signatures, every single one would have failed and required manual updating.

## Key Takeaways
1. Tests are structural glue: tests that touch private attributes or internal constructors resist refactoring.
2. Use Low Gear (domain tests) to explore complex, unfamiliar business logic and receive immediate design feedback.
3. Shift to High Gear (service tests) for day-to-day feature development to achieve high coverage with low coupling.
4. Drive service tests using primitive types and service-layer helper functions for setup to completely decouple tests from domain classes.
5. Keep the test pyramid healthy: many fast service/domain tests, a modest set of adapter integration tests, and minimal E2E smoke tests.

## Connects To
- **Ch 01**: Domain Modeling — where low-gear testing starts.
- **Ch 04**: Service Layer — the target API for high-gear testing.
- **Ch 06**: Unit of Work Pattern — standardizing session and repository management for clean service testing.
