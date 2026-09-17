# Chapter 10: Commands and Command Handlers

## Core Idea
Messages divide into Commands (imperative intent sent to a single handler that must fail noisily) and Events (past facts broadcast to multiple subscribers that fail independently), establishing clear failure semantics and enabling cross-aggregate eventual consistency.

## Frameworks Introduced
- **Commands vs. Events Pattern**: A strict architectural distinction between two types of messages:
  - *Commands*:
    - Intent: An instruction expressing a desire for the system to change state (e.g., `commands.Allocate`, `commands.CreateBatch`).
    - Naming: Imperative mood verb phrase (`AllocateStock`, `ChangeQuantity`).
    - Routing: Sent to exactly *one* designated handler.
    - Error Semantics: Fail fast and noisily; exceptions re-raise immediately to the caller (web endpoint, CLI).
  - *Events*:
    - Fact: A broadcast announcement that something significant has already happened in the past (e.g., `events.Allocated`, `events.OutOfStock`).
    - Naming: Past tense verb phrase (`OrderAllocated`, `StockDepleted`).
    - Routing: Broadcast to *zero or more* subscribed listeners.
    - Error Semantics: Fail independently; exceptions are logged and caught so one failing listener does not abort the main transaction.

- **Asymmetric Exception Handling on the Message Bus**:
  - The message bus maintains two distinct handler registries:
    `COMMAND_HANDLERS: Dict[Type[Command], Callable]` (1-to-1)
    `EVENT_HANDLERS: Dict[Type[Event], List[Callable]]` (1-to-many)
  - When dispatching a Command: if the handler raises an error, immediately stop, log, and re-raise the exception to the caller.
  - When dispatching an Event: wrap each handler invocation in a `try/except Exception` block, log errors, and continue processing other handlers and queued messages.

- **Cross-Aggregate Eventual Consistency**:
  - A single command should mutate exactly *one* aggregate root within one transaction.
  - If another aggregate must be updated in response, the first aggregate emits an Event.
  - The message bus catches the event and triggers a subsequent command or handler to update the second aggregate in a separate Unit of Work transaction.

## Key Concepts
- **Command**: A message sent from one component to another requesting an action to be taken.
- **Event**: A message broadcast to notify the system of a completed occurrence.
- **Fail Fast**: Halting execution immediately upon encountering an error so the caller can respond.
- **Fail Independently**: Isolating errors within secondary handlers so that optional side effects (like sending emails or updating analytics) do not roll back core business changes.
- **Imperative Mood**: A grammatical form expressing a direct command or request ("Allocate", "Create").
- **Past Tense**: A grammatical form expressing a historical fact ("Allocated", "Created").

## Mental Models
- **Orders vs. Newsflashes**: A Command is an order sent by a general to a specific sergeant (the sergeant must report if they fail); an Event is a newsflash broadcast over the radio (listeners react, but the broadcaster does not wait or fail if someone's radio battery dies).
- **The Blast Radius Barrier**: Isolate failures so that an SMTP server timeout during notification dispatch does not cancel an already-completed inventory allocation.
- **Single-Aggregate Rule**: One command = one aggregate update = one database commit.

## Anti-patterns
- **Using Events as Commands**: Naming an input message `BatchCreated` when the batch does not yet exist and the request can be rejected.
- **Multiple Command Handlers**: Subscribing two competing handlers to a single command, creating ambiguous execution authority.
- **Silent Command Failures**: Swallowing exceptions in command handlers, leaving the caller believing an operation succeeded when it failed.
- **Event Cascade Catastrophe**: Allowing an unhandled exception in an event listener to crash the entire application or roll back an already-committed database transaction.

## Code Examples

### Command and Event Definitions

```python
# commands.py - Imperative Intent
from dataclasses import dataclass
from typing import Optional
from datetime import date

class Command:
    pass

@dataclass
class Allocate(Command):
    orderid: str
    sku: str
    qty: int

@dataclass
class CreateBatch(Command):
    ref: str
    sku: str
    qty: int
    eta: Optional[date] = None

# events.py - Historical Facts
@dataclass
class Event:
    pass

@dataclass
class Allocated(Event):
    orderid: str
    sku: str
    qty: int
    batchref: str

@dataclass
class OutOfStock(Event):
    sku: str
```
- **What it demonstrates**: Commands use imperative verbs (`Allocate`); events use past tense (`Allocated`).

### Asymmetric Message Bus Implementation

```python
# messagebus.py
import logging
from typing import Dict, Type, List, Callable, Union
import commands
import events
from unit_of_work import AbstractUnitOfWork

logger = logging.getLogger(__name__)
Message = Union[commands.Command, events.Event]

def handle(message: Message, uow: AbstractUnitOfWork) -> List[any]:
    results = []
    queue = [message]
    
    while queue:
        msg = queue.pop(0)
        if isinstance(msg, commands.Command):
            results.append(handle_command(msg, queue, uow))
        elif isinstance(msg, events.Event):
            handle_event(msg, queue, uow)
        else:
            raise ValueError(f"{msg} is neither Command nor Event")
            
    return results

def handle_command(
    command: commands.Command,
    queue: List[Message],
    uow: AbstractUnitOfWork,
) -> any:
    logger.debug("Handling command %s", command)
    try:
        handler = COMMAND_HANDLERS[type(command)]
        result = handler(command, uow=uow)
        queue.extend(uow.collect_new_events())
        return result
    except Exception:
        logger.exception("Exception handling command %s", command)
        raise  # Commands fail fast and bubble up to caller

def handle_event(
    event: events.Event,
    queue: List[Message],
    uow: AbstractUnitOfWork,
) -> None:
    for handler in EVENT_HANDLERS.get(type(event), []):
        try:
            logger.debug("Handling event %s with %s", event, handler)
            handler(event, uow=uow)
            queue.extend(uow.collect_new_events())
        except Exception:
            logger.exception("Exception handling event %s", event)
            continue  # Events fail independently; loop continues
```
- **What it demonstrates**: Commands bubble exceptions up; events catch, log, and proceed with other handlers.

### Handler Registries

```python
# messagebus.py
EVENT_HANDLERS: Dict[Type[events.Event], List[Callable]] = {
    events.OutOfStock: [handlers.send_out_of_stock_notification],
}

COMMAND_HANDLERS: Dict[Type[commands.Command], Callable] = {
    commands.Allocate: handlers.allocate,
    commands.CreateBatch: handlers.add_batch,
    commands.ChangeBatchQuantity: handlers.change_batch_quantity,
}
```
- **What it demonstrates**: Exactly one handler per command; zero or more handlers per event.

## Reference Tables

### Commands vs. Events Comparison Matrix

| Property | Command | Event |
|---|---|---|
| **Naming** | Imperative mood (`Allocate`, `Pay`) | Past tense (`Allocated`, `Paid`) |
| **Recipient** | Exactly one handler | Zero, one, or many subscribers |
| **Intent** | Requests an action to occur | Announces an action already occurred |
| **Error Handling** | Fails noisily; raises immediately | Fails independently; logged and skipped |
| **Origin** | Outside actors (API, CLI, Queue) | Domain Aggregates or Services |
| **Transactional Scope** | Modifies single aggregate | Can trigger follow-up commands/events |

## Worked Example

### Testing Command Failure vs. Event Failure

```python
# test_handlers.py
import pytest
import commands
import events
import messagebus
from unit_of_work import FakeUnitOfWork

def test_command_failure_raises_exception():
    uow = FakeUnitOfWork()
    # Sending Allocate command for non-existent SKU raises error
    with pytest.raises(Exception, match="Invalid sku"):
        messagebus.handle(commands.Allocate("o1", "NONEXISTENT", 10), uow)

def test_event_failure_does_not_halt_bus(monkeypatch):
    uow = FakeUnitOfWork()
    
    # Simulate email server explosion during OutOfStock event
    def explode(event, uow):
        raise ConnectionError("SMTP server down")
        
    monkeypatch.setitem(messagebus.EVENT_HANDLERS, events.OutOfStock, [explode])

    # Publishing the event logs an error but does NOT raise ConnectionError
    messagebus.handle(events.OutOfStock("SOME-SKU"), uow)
    # Execution completes gracefully
```

## Key Takeaways
1. Distinguish messages by intent: Commands capture desires to do something; Events capture facts about what happened.
2. Commands are 1-to-1: sent to a single handler, failing noisily and fast so callers receive immediate error feedback.
3. Events are 1-to-many: broadcast to multiple listeners, failing independently so optional side effects don't abort core workflows.
4. One command should mutate exactly one aggregate root within a single atomic database transaction.
5. Use events to coordinate eventual consistency across multiple aggregates without locking multiple tables together.

## Connects To
- **Ch 08**: Events and the Message Bus — introduced basic events; Ch 10 splits them from commands.
- **Ch 09**: Going to Town on the Message Bus — the message processor engine that executes both commands and events.
- **Ch 11**: External Events — serializing commands and events across network boundaries.
