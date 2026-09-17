# Architecture Patterns with Python — Cheatsheet & Decision Guide

## 1. Core Decision Rules

- **When modeling immutable data or measurements**, use a **Value Object** (`@dataclass(frozen=True)` or `NamedTuple`), because values lack independent lifecycle and compare by structural equality.
- **When modeling objects whose state evolves over time**, define an **Entity** with persistent identity (`__eq__` compares `self.reference == other.reference` and `__hash__ = None`), because two entities with identical attributes are distinct physical objects if their IDs differ.
- **When persisting domain entities**, define an `AbstractRepository` and map tables imperatively (`mapper_registry.map_imperatively`), because domain models must maintain total persistence ignorance.
- **When designing service layer APIs**, accept plain primitives (`str`, `int`, `dict`) rather than rich domain classes, because external callers (web views, CLI) should not be coupled to domain constructors.
- **When coordinating database updates**, wrap operations in a **Unit of Work** context manager (`with uow:`) with rollback by default, because multiple repository changes must succeed or fail as an atomic transaction.
- **When enforcing business invariants under concurrency**, draw a boundary around a single **Aggregate Root** and use a `version_number` (optimistic locking), because locking entire database tables destroys scalability.
- **When an aggregate state change requires secondary side effects** (emails, audit logs, broker publishing), append a **Domain Event** and flush it via the **Message Bus** *after* commit, because side effects must never trigger if database transactions roll back.
- **When defining application messages**:
  - Use a **Command** (imperative, 1-to-1) when requesting state mutation; fail fast and noisily.
  - Use an **Event** (past tense, 1-to-many) when broadcasting facts; fail listeners independently without crashing the caller.
- **When retrieving data for display or reports**, bypass the domain model and repository entirely and query raw SQL or denormalized view tables in `views.py`, because reads do not enforce invariants and hydrating aggregates wastes memory and CPU.
- **When wiring system dependencies**, centralize configuration and dependency injection in `bootstrap.py` using closures or signature inspection, because entry points must remain thin transport adapters.

---

## 2. Decision Tree: Where Does This Code Belong?

```text
Is this code about to be written?
│
├── Pure business calculation or rule?
│   ├── Touches attributes of one entity? ────────────► Method on Entity (model.py)
│   ├── Touches multiple entities in same cluster? ──► Method on Aggregate Root (model.py)
│   └── Cross-aggregate calculation with no home? ────► Domain Service function (model.py)
│
├── Orchestrating a use case (fetching, deciding, committing)?
│   └── Handling a Command or Event? ─────────────────► Command/Event Handler (handlers.py)
│
├── Reading data for display, export, or HTTP GET?
│   └── Does it mutate state?
│       ├── NO ───────────────────────────────────────► Raw SQL / View Projection (views.py)
│       └── YES ──────────────────────────────────────► Reject! Apply CQS (Split into POST + GET)
│
├── Talking to external infrastructure (DB, Redis, Email)?
│   ├── Driving the app from outside (HTTP, CLI)? ────► Primary Entrypoint (entrypoints/)
│   └── Driven by the app to do I/O (SQL, SMTP)? ────► Secondary Adapter (adapters/)
│
└── Wiring components together at startup? ───────────► Composition Root (bootstrap.py)
```

---

## 3. Trade-off Matrices

### Testing Gears Matrix

| Testing Strategy | Target Layer | Execution Speed | Refactoring Freedom | Best Used For |
|---|---|---|---|---|
| **Low Gear (Domain)** | `model.py` | Sub-millisecond | Low (glued to entities) | New domain design, complex algorithms |
| **High Gear (Service)** | `handlers.py` via Bus | 1–5 milliseconds | High (glued to primitives) | Day-to-day features, bugfixes, workflows |
| **Integration** | `adapters/`, `views.py`| 10–50 milliseconds| Medium (glued to SQL/DB) | ORM mappings, repositories, raw SQL views |
| **End-to-End (E2E)** | HTTP APIs / Queues | 100–1000 ms | Maximum (black box) | Smoke tests, routing, JSON parsing |

### Read Architecture Selection

| Approach | Query Latency | Implementation Cost | Data Freshness | Best Used For |
|---|---|---|---|---|
| **Raw SQL in Views** | Fast (~5–10ms) | Low (single function) | Immediate (transactional) | Default read strategy for normalized DBs |
| **ORM Query via Repo** | Slow (~50–200ms) | Low (reuses mappers) | Immediate | Small apps with low read volume |
| **Event-Driven View Table**| Ultra-fast (<1ms) | Medium (needs handlers)| Eventual consistency | High-traffic views, search indexes, dashboards |

---

## 4. Thresholds & Defaults

- **Aggregate Size**: Keep small! 1 Aggregate Root + 1–5 child entities/value objects. Never put all products or an entire warehouse in one aggregate.
- **Test Ratio Rule of Thumb**:
  - ~70–80% High-Gear Service & Low-Gear Domain unit tests (fast, in-memory with `FakeUnitOfWork`).
  - ~15–20% Integration tests (verifying real SQLite/Postgres mappers and SQL views).
  - ~5% End-to-End smoke tests (exactly 1 test per endpoint/route).
- **Unit of Work Default**: Always execute `rollback()` on context manager exit unless `commit()` was explicitly called.
- **Architecture Tax**: Allocate 10–20% of engineering bandwidth alongside major feature initiatives to incrementally carve out domain boundaries.
- **Transaction Scope**: One Command = One Aggregate Root modified = One Database Transaction.

---

## 5. Tells & Smells (Diagnostic Heuristics)

| Codebase Smell | Diagnostic Tell | Prescribed Remedy |
|---|---|---|
| **Unit test requires 5+ `mock.patch()` calls** | Business logic is entangled with I/O side effects | Refactor using **Functional Core, Imperative Shell** (Ch 3). |
| **DB column change breaks 30 unit tests** | Tests are coupled directly to Active Record ORM models | Introduce **Repository Pattern** and **Imperative Mapping** (Ch 2). |
| **Web view has 150 lines of ORM and logic** | Controller is "fat" and doing orchestration | Extract into a **Service Layer** function taking primitives (Ch 4). |
| **Ghost emails sent when order fails** | Side effects executed before database commit | Emit a **Domain Event**; publish via UoW *after* commit (Ch 8). |
| **Deadlocks / table lock timeouts in DB** | Aggregates are too large or missing boundaries | Carve into smaller **Aggregates**; use optimistic version locks (Ch 7). |
| **Repository has 30 query methods** | Read concerns are polluting write abstractions | Apply **CQRS**; move reads to raw SQL in `views.py` (Ch 12). |
| **Entrypoints duplicate DB setup code** | Dependencies are wired ad-hoc across modules | Centralize initialization in `bootstrap.py` **Composition Root** (Ch 13). |
| **HTTP POST chains across 4 services** | System is a **Distributed Ball of Mud** | Replace synchronous HTTP with **Asynchronous Events** via broker (Ch 11). |
