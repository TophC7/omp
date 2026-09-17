---
name: cosmic-python
description: "Knowledge base from \"Architecture Patterns with Python\" by Harry Percival and Bob Gregory. Use when applying domain-driven design (DDD), the repository pattern, unit of work, event-driven architecture, message bus, command-query responsibility segregation (CQRS), or clean architecture in Python."
---

<!-- argument-hint: [topic, framework name, or chapter number] -->

# Architecture Patterns with Python
**Authors**: Harry Percival & Bob Gregory | **Chapters**: 14 | **Generated**: 2026-09-05

## How to Use This Skill

- **Without arguments** — load core architectural frameworks, patterns, and mental models
- **With a topic** — ask about `repository`, `unit-of-work`, `aggregates`, `messagebus`, `cqrs`, or `dependency-injection`; I load and reason from the relevant chapter
- **With a chapter** — ask for `ch01` through `ch14` to inspect a specific chapter
- **Browse** — ask "what chapters do you have?" to see the full architecture index

When you ask about a topic not covered in Core Frameworks below, I will read the relevant chapter file under `chapters/` before answering.

---

## Core Frameworks & Mental Models

### 1. The Dependency Inversion Principle (DIP) & Onion Architecture
- **Rule**: High-level modules (business domain) should not depend on low-level modules (ORM, SQL, web frameworks). Both should depend on abstractions.
- **Mental Model**: Turn traditional 3-layer architecture inside out. Place the pure Python domain model at the center. Infrastructure (databases, APIs, message queues) sits at the edges, pointing inward as swappable adapters.
- **Application**: The domain model never imports SQLAlchemy, Flask, Django, or requests.

### 2. Domain Modeling (Entities vs. Value Objects)
- **Value Object**: Any domain object identified solely by its data attributes with no independent lifecycle (`OrderLine`, `Money`, `Sku`). Implement as immutable dataclasses (`@dataclass(frozen=True)`) with structural equality (`__eq__`).
- **Entity**: A domain object with an enduring identity that outlives its mutable attributes (`Batch`, `Order`). Implement with identity equality (`self.reference == other.reference`) and `__hash__ = None`.
- **Domain Service**: A standalone pure function representing business calculations across multiple entities (`allocate(line, batches)`) with zero I/O side effects.

### 3. The Repository Pattern
- **Purpose**: An abstraction over persistent storage that presents the illusion of an in-memory collection.
- **Interface**: Expose minimal collection primitives: `add(aggregate)` and `get(id)` (plus optional `list()`).
- **Implementation**:
  - Production: `SqlAlchemyRepository(session)` using SQLAlchemy's classical imperative mapping (`mapper_registry.map_imperatively`) to keep domain entities free of ORM inheritance.
  - Testing: `FakeRepository(set)` for sub-millisecond, dependency-free in-memory unit tests.
- **Rule**: Repositories only load and persist Aggregate Roots ("One Aggregate = One Repository").

### 4. Functional Core, Imperative Shell (FCIS)
- **Principle**: Separate pure decision logic from external I/O mutations.
- **Workflow**:
  1. *Imperative Shell (Input)*: Gather state from disk/network into simple primitives or dicts.
  2. *Functional Core*: Execute pure functions that calculate decisions and yield declarative command tuples (e.g. `("COPY", src, dst)`).
  3. *Imperative Shell (Output)*: Iterate through command tuples and execute actual side effects.
- **Diagnostic Tell**: If a unit test requires 5+ `mock.patch()` calls, business logic is tangled with I/O; refactor into FCIS.

### 5. The Service Layer (Application Services)
- **Purpose**: Defines application use cases and orchestrates workflows between external entry points and internal domain models.
- **Boundary Contract**: Service layer functions accept primitive types (`str`, `int`, `dict`) rather than rich domain classes, preventing presentation callers from coupling to domain constructors.
- **Testing Pyramid**: Push the bulk of tests from slow, brittle E2E suites down to the Service Layer, using `FakeRepository` and `FakeUnitOfWork` to test complete user stories in milliseconds.

### 6. High Gear vs. Low Gear TDD
- **Low Gear (Domain Tests)**: Write fine-grained tests against domain models (`model.py`) when exploring unfamiliar domains or complex business rules. Gives maximum design feedback but high structural glue.
- **High Gear (Service Tests)**: Write tests against the service layer using primitives and fakes during day-to-day feature work. Gives high coverage with minimal coupling, leaving domain models free to refactor.

### 7. The Unit of Work (UoW) Pattern
- **Purpose**: Abstraction over atomic database transactions and session lifecycles.
- **Syntax**: Implemented as a Python context manager (`with uow:`).
- **Invariants**: "Rollback by default"—exiting the context block without an explicit `uow.commit()` automatically triggers `rollback()`.
- **Testing**: Test with `FakeUnitOfWork` tracking `self.committed = True`. "Don't mock what you don't own"—abstract third-party sessions into your own UoW port, and fake that port.

### 8. Aggregates and Consistency Boundaries
- **Definition**: A cluster of domain entities and value objects treated as a single transactional unit, accessed exclusively through an Aggregate Root entity (`Product`).
- **Rule**: Enforces invariants synchronously within its boundary. Outside code never mutates child entities directly.
- **Concurrency**: Use optimistic locking (`version_number` compare-and-swap on update) to prevent race conditions without locking entire tables. Keep aggregates small (1 root + 1–5 children).

### 9. Domain Events & The Message Bus
- **Domain Event**: An immutable dataclass representing a completed business fact (`events.OutOfStock`, `events.Allocated`). Recorded internally by aggregates (`aggregate.events.append(...)`).
- **Publish Post-Commit**: The Unit of Work collects events from seen aggregates after `commit()` and publishes them to the message bus, preventing side effects from executing on rolled-back transactions.
- **Message Bus Dispatcher**: Maintains an in-memory FIFO queue loop that executes handlers and collects secondary events raised during execution.

### 10. Commands vs. Events
- **Commands**: Express imperative *intent* (`commands.Allocate`). Sent to exactly *one* handler. Fail noisily and fast (re-raise exceptions to the caller).
- **Events**: Announce historical *facts* (`events.Allocated`). Broadcast to *zero or more* handlers. Fail independently (logged and caught; do not abort the main transaction).

### 11. Event-Driven Microservice Integration
- **Distributed Ball of Mud**: Avoid splitting services by static nouns (`BatchService`, `OrderService`) with synchronous chained HTTP calls.
- **Temporal Decoupling**: Integrate services by publishing domain events to message brokers (Redis, RabbitMQ, Kafka). Upstream services commit locally and return; downstream services handle events asynchronously.
- **Connascence**: Replace strong execution/timing connascence with weak name/data connascence. Ensure all consumer handlers are idempotent.

### 12. Command-Query Responsibility Segregation (CQRS)
- **Principle**: Domain models exist to protect invariants during writes; queries do not mutate state and should bypass domain models entirely.
- **Write Path**: Commands → Message Bus → Handlers → UoW → Aggregates → Commit (returns `202 Accepted`).
- **Read Path**: Queries → `views.py` → Raw SQL / Denormalized View Tables → Plain JSON Dictionaries.
- **Event-Driven View Projections**: Maintain zero-join, denormalized read tables updated asynchronously by domain event listeners.

### 13. Composition Root & Bootstrapping
- **Bootstrapper (`bootstrap.py`)**: The single location that initializes mappers, session factories, and adapters, and injects dependencies into handlers using Python closures or signature inspection.
- **Pythonic DI**: No heavy enterprise IoC containers. Handlers declare parameters (`uow`, `send_mail`); the bootstrapper binds them with `functools.partial` or lambdas. Entry points only call `bus.handle(message)`.

---

## Chapter Index

| Chapter | Title | Key Frameworks & Topics |
|---|---|---|
| [ch00](chapters/ch00-preface-and-intro.md) | Preface & Introduction | Big Ball of Mud, DIP, 3-layer vs. inverted architecture |
| [ch01](chapters/ch01-domain-modeling.md) | Domain Modeling | Entities, Value Objects, Domain Services, Invariants |
| [ch02](chapters/ch02-repository-pattern.md) | Repository Pattern | Persistence Ignorance, Imperative Mapping, FakeRepository |
| [ch03](chapters/ch03-coupling-and-abstractions.md) | Coupling & Abstractions | Functional Core / Imperative Shell, Mocking smells |
| [ch04](chapters/ch04-service-layer.md) | Service Layer | Application Services, Primitives, Thin Flask controllers |
| [ch05](chapters/ch05-high-gear-low-gear.md) | TDD High Gear / Low Gear | Test Glue, Driving tests via services, Test Pyramid |
| [ch06](chapters/ch06-unit-of-work.md) | Unit of Work Pattern | Context managers, Atomic commits, Don't mock what you don't own |
| [ch07](chapters/ch07-aggregates.md) | Aggregates & Boundaries | Aggregate Roots, Invariants, Optimistic locking, Bounded Contexts |
| [ch08](chapters/ch08-events-and-message-bus.md) | Events & Message Bus | Domain Events, Internal Pub/Sub, Post-commit dispatch |
| [ch09](chapters/ch09-all-message-bus.md) | All Message Bus | App as message processor, Queue loop, Event chaining |
| [ch10](chapters/ch10-commands-and-handlers.md) | Commands & Handlers | Commands vs. Events, Asymmetric exception handling, Fail fast |
| [ch11](chapters/ch11-external-events.md) | External Events & Microservices | Distributed Ball of Mud, Temporal decoupling, Connascence, Redis |
| [ch12](chapters/ch12-cqrs.md) | CQRS | Bypassing domain model for reads, View tables, CQS |
| [ch13](chapters/ch13-dependency-injection.md) | Dependency Injection & Bootstrap | Composition Root, Pythonic DI with closures, Clean entrypoints |
| [ch14](chapters/ch14-epilogue-and-appendices.md) | Architecture Blueprint | Full architecture map, Architecture tax, Canonical directory layout |

---

## Topic Index

- **Active Record (Anti-pattern)** → [ch02](chapters/ch02-repository-pattern.md)
- **Aggregates & Aggregate Roots** → [ch07](chapters/ch07-aggregates.md), [ch14](chapters/ch14-epilogue-and-appendices.md)
- **Architecture Tax (Refactoring Strategy)** → [ch14](chapters/ch14-epilogue-and-appendices.md)
- **Asynchronous Messaging** → [ch11](chapters/ch11-external-events.md)
- **Big Ball of Mud** → [ch00](chapters/ch00-preface-and-intro.md), [ch03](chapters/ch03-coupling-and-abstractions.md), [ch11](chapters/ch11-external-events.md)
- **Bootstrap / Composition Root** → [ch13](chapters/ch13-dependency-injection.md), [ch14](chapters/ch14-epilogue-and-appendices.md)
- **Bounded Contexts** → [ch07](chapters/ch07-aggregates.md)
- **Classical / Imperative Mapping (SQLAlchemy)** → [ch02](chapters/ch02-repository-pattern.md)
- **Commands & Command Handlers** → [ch10](chapters/ch10-commands-and-handlers.md)
- **Command-Query Responsibility Segregation (CQRS)** → [ch12](chapters/ch12-cqrs.md)
- **Command-Query Separation (CQS)** → [ch12](chapters/ch12-cqrs.md)
- **Connascence** → [ch11](chapters/ch11-external-events.md)
- **Consistency Boundaries** → [ch07](chapters/ch07-aggregates.md)
- **Context Managers** → [ch06](chapters/ch06-unit-of-work.md)
- **Dependency Inversion Principle (DIP)** → [ch00](chapters/ch00-preface-and-intro.md), [ch02](chapters/ch02-repository-pattern.md)
- **Dependency Injection (Pythonic)** → [ch13](chapters/ch13-dependency-injection.md)
- **Domain Events** → [ch08](chapters/ch08-events-and-message-bus.md), [ch09](chapters/ch09-all-message-bus.md)
- **Domain Exceptions** → [ch01](chapters/ch01-domain-modeling.md)
- **Domain Model** → [ch01](chapters/ch01-domain-modeling.md)
- **Domain Services vs. Application Services** → [ch01](chapters/ch01-domain-modeling.md), [ch04](chapters/ch04-service-layer.md)
- **Entities** → [ch01](chapters/ch01-domain-modeling.md)
- **Event-Driven Architecture** → [ch08](chapters/ch08-events-and-message-bus.md), [ch09](chapters/ch09-all-message-bus.md), [ch11](chapters/ch11-external-events.md)
- **Eventual Consistency** → [ch07](chapters/ch07-aggregates.md), [ch11](chapters/ch11-external-events.md), [ch12](chapters/ch12-cqrs.md)
- **Fakes vs. Mocks** → [ch02](chapters/ch02-repository-pattern.md), [ch03](chapters/ch03-coupling-and-abstractions.md), [ch06](chapters/ch06-unit-of-work.md)
- **Functional Core, Imperative Shell (FCIS)** → [ch03](chapters/ch03-coupling-and-abstractions.md)
- **High Gear / Low Gear Testing** → [ch05](chapters/ch05-high-gear-low-gear.md)
- **Idempotency** → [ch01](chapters/ch01-domain-modeling.md), [ch11](chapters/ch11-external-events.md)
- **Invariants** → [ch01](chapters/ch01-domain-modeling.md), [ch07](chapters/ch07-aggregates.md)
- **Message Bus** → [ch08](chapters/ch08-events-and-message-bus.md), [ch09](chapters/ch09-all-message-bus.md), [ch10](chapters/ch10-commands-and-handlers.md)
- **Mocking Smells** → [ch03](chapters/ch03-coupling-and-abstractions.md), [ch06](chapters/ch06-unit-of-work.md)
- **Optimistic Concurrency Control (Version Numbers)** → [ch07](chapters/ch07-aggregates.md)
- **Persistence Ignorance** → [ch02](chapters/ch02-repository-pattern.md)
- **Ports and Adapters (Hexagonal)** → [ch00](chapters/ch00-preface-and-intro.md), [ch02](chapters/ch02-repository-pattern.md), [ch14](chapters/ch14-epilogue-and-appendices.md)
- **Project Structure** → [ch14](chapters/ch14-epilogue-and-appendices.md)
- **Read Models & View Projections** → [ch12](chapters/ch12-cqrs.md)
- **Repository Pattern** → [ch02](chapters/ch02-repository-pattern.md)
- **Rollback by Default** → [ch06](chapters/ch06-unit-of-work.md)
- **Service Layer** → [ch04](chapters/ch04-service-layer.md)
- **Single Responsibility Principle (SRP)** → [ch08](chapters/ch08-events-and-message-bus.md)
- **Test Pyramid** → [ch04](chapters/ch04-service-layer.md), [ch05](chapters/ch05-high-gear-low-gear.md)
- **Ubiquitous Language** → [ch01](chapters/ch01-domain-modeling.md)
- **Unit of Work (UoW)** → [ch06](chapters/ch06-unit-of-work.md)
- **Validation (Ensure Pattern)** → [ch14](chapters/ch14-epilogue-and-appendices.md)
- **Value Objects** → [ch01](chapters/ch01-domain-modeling.md)

---

## Supporting Files

- [glossary.md](glossary.md) — Comprehensive alphabetical glossary of all domain and architectural terms with chapter references.
- [patterns.md](patterns.md) — Practical pattern catalog detailing When to use, How to implement, and Trade-offs for all 11 core patterns.
- [cheatsheet.md](cheatsheet.md) — High-density decision guide featuring "When X, do Y, because Z" rules, architectural decision trees, trade-off matrices, thresholds, and diagnostic smells.

---

## Scope & Limits

This skill covers the architectural principles, domain modeling patterns, and testing practices presented in *Architecture Patterns with Python* (O'Reilly). It provides conceptual guidance, design trade-offs, and implementation idioms. For infrastructure deployment, cloud services, Kubernetes orchestration, or database cluster administration, combine with operational tools and platform documentation.
