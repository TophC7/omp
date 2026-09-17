# Chapter 12: Command-Query Responsibility Segregation (CQRS)

## Core Idea
Reads and writes have fundamentally different access patterns, performance constraints, and consistency requirements; segregating them allows commands to focus exclusively on enforcing domain invariants while queries bypass the domain model entirely to read directly from optimized read stores.

## Frameworks Introduced
- **Command-Query Responsibility Segregation (CQRS)**: Separating the data mutation path (Commands) from the data retrieval path (Queries) across the application architecture.
  - When to use: When read volume dwarfs write volume, when read queries require complex joins across multiple aggregates, or when query performance needs optimization without compromising domain boundaries.
  - How:
    1. *Write Path*: Commands → Message Bus → Command Handlers → Unit of Work → Aggregates → Commit.
    2. *Read Path*: Queries → `views.py` → Raw SQL / View Tables / Cache → Serialized JSON Dictionaries.
    3. Remove query methods from domain aggregates and repositories.
  - Why it works: Domain models exist solely to enforce consistency during state changes; reads do not mutate state and need no invariant protection, so hydrating rich domain objects for reads wastes memory and CPU.
  - Failure mode: Forcing every read query through the write pipeline (loading aggregates into memory just to read two fields).

- **Command-Query Separation (CQS) at the API Level**:
  - Functions that change state should not return data; functions that return data should not change state ("asking questions shouldn't flick the light switch").
  - Mutating API endpoints (e.g., `POST /allocate`) return `202 Accepted` or `201 Created` with empty bodies or a resource URL header.
  - Reading API endpoints (e.g., `GET /allocations/<orderid>`) handle retrieval independently.
  - Eliminates the hack of returning business query results from message bus command handlers.

- **Event-Driven Read Projections (View Tables)**:
  - Create a denormalized table (e.g., `allocations_view`) tailored specifically to query needs.
  - Subscribe read-model updater handlers to domain events:
    - On `events.Allocated`: `INSERT INTO allocations_view VALUES (:orderid, :sku, :batchref)`.
    - On `events.Deallocated`: `DELETE FROM allocations_view WHERE orderid = :orderid AND sku = :sku`.
  - Queries against the view table require zero joins, zero ORM hydration, and execute in sub-milliseconds.

## Key Concepts
- **Read Model**: A data structure or storage representation optimized exclusively for querying and reporting.
- **Write Model**: The domain model (aggregates, entities, value objects) optimized for consistency and invariant enforcement.
- **Hydration**: The process of taking raw database rows and converting them into in-memory domain entity objects.
- **Denormalization**: Duplicating or pre-joining relational data into flat tables to eliminate SQL joins during read queries.
- **Eventual Consistency in Reads**: Accepting that a read query might reflect data that is a few milliseconds or seconds behind the latest write transaction in exchange for massive read throughput.

## Mental Models
- **Ask vs. Tell**: Tell the system to change state with a Command; Ask the system what its state is with a Query.
- **The Ledger vs. The Billboard**: The write model is an accountant's audited ledger (every row checked against strict rules); the read model is a billboard on the highway (large, fast, easy to read, painted after the ledger updates).
- **Two Roads Diverged**: Commands travel down the paved, gated highway of Aggregates and UoWs; Queries take the high-speed transit tunnel straight to the data warehouse.

## Anti-patterns
- **Repository Finder Explosion**: Adding dozens of specialized query methods (`find_by_customer_and_date_range_with_items`) to domain repositories, bloating write abstractions with read concerns.
- **Loading Full Aggregates for Display**: Hydrating a giant aggregate with 50 child entities just to display an order total and customer status on a webpage.
- **Command Methods Returning Complex DTOs**: Returning full domain representations from commands, entangling mutation workflows with query serialization.
- **Synchronous View Table Locks**: Locking write transactions while updating multiple secondary read tables synchronously.

## Code Examples

### Direct Raw SQL View (Bypassing Domain Model)

```python
# views.py - Read Model Layer
from typing import List, Dict
from unit_of_work import SqlAlchemyUnitOfWork

def allocations(orderid: str, uow: SqlAlchemyUnitOfWork) -> List[Dict[str, str]]:
    with uow:
        rows = uow.session.execute(
            """
            SELECT ol.sku, b.reference AS batchref
            FROM allocations AS a
            JOIN batches AS b ON a.batch_id = b.id
            JOIN order_lines AS ol ON a.orderline_id = ol.id
            WHERE ol.orderid = :orderid
            """,
            dict(orderid=orderid),
        )
    return [{"sku": row.sku, "batchref": row.batchref} for row in rows]
```
- **What it demonstrates**: Bypasses the domain model and repository entirely; executes raw SQL and returns plain dicts directly.

### Event-Driven Read Projection (View Table)

Updating read table in response to domain events:
```python
# handlers.py - Read Model Event Handlers
import events
from unit_of_work import SqlAlchemyUnitOfWork

def add_allocation_to_read_model(event: events.Allocated, uow: SqlAlchemyUnitOfWork) -> None:
    with uow:
        uow.session.execute(
            """
            INSERT INTO allocations_view (orderid, sku, batchref)
            VALUES (:orderid, :sku, :batchref)
            """,
            dict(orderid=event.orderid, sku=event.sku, batchref=event.batchref),
        )
        uow.commit()

def remove_allocation_from_read_model(event: events.Deallocated, uow: SqlAlchemyUnitOfWork) -> None:
    with uow:
        uow.session.execute(
            """
            DELETE FROM allocations_view
            WHERE orderid = :orderid AND sku = :sku
            """,
            dict(orderid=event.orderid, sku=event.sku),
        )
        uow.commit()
```

Reading from the denormalized projection:
```python
# views.py - Single-table flat read
def allocations(orderid: str, uow: SqlAlchemyUnitOfWork) -> List[Dict[str, str]]:
    with uow:
        rows = uow.session.execute(
            "SELECT sku, batchref FROM allocations_view WHERE orderid = :orderid",
            dict(orderid=orderid),
        )
    return [{"sku": r.sku, "batchref": r.batchref} for r in rows]
```
- **What it demonstrates**: Zero joins during reads; the view table is kept in sync by event handlers.

## Reference Tables

### Evolution of Read Strategies

| Approach | Implementation | Pros | Cons |
|---|---|---|---|
| **1. Via Repository** | `uow.products.for_order(orderid)` | Keeps single abstraction | Terrible performance; bloats repository with query methods |
| **2. Via ORM Query** | `session.query(Batch)...` | Flexible query building | Couples reads to ORM mapping classes and relationship configs |
| **3. Raw SQL in Views** | `session.execute(SELECT ... JOIN ...)` | High performance; no domain coupling | Complex queries require SQL joins on normalized tables |
| **4. Event-Driven Projection** | `SELECT FROM allocations_view` | Maximum speed; zero joins; flat schema | Eventual consistency; storage duplication; handler maintenance |

## Worked Example

### End-to-End Test of Separated Read & Write Endpoints

```python
# tests/e2e/test_api.py - Demonstrating CQS at the HTTP level
import pytest
from . import api_client

def test_cqs_post_then_get_allocation():
    orderid = "order-999"
    sku = "COMFORTABLE-CHAIR"
    
    # 1. Setup inventory
    api_client.post_to_add_batch("batch-chair", sku, qty=5, eta=None)

    # 2. Command: POST to allocate returns 202 Accepted (no body content)
    post_resp = api_client.post_to_allocate(orderid, sku, qty=2)
    assert post_resp.status_code == 202

    # 3. Query: GET allocation details from dedicated read endpoint
    get_resp = api_client.get_allocation(orderid)
    assert get_resp.status_code == 200
    assert get_resp.json() == [
        {"sku": sku, "batchref": "batch-chair"}
    ]
```

## Key Takeaways
1. Domain models exist to protect invariants during writes; queries do not mutate state and should bypass the domain model.
2. Command-Query Separation (CQS) dictates that an operation either mutates state or returns data, never both.
3. Raw SQL queries in dedicated `views.py` modules offer high performance and clear architectural separation without complex ORM mappings.
4. Event-Driven Read Projections use domain event listeners to maintain denormalized view tables that serve reads with zero joins.
5. Embracing eventual consistency for queries enables massive read scalability without compromising transactional write safety.

## Connects To
- **Ch 07**: Aggregates — the write-model consistency boundaries that CQRS protects from query pollution.
- **Ch 10**: Commands and Command Handlers — the write side of the CQRS divide.
- **Ch 13**: Dependency Injection — wiring up distinct read and write dependencies cleanly at application startup.
