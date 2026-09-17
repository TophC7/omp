# Chapter 13: Dependency Injection (and Bootstrapping)

## Core Idea
A dedicated Bootstrapper script acts as the application's Composition Root, centralizing initialization (ORM mappers, database session factories) and injecting external dependencies into message handlers using Pythonic closures, leaving entry points and handlers decoupled and clean.

## Frameworks Introduced
- **The Composition Root (Bootstrapper Pattern)**: A single module (`bootstrap.py`) where all dependencies are resolved and glued together at application startup.
  - When to use: In every non-trivial application to prevent entry points (Flask, CLI, Celery, Redis consumer) from duplicating configuration, database wiring, and adapter setup.
  - How:
    1. Define `bootstrap(start_orm=True, uow=..., send_mail=..., publish=...) -> MessageBus`.
    2. Start global infrastructure (e.g., `orm.start_mappers()`, logging configuration).
    3. Bind production or test dependencies into a dictionary or explicit factory calls.
    4. Inject dependencies into command and event handlers.
    5. Return an initialized `MessageBus` instance pre-loaded with injected handlers.
  - Why it works: Entry points only call `bus = bootstrap.bootstrap()` and `bus.handle(msg)`; tests override individual dependencies cleanly (`bootstrap(start_orm=False, uow=FakeUnitOfWork())`).
  - Failure mode: Distributing dependency construction across random modules or importing global singletons throughout the codebase.

- **Pythonic Dependency Injection (No Heavy IoC Containers)**:
  - Avoid complex enterprise DI frameworks; use Python's first-class functions and closures:
    - *Option A (Signature Inspection)*: Use `inspect.signature(handler).parameters` to automatically match parameter names (`uow`, `send_mail`, `publish`) to available dependencies.
    - *Option B (Explicit Lambdas / Partials)*: Explicitly bind dependencies using inline lambdas (`lambda e: handler(e, uow=uow)`) or `functools.partial(handler, uow=uow)`.
    - *Option C (Class-based Handlers)*: Implement handlers as callable classes with dependencies injected in `__init__` and actions in `__call__`.
  - Handlers declare only the dependencies they actually need in their function signatures.

- **Clean Entry Points**:
  - Entry points (Flask routes, CLI commands, background consumers) should contain zero database logic and zero adapter configuration.
  - An entry point's sole responsibility is:
    1. Parsing incoming transport data (HTTP JSON, CLI arguments, Redis pub/sub payload).
    2. Instantiating a domain Command or Event.
    3. Passing the message to `bus.handle(message)`.
    4. Returning an appropriate transport response (HTTP status, process exit code).

## Key Concepts
- **Composition Root**: The single location in an application where the dependency graph is composed and wired together.
- **Implicit vs. Explicit Dependencies**: Explicit dependencies are passed via parameters; implicit dependencies are hardcoded module imports (`import email; email.send()`).
- **Signature Inspection**: Using Python's `inspect` module to dynamically discover what arguments a function accepts.
- **Closure**: A function that captures and retains references to variables in its enclosing lexical scope (e.g., `uow` captured in `lambda cmd: handler(cmd, uow)`).
- **MessageBus as an Object**: Refactoring the message bus from a static module of functions into an instantiable class holding its own injected handler dictionaries and UoW.

## Mental Models
- **The Power Strip / Junction Box**: The Bootstrapper is the central electrical junction box where all wires (database cables, email pipes, message queues) are connected; the rest of the house only sees clean, standard wall outlets.
- **The Universal Remote**: Once bootstrapped, the `MessageBus` acts as a universal remote control (`bus.handle(msg)`) for every entry point in the system.
- **No Magic DI**: Python does not need XML configs or reflection magic; functions accepting parameters plus lambdas provide all the dependency injection power required.

## Anti-patterns
- **The "Control Freak" Antipattern**: Classes creating their own dependencies internally (e.g., a handler instantiating `SqlAlchemyUnitOfWork()` directly in its body).
- **Global Mutable Singletons**: Storing database sessions, clients, or configuration in module-level global variables mutated across modules.
- **Heavyweight Framework Overkill**: Adopting Java-style enterprise IoC container libraries in Python that introduce complex XML or metaclass magic for simple parameter passing.
- **Entrypoint Initialization Sprawl**: Copy-pasting `orm.start_mappers()` and database connection setup into `flask_app.py`, `cli.py`, `worker.py`, and test files.

## Code Examples

### The Bootstrap Module

```python
# bootstrap.py - Composition Root
import inspect
from typing import Callable
from orm import start_mappers
import unit_of_work
import handlers
import messagebus
from adapters import email, redis_eventpublisher

def bootstrap(
    start_orm: bool = True,
    uow: unit_of_work.AbstractUnitOfWork = None,
    send_mail: Callable = email.send_mail,
    publish: Callable = redis_eventpublisher.publish,
) -> messagebus.MessageBus:
    if start_orm:
        start_mappers()

    if uow is None:
        uow = unit_of_work.SqlAlchemyUnitOfWork()

    dependencies = {"uow": uow, "send_mail": send_mail, "publish": publish}
    
    injected_event_handlers = {
        event_type: [
            inject_dependencies(handler, dependencies)
            for handler in event_handlers
        ]
        for event_type, event_handlers in handlers.EVENT_HANDLERS.items()
    }
    injected_command_handlers = {
        command_type: inject_dependencies(handler, dependencies)
        for command_type, handler in handlers.COMMAND_HANDLERS.items()
    }

    return messagebus.MessageBus(
        uow=uow,
        event_handlers=injected_event_handlers,
        command_handlers=injected_command_handlers,
    )

def inject_dependencies(handler: Callable, dependencies: dict) -> Callable:
    params = inspect.signature(handler).parameters
    deps = {
        name: dependency
        for name, dependency in dependencies.items()
        if name in params
    }
    return lambda message: handler(message, **deps)
```
- **What it demonstrates**: `bootstrap()` binds infrastructure, inspects handler parameters, and returns a fully initialized `MessageBus`.

### Ultra-Clean Entry Points

Flask Web Controller:
```python
# entrypoints/flask_app.py
from flask import Flask, request, jsonify
import bootstrap
from domain import commands

app = Flask(__name__)
bus = bootstrap.bootstrap()

@app.route("/allocate", methods=["POST"])
def allocate_endpoint():
    cmd = commands.Allocate(
        request.json["orderid"],
        request.json["sku"],
        request.json["qty"],
    )
    bus.handle(cmd)
    return "OK", 202
```

Redis Consumer Entry Point:
```python
# entrypoints/redis_eventconsumer.py
import json, redis, config, bootstrap
from domain import commands

bus = bootstrap.bootstrap()
r = redis.Redis(**config.get_redis_host_and_port())

def main():
    pubsub = r.pubsub(ignore_subscribe_messages=True)
    pubsub.subscribe("change_batch_quantity")
    for message in pubsub.listen():
        data = json.loads(message["data"])
        cmd = commands.ChangeBatchQuantity(ref=data["batchref"], qty=data["qty"])
        bus.handle(cmd)
```
- **What it demonstrates**: Entry points share the exact same bootstrap logic; their code is reduced to simple transport translation and dispatch.

## Reference Tables

### Dependency Injection Approaches in Python

| Technique | Implementation | Pros | Cons |
|---|---|---|---|
| **Inspection (`inspect.signature`)** | Automatic mapping by parameter name | Handlers declare only needed deps; low boilerplate | Slight runtime reflection magic |
| **Explicit Lambdas** | `lambda msg: handler(msg, uow=uow)` | 100% explicit; no reflection; clear stack traces | Requires manual maintenance in bootstrap dictionary |
| **`functools.partial`** | `partial(handler, uow=uow)` | Clean functional idiom; preserves signature | Be aware of mutable default argument binding |
| **Class Handlers (`__call__`)** | `class Handler: def __init__(self, uow): ...` | Familiar to OO developers; explicit fields | Boilerplate: requires converting functions to classes |

## Worked Example

### Testing the Entire Application with Bootstrapped Fakes

```python
# tests/unit/test_handlers.py - Clean testing with bootstrapped fakes
import pytest
import bootstrap
from unit_of_work import FakeUnitOfWork
from domain import commands

def test_allocate_use_case_with_bootstrapped_bus():
    fake_emails = []
    def fake_send_mail(to, body):
        fake_emails.append((to, body))

    # Bootstrap app with in-memory fakes and no ORM
    bus = bootstrap.bootstrap(
        start_orm=False,
        uow=FakeUnitOfWork(),
        send_mail=fake_send_mail,
        publish=lambda *args: None,
    )

    # Execute system use cases via message bus
    bus.handle(commands.CreateBatch("b1", "ELEGANT-LAMP", 100, None))
    bus.handle(commands.Allocate("o1", "ELEGANT-LAMP", 10))

    # Verify observable outcome on aggregate
    batch = bus.uow.products.get("ELEGANT-LAMP").batches[0]
    assert batch.available_quantity == 90
```

## Key Takeaways
1. A Composition Root (`bootstrap.py`) centralizes initialization and dependency resolution in one place.
2. In Python, Dependency Injection does not require complex frameworks; closures, lambdas, and signature inspection provide clean, testable injection.
3. Handlers declare explicit dependencies in their function signatures and remain completely agnostic of how those dependencies are instantiated.
4. Entry points (web controllers, queue consumers, CLI scripts) become thin transport adapters that parse inputs, build messages, and call `bus.handle()`.
5. Testing is simplified: unit tests bootstrap the message bus with fake adapters and execute entire use cases in memory without databases or networks.

## Connects To
- **Ch 06**: Unit of Work — the core persistence dependency injected into handlers.
- **Ch 09**: Going to Town on the Message Bus — converted into a clean object holding injected handlers.
- **Ch 10**: Commands and Command Handlers — the recipients of injected dependencies.
- **Ch 14**: Epilogue and Appendices — the complete architectural map tying all patterns together.
