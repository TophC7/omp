# Chapter 9: Going to Town on the Message Bus

## Core Idea
By routing all application use cases through an in-memory Message Bus and unifying service functions as message handlers, the application becomes a coherent message processor where complex, multi-step business workflows are driven entirely by event chains.

## Frameworks Introduced
- **The Application as a Message Processor**: Re-architecting the entire application entry point around messages.
  - When to use: When system workflows trigger cascading business side effects (e.g., changing batch quantity forces deallocations, which trigger new allocations).
  - How:
    1. Represent all external requests as message objects (events or commands).
    2. Pass messages directly into `messagebus.handle(message, uow)`.
    3. Treat former service-layer functions as message handlers subscribed to specific message types.
  - Why it works: Unifies internal and external workflows under a single, consistent programming model; allows chaining domain side effects without tight coupling.
  - Failure mode: Event chains becoming unbounded recursive loops (Event Storm cascades) without clear termination criteria.

- **The Message Bus Queue Loop (Pull Architecture)**:
  - Instead of having the Unit of Work push events directly onto the message bus (which creates a circular dependency), the message bus *pulls* new events from the UoW.
  - While processing an event:
    1. Initialize `queue = [initial_event]`.
    2. While `queue` is not empty, pop `message = queue.pop(0)`.
    3. Look up registered handlers and execute them with the current UoW.
    4. Call `queue.extend(uow.collect_new_events())` to capture any secondary events raised by domain aggregates during the step.
  - Guarantees sequential, deterministic event dispatch within a controlled loop.

- **Chaining Events for Situated Software**:
  - Real-world business software is "situated" (Rich Hickey): it models physical realities where things go wrong (e.g., goods water-damaged in transit).
  - Model complex operational changes as a chain of distinct events:
    `BatchQuantityChanged` → deallocate excess stock → emit `AllocationRequired` → allocate to new batch.
  - Each link in the chain represents a focused, single-responsibility transaction.

## Key Concepts
- **Situated Software**: Software that runs for extended periods managing physical, real-world processes where unpredictable disruptions routinely occur.
- **Event Storming**: A collaborative workshop method where domain experts and developers map out business processes using domain events on a timeline.
- **Event Queue**: An in-memory list inside the message bus holding pending events to be processed sequentially.
- **New Events Generator (`collect_new_events`)**: A generator method on the Unit of Work that yields and clears all unhandled events from seen aggregates.
- **Handler Mapping**: A static dictionary binding message classes to one or more callable handler functions.

## Mental Models
- **The Event Pinball**: An initial event enters the machine, hits a handler, triggers a domain aggregate, which drops two new event balls into the queue, each hitting subsequent bumpers until the queue drains.
- **The Message Processor**: The entire application is simply an engine that consumes messages, consults domain models, and outputs state changes and new messages.
- **One-Way Dependency**: Presentation → Message Bus → Handlers → Domain Model & Unit of Work (the UoW no longer imports or calls the message bus).

## Anti-patterns
- **Circular UoW-Messagebus Coupling**: Having the Unit of Work import and call `messagebus.handle()`, while handlers import and use the Unit of Work.
- **God Workflow Functions**: Writing a single 200-line service function that reallocates stock, sends emails, updates manifests, and audits logs in one massive procedural block.
- **Recursive Handler Invocation**: Having handlers directly call `messagebus.handle()` inside their own execution body, blowing the stack instead of queueing events.
- **Mixing Query Results with Event Handlers**: Forcing the message bus to return business query results (a temporary symptom of mixing reads and writes before CQRS).

## Code Examples

### The Message Bus Queue Dispatcher

```python
# messagebus.py - Application Core
from typing import Dict, Type, List, Callable
import events
from unit_of_work import AbstractUnitOfWork

def handle(
    event: events.Event,
    uow: AbstractUnitOfWork,
) -> List[any]:
    results = []
    queue = [event]
    
    while queue:
        current_event = queue.pop(0)
        handlers = HANDLERS.get(type(current_event), [])
        for handler in handlers:
            results.append(handler(current_event, uow=uow))
            # Pull new events generated during aggregate mutation
            queue.extend(uow.collect_new_events())
            
    return results
```
- **What it demonstrates**: FIFO queue processing loop pulling newly generated events from `uow.collect_new_events()`.

### Unit of Work Collecting Events (Pull Pattern)

```python
# unit_of_work.py
import abc
from typing import Generator
import events

class AbstractUnitOfWork(abc.ABC):
    products: repository.AbstractProductRepository

    def commit(self) -> None:
        self._commit()

    def collect_new_events(self) -> Generator[events.Event, None, None]:
        for product in self.products.seen:
            while product.events:
                yield product.events.pop(0)

    @abc.abstractmethod
    def _commit(self) -> None:
        raise NotImplementedError
```
- **What it demonstrates**: UoW cleanly decouples from the message bus; it merely yields events from seen aggregates.

### Cascading Domain Event Workflow

```python
# model.py - Product Aggregate Handling Batch Quantity Change
class Product:
    ...
    def change_batch_quantity(self, ref: str, qty: int) -> None:
        batch = next(b for b in self.batches if b.reference == ref)
        batch.change_purchased_quantity(qty)
        while batch.available_quantity < 0:
            line = batch.deallocate_one()
            # Aggregate emits event requesting reallocation
            self.events.append(
                events.AllocationRequired(line.orderid, line.sku, line.qty)
            )
```

Handler mapping coordinating the workflow:
```python
# messagebus.py
HANDLERS: Dict[Type[events.Event], List[Callable]] = {
    events.BatchCreated: [handlers.add_batch],
    events.AllocationRequired: [handlers.allocate],
    events.BatchQuantityChanged: [handlers.change_batch_quantity],
    events.OutOfStock: [handlers.send_out_of_stock_notification],
}
```
- **What it demonstrates**: When a batch quantity shrinks, `Product` deallocates lines and emits `AllocationRequired`, which the bus re-routes to `handlers.allocate` on the next loop iteration.

## Reference Tables

### Evolution of the Message Bus Across Chapters

| Stage | Trigger Mechanism | Event Collection | Dependencies |
|---|---|---|---|
| **Ch 04 (Service Layer)** | Direct function calls (`services.allocate`) | None | Route → Services → Repo/Session |
| **Ch 08 (Side Effects)** | Service calls `messagebus.handle(event)` | UoW pushes events to bus | UoW imports Message Bus (circular risk) |
| **Ch 09 (Full Message Bus)** | Bus is primary entry point (`handle(event, uow)`) | Bus pulls events from UoW queue | Bus → Handlers → UoW (clean 1-way) |

## Worked Example

### Testing the Complete Event Cascade

```python
# test_handlers.py - High-level test driving workflows via messages
from unit_of_work import FakeUnitOfWork
import messagebus
import events

def test_reallocates_if_batch_quantity_decreases():
    uow = FakeUnitOfWork()
    
    # 1. Create two batches
    messagebus.handle(events.BatchCreated("batch-1", "RETRO-SOFA", 10, eta=None), uow)
    messagebus.handle(events.BatchCreated("batch-2", "RETRO-SOFA", 10, eta=None), uow)
    
    # 2. Allocate 10 units -> allocates to batch-1
    messagebus.handle(events.AllocationRequired("order-1", "RETRO-SOFA", 10), uow)
    
    batch1 = next(b for b in uow.products.get("RETRO-SOFA").batches if b.reference == "batch-1")
    assert batch1.available_quantity == 0

    # 3. Batch 1 quantity drops to 5 (e.g. damaged goods)
    # This triggers deallocation of order-1 and an AllocationRequired event
    # which reallocates order-1 to batch-2!
    messagebus.handle(events.BatchQuantityChanged("batch-1", 5), uow)

    batch2 = next(b for b in uow.products.get("RETRO-SOFA").batches if b.reference == "batch-2")
    assert batch2.available_quantity == 0  # Reallocated to batch-2!
```

## Key Takeaways
1. Converting an application into a message processor unifies internal side effects and external API calls under a single handler pattern.
2. The message bus uses an in-memory queue loop to process events and all secondary events triggered during execution.
3. Decouple the Unit of Work from the Message Bus by having the bus *pull* events via `uow.collect_new_events()`.
4. Event chains allow modeling complex, real-world "situated" business disruptions (like damaged stock) as clean, isolated steps.
5. High-level tests interact exclusively with message classes and the message bus, making the architecture highly resistant to internal refactoring.

## Connects To
- **Ch 08**: Events and the Message Bus — introduced the basic concept of domain events and pub/sub.
- **Ch 10**: Commands and Command Handlers — distinguishing events (past facts) from commands (imperative instructions).
- **Ch 11**: External Events — taking internal message bus events and broadcasting them over Redis/Kafka to other microservices.
