# Chapter 8: Events and the Message Bus

## Core Idea
Domain Events record business facts that have occurred in the domain model, allowing secondary side effects (notifications, audits, external integrations) to be decoupled from core workflows and dispatched via a lightweight in-memory Message Bus after transaction commits.

## Frameworks Introduced
- **The Domain Events Pattern**: Immutable data structures representing significant business occurrences that have already happened.
  - When to use: When a state change in an aggregate requires secondary actions (e.g., sending an email, logging an audit record, updating a search index) without polluting the core domain logic.
  - How:
    1. Define events as immutable dataclasses named in the past tense or as completed facts (`@dataclass class OutOfStock(Event): sku: str`).
    2. Add an internal list `self.events = []` to the Aggregate Root.
    3. When a business rule triggers, append the event to the root's list (`self.events.append(events.OutOfStock(sku))`).
  - Why it works: Keeps domain entities completely free of I/O, email clients, and infrastructure concerns while retaining rich diagnostic signals.
  - Failure mode: Executing side effects directly inside the domain model instead of recording the event.

- **The Message Bus Pattern**: A simple dispatcher mapping event classes to lists of handler functions (a lightweight publish-subscribe system).
  - When to use: To route domain events to their respective side-effect handlers.
  - How:
    1. Define a mapping dictionary: `HANDLERS: Dict[Type[Event], List[Callable]]`.
    2. Implement `handle(event: Event)`: look up handlers for `type(event)` and invoke them sequentially.
    3. Register handler functions that take an event as their sole parameter.
  - Why it works: Handlers are completely decoupled from the caller; adding a new reaction to an event requires zero edits to existing domain entities or service use cases (Open/Closed Principle).
  - Failure mode: Relying on the message bus for asynchronous multithreading; in this chapter, it operates synchronously within the process boundary.

- **UoW-Driven Event Publishing (Seen Aggregates)**:
  - The repository tracks all aggregates retrieved or added during a session via a `self.seen: Set[Aggregate]` attribute.
  - When `uow.commit()` is called:
    1. The UoW commits database changes (`self._commit()`).
    2. Upon successful persistence, the UoW iterates over `self.products.seen`.
    3. For each aggregate, it pops all recorded events and dispatches them to `messagebus.handle(event)`.
  - Guarantees that side effects (like sending emails) occur *only after* database state has been durably committed.

## Key Concepts
- **Domain Event**: A record of something significant that happened in the business domain.
- **Message Bus**: A routing mechanism that distributes events to subscribed handlers.
- **Handler**: A focused function executed in response to a specific event.
- **Seen Aggregates**: The set of domain objects loaded or modified during the lifetime of a Unit of Work context.
- **Publish-Subscribe (Pub/Sub)**: An architectural pattern where event emitters do not directly invoke specific receivers.
- **Single Responsibility Principle (SRP)**: Ensuring a function or class has only one reason to change (e.g., allocating stock vs. sending emails).

## Mental Models
- **Diary of Facts**: The aggregate root writes notes in its private diary (`self.events.append(...)`) about what happened; it doesn't care who reads the diary.
- **The Post-Commit Mailbag**: The Unit of Work holds onto all event envelopes until the safe is locked (`commit()`); once locked, it drops the envelopes into the post box (`messagebus`).
- **Open for Extension, Closed for Modification**: Adding a Slack alert when stock runs out requires adding one handler to `HANDLERS[OutOfStock]`; neither `Product` nor `services.allocate` is touched.

## Anti-patterns
- **Emailing from the Web Endpoint**: Writing notification and email logic directly inside web controllers.
- **I/O Inside the Domain Model**: Injecting SMTP clients or notification services into domain entity methods.
- **Side Effects Before Commits**: Sending emails or triggering external actions before the database transaction commits, resulting in ghost emails if the database rollback occurs.
- **Using Exceptions for Normal Business Flow**: Raising exceptions like `OutOfStock` for routine operational facts instead of recording events.

## Code Examples

### Domain Event Definition and Aggregate Recording

```python
# events.py - Pure domain event definitions
from dataclasses import dataclass

class Event:
    pass

@dataclass
class OutOfStock(Event):
    sku: str
```

Aggregate recording the event:
```python
# model.py - Product Aggregate Root
from typing import List, Optional
import events

class Product:
    def __init__(self, sku: str, batches: List["Batch"], version_number: int = 0):
        self.sku = sku
        self.batches = batches
        self.version_number = version_number
        self.events: List[events.Event] = []

    def allocate(self, line: "OrderLine") -> Optional[str]:
        try:
            batch = next(b for b in sorted(self.batches) if b.can_allocate(line))
            batch.allocate(line)
            self.version_number += 1
            return batch.reference
        except StopIteration:
            # Record business event instead of raising an exception
            self.events.append(events.OutOfStock(line.sku))
            return None
```
- **What it demonstrates**: `Product` records the business occurrence in `self.events` without executing side effects or raising exceptions.

### Simple Message Bus

```python
# messagebus.py - Application Layer
from typing import Dict, Type, List, Callable
import events
from adapters import email

def send_out_of_stock_notification(event: events.OutOfStock) -> None:
    email.send_mail(
        "stock_buyer@example.com",
        f"Out of stock for SKU: {event.sku}",
    )

HANDLERS: Dict[Type[events.Event], List[Callable]] = {
    events.OutOfStock: [send_out_of_stock_notification],
}

def handle(event: events.Event) -> None:
    for handler in HANDLERS.get(type(event), []):
        handler(event)
```
- **What it demonstrates**: Dictionary mapping event types to handlers; executing handler lists dynamically.

### Unit of Work Publishing Events on Commit

```python
# unit_of_work.py
import abc
import messagebus

class AbstractUnitOfWork(abc.ABC):
    products: repository.AbstractProductRepository

    def commit(self) -> None:
        self._commit()
        self.publish_events()

    def publish_events(self) -> None:
        for product in self.products.seen:
            while product.events:
                event = product.events.pop(0)
                messagebus.handle(event)

    @abc.abstractmethod
    def _commit(self) -> None:
        raise NotImplementedError
```
- **What it demonstrates**: `publish_events()` runs strictly after `self._commit()`, clearing events from seen aggregates.

## Reference Tables

### Options for Connecting Events to the Message Bus

| Option | Implementation | Pros | Cons |
|---|---|---|---|
| **1. Service Layer Explicit** | `services.allocate` calls `messagebus.handle(product.events)` | Simple to see control flow | Pollutes every service function with manual event flushing |
| **2. Service Raises Events** | Service constructs and dispatches events directly | Aggregate doesn't need `.events` | Domain rules leak out of aggregate into service layer |
| **3. UoW Automatic (Recommended)** | UoW inspects `seen` aggregates and flushes after commit | Fully automated; zero boilerplate in service functions | Requires repository to track `seen` entities |

## Worked Example

### Testing Domain Events at the Unit Level

```python
# test_product.py - Unit test verifying event recording
import events
from model import Product, Batch, OrderLine
from datetime import date

def test_records_out_of_stock_event_when_allocation_fails():
    batch = Batch("b1", "SMALL-CHAIR", 10, eta=date.today())
    product = Product("SMALL-CHAIR", [batch])
    
    # Allocate all available stock
    product.allocate(OrderLine("o1", "SMALL-CHAIR", 10))
    assert len(product.events) == 0

    # Next allocation fails and triggers event
    allocation = product.allocate(OrderLine("o2", "SMALL-CHAIR", 5))

    assert allocation is None
    assert product.events[-1] == events.OutOfStock("SMALL-CHAIR")
```

Testing the message bus handler with a fake email client:
```python
# test_messagebus.py - Unit test verifying handler execution
from unittest.mock import patch
import events
import messagebus

def test_out_of_stock_handler_sends_email():
    with patch("adapters.email.send_mail") as mock_send_mail:
        messagebus.handle(events.OutOfStock("RUSTY-SPOON"))
        
        assert mock_send_mail.call_count == 1
        args, _ = mock_send_mail.call_args
        assert "RUSTY-SPOON" in args[1]
```

## Key Takeaways
1. Domain Events capture significant occurrences in the business domain as immutable dataclasses.
2. Aggregates record domain events internally (`self.events.append(...)`) rather than executing side effects.
3. The Message Bus is a lightweight dispatch table mapping event classes to handler functions.
4. The Unit of Work publishes events to the message bus automatically *after* database transactions commit successfully.
5. This architecture respects the Single Responsibility Principle: the domain model decides, the UoW commits, and the message bus notifies.

## Connects To
- **Ch 06**: Unit of Work Pattern — enhanced to publish events after transaction commits.
- **Ch 07**: Aggregates — the entities responsible for raising domain events.
- **Ch 09**: Going to Town on the Message Bus — expanding the message bus to become the primary architectural driver of the system.
