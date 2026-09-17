# Architecture Patterns with Python — Patterns Reference

## Domain Model (Entities, Value Objects, and Domain Services)
**When to use**: When business logic contains non-trivial rules, constraints, calculations, or workflows that evolve independently of database storage and web interfaces.
**How**:
1. Implement **Value Objects** as immutable dataclasses (`@dataclass(frozen=True)`) or `NamedTuple` instances comparing by structural equality.
2. Implement **Entities** as classes defined by an enduring identifier (`reference`), overriding `__eq__` on identity and setting `__hash__ = None` (or hashing on identity).
3. Implement **Domain Services** as standalone pure functions for operations that naturally span multiple entities.
4. Keep the domain layer 100% free of external library imports (no ORMs, no web frameworks).
**Trade-offs**:
- *Pros*: Isolates high-value business logic; testable in sub-milliseconds without mocks.
- *Cons*: Adds conceptual overhead and indirection for trivial CRUD applications.

## Repository Pattern
**When to use**: When reading and writing domain aggregates to persistent storage without coupling domain entities to database technologies, SQL, or ORM base classes.
**How**:
1. Define an abstract interface `AbstractRepository` with minimal collection methods: `add(aggregate)` and `get(id)`.
2. Use SQLAlchemy imperative mapping (`mapper_registry.map_imperatively`) to bind database tables to pure domain classes at startup.
3. Implement a production adapter `SqlAlchemyRepository(session)` that executes queries against the database session.
4. Implement `FakeRepository` using Python sets or dicts for fast, isolated in-memory unit tests.
**Trade-offs**:
- *Pros*: Complete persistence ignorance; lightning-fast tests with fakes; storage engines can be swapped seamlessly.
- *Cons*: Writing and maintaining imperative mappers requires ORM expertise and initial boilerplate.

## Functional Core, Imperative Shell (FCIS)
**When to use**: When core decision logic is tangled with external I/O (filesystems, network calls, external APIs).
**How**:
1. *Imperative Shell (Read)*: Fetch state from external sources into primitive data structures (dicts, tuples).
2. *Functional Core*: Pass primitives into pure deterministic functions that compute decisions and yield intent-revealing command tuples (e.g., `("COPY", src, dst)`).
3. *Imperative Shell (Write)*: Iterate over command tuples and execute actual side effects.
**Trade-offs**:
- *Pros*: Complex branching logic tested without mocking frameworks; eliminates brittle mock-heavy test suites.
- *Cons*: Requires separating algorithms into discrete gather-compute-act phases.

## Service Layer Pattern (Application Services)
**When to use**: To define the application's operational use cases and orchestrate workflows between external entry points and the domain model.
**How**:
1. Place use-case functions in `services.py`.
2. Accept primitive types (`str`, `int`) to decouple callers (web views, CLI) from domain model classes.
3. Fetch aggregates from repositories, execute domain methods, and commit transactions.
**Trade-offs**:
- *Pros*: Eliminates Fat Controllers; allows driving the same application use case via HTTP API, CLI, or message queues.
- *Cons*: Adds another layer of functions between the web router and domain entities.

## Unit of Work Pattern (UoW)
**When to use**: To manage database transaction lifecycles, enforce atomic operations across repositories, and prevent partial writes.
**How**:
1. Implement `AbstractUnitOfWork` as a Python context manager (`__enter__`, `__exit__`, `commit()`, `rollback()`).
2. Expose repositories as attributes on the UoW (`uow.products`, `uow.orders`).
3. Enforce "Rollback by default": uncommitted exits automatically trigger a rollback.
4. Implement `FakeUnitOfWork` tracking `committed = True` for testing without database sessions.
**Trade-offs**:
- *Pros*: Guarantees atomic transaction boundaries; centralizes session management; avoids passing raw database connections across layers.
- *Cons*: Adds a context manager wrapper around service workflows.

## Aggregate Pattern
**When to use**: To maintain data consistency across associated entities and enforce business invariants under concurrent operations.
**How**:
1. Group tightly coupled entities and value objects behind a single Aggregate Root entity.
2. Direct all external modifications through methods on the Aggregate Root; never mutate child entities directly.
3. Enforce "One Aggregate = One Repository": repositories only load and persist Aggregate Roots.
4. Add a `version_number` column to the root for optimistic concurrency control (compare-and-swap on update).
**Trade-offs**:
- *Pros*: Restricts locks to small consistency boundaries, maximizing concurrency; prevents invalid partial states.
- *Cons*: Designing boundary granularity requires deep domain understanding; cross-aggregate operations require eventual consistency.

## Domain Events Pattern
**When to use**: When a state change in an aggregate requires secondary side effects (notifications, audit logs, search indexing) without violating the Single Responsibility Principle.
**How**:
1. Define events as immutable dataclasses named in the past tense (`@dataclass class OutOfStock(Event): sku: str`).
2. Add `self.events = []` to the Aggregate Root and record events when business conditions occur.
3. The Unit of Work collects events from seen aggregates after `commit()` and publishes them to the message bus.
**Trade-offs**:
- *Pros*: Completely decouples core domain algorithms from secondary side effects; prevents ghost emails on rollback.
- *Cons*: Event flow is harder to trace than direct linear function calls.

## Message Bus Pattern (In-Memory Queue Dispatcher)
**When to use**: To coordinate multi-step workflows, decouple entry points, and drive applications as message processors.
**How**:
1. Maintain an internal FIFO queue of messages in `messagebus.py`.
2. Map message types to handlers in `COMMAND_HANDLERS` and `EVENT_HANDLERS` dictionaries.
3. While the queue has messages, pop the next message, invoke its registered handlers with the UoW, and append any newly raised events yielded by `uow.collect_new_events()`.
**Trade-offs**:
- *Pros*: Unifies internal and external workflows; handles event cascades cleanly without stack overflow.
- *Cons*: In-memory bus is single-threaded and non-persistent; process crashes drop uncommitted in-memory events.

## Commands and Command Handlers Pattern
**When to use**: To distinguish imperative intent (commands) from completed facts (events) and establish strict failure semantics.
**How**:
1. Define Commands with imperative verb names (`Allocate`, `CreateBatch`); route each command to exactly *one* handler.
2. Fail commands fast and noisily: re-raise exceptions immediately to the caller.
3. Define Events with past-tense names (`Allocated`); route events to zero or more handlers.
4. Fail events independently: catch, log, and continue processing remaining event listeners.
**Trade-offs**:
- *Pros*: Crystal-clear operational contracts; commands guarantee atomic aggregate updates while events handle side effects.
- *Cons*: Requires declaring two distinct message hierarchies and handler registries.

## Command-Query Responsibility Segregation (CQRS)
**When to use**: When read volume significantly exceeds write volume, or when read queries require cross-aggregate joins that would pollute write models.
**How**:
1. *Write Path*: Route commands through the Message Bus, Unit of Work, and Domain Aggregates. Commands return empty status (202 Accepted).
2. *Read Path*: Route queries directly to `views.py`. Read models bypass the domain model and repository entirely, querying via raw SQL or denormalized view tables.
3. Keep read tables synchronized asynchronously using domain event handlers (e.g., `add_allocation_to_read_model`).
**Trade-offs**:
- *Pros*: Massive query performance; zero domain object hydration overhead; read views can be denormalized and cached.
- *Cons*: Introduces eventual consistency between writes and read views; requires maintaining synchronization handlers.

## Composition Root (Bootstrapper Pattern)
**When to use**: To centralize application configuration, database connection factories, and dependency injection in a single location.
**How**:
1. Implement `bootstrap.py` as the sole module that knows how to instantiate real production or test dependencies.
2. Call `orm.start_mappers()` and initialize session factories.
3. Inject dependencies into command and event handlers using Python closures, partials, or signature inspection.
4. Return an initialized `MessageBus` instance to entry points.
**Trade-offs**:
- *Pros*: Entry points (Flask, CLI, Celery) become 5-line wrappers; unit tests override dependencies cleanly without complex DI container libraries.
- *Cons*: Slightly indirect startup flow compared to hardcoded imports.
