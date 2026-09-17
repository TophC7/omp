# Chapter 11: Event-Driven Architecture: Using Events to Integrate Microservices

## Core Idea
Integrating microservices via asynchronous event-driven messaging replaces tight temporal and execution coupling (the Distributed Big Ball of Mud) with weak connascence of name, allowing distributed systems to fail independently, scale horizontally, and evolve locally.

## Frameworks Introduced
- **The Distributed Ball of Mud Antipattern**: Designing microservices by carving systems into static nouns (`OrderService`, `BatchService`, `CustomerService`), exposing CRUD HTTP endpoints.
  - Failure mode: Creates extreme temporal coupling; placing an order triggers synchronous HTTP chains across four services. If one service is degraded or offline, the entire transaction fails, compounding failure rates exponentially.
  - Solution: Think in verbs and business workflows (`Ordering`, `Allocating`, `Shipping`).

- **Temporal Decoupling via Asynchronous Messaging**:
  - Services communicate across process boundaries by publishing events to an external message broker (Redis, Kafka, RabbitMQ, EventStore).
  - An upstream service commits its local aggregate and emits an event (e.g., `OrderPlaced`), immediately returning success to the user.
  - Downstream services consume the event asynchronously and execute subsequent use cases in their own independent transactions.

- **The Connascence Spectrum for System Coupling**:
  - *Connascence of Execution (Strong)*: Components must execute in an exact global order; changing one breaks the workflow.
  - *Connascence of Timing (Strong)*: Operations must happen synchronously within the same HTTP request timeframe.
  - *Connascence of Name / Structure (Weak)*: Components only need to agree on event names and JSON field contracts; execution time, order, and implementation language vary freely.
  - Goal: Strong cohesion/connascence locally within an aggregate; weak connascence at a distance across microservices.

- **External Event Adapters (Publishers and Consumers)**:
  - *Outbound Publisher*: An internal event handler subscribed on the in-memory message bus that serializes domain events to JSON and pushes them to a broker channel (e.g., Redis `PUBLISH line_allocated`).
  - *Inbound Consumer*: A long-running entry point script that listens on a broker channel (e.g., Redis `SUBSCRIBE change_batch_quantity`), deserializes JSON, instantiates internal Command objects, and dispatches them to `messagebus.handle(command, uow)`.

## Key Concepts
- **Temporal Coupling**: A dependency where two or more services must be operational, reachable, and responsive at the exact same millisecond for an operation to succeed.
- **Message Broker**: Infrastructure (Redis, RabbitMQ, Kafka) responsible for receiving published messages and delivering them to subscribers across network boundaries.
- **Choreography**: Microservices react autonomously to published events without a central coordinator dictating workflow steps.
- **Orchestration**: A central orchestrator service makes explicit RPC/HTTP command calls to worker services in a rigid sequence.
- **Idempotency**: Designing message handlers so that receiving the exact same message multiple times produces the identical final system state without duplicating side effects.
- **At-Least-Once Delivery**: The messaging guarantee where brokers re-deliver unacknowledged messages, requiring consumers to tolerate duplicate events.

## Mental Models
- **Walkie-Talkie Broadcast vs. Telephone Switchboard**: Synchronous HTTP RPC is like a 5-person phone conference call (if one person drops, the meeting halts); event-driven messaging is like a walkie-talkie broadcast (speak the message, release the button; listeners act when ready).
- **Thinking in Verbs, Not Nouns**: Do not design a `Customer` microservice and a `Batch` microservice; design an `Allocating` bounded context and a `Billing` bounded context.
- **Islands of Durability**: Each microservice is an autonomous island that receives messages, updates its local database atomically, and broadcasts new events.

## Anti-patterns
- **The Microservice Monolith / Distributed Ball of Mud**: Splitting code into 20 microservices that make synchronous nested HTTP calls to one another to complete a single user transaction.
- **Two-Phase Commit (2PC) over Microservices**: Attempting distributed ACID transactions across multiple microservice databases, creating extreme latency and failure brittleness.
- **Unchecked Duplicate Processing**: Assuming the network delivers each message exactly once, leading to double billing or duplicate stock allocations on retry.
- **Database Sharing across Microservices**: Allowing multiple microservices to read and write to the same relational tables, completely destroying service boundaries.

## Code Examples

### Outbound Event Publisher (Adapter)

```python
# adapters/redis_eventpublisher.py
import json
import logging
from dataclasses import asdict
import redis
import config
import events

logger = logging.getLogger(__name__)
r = redis.Redis(**config.get_redis_host_and_port())

def publish(channel: str, event: events.Event) -> None:
    logging.debug("Publishing: channel=%s, event=%s", channel, event)
    r.publish(channel, json.dumps(asdict(event)))
```

Subscribing the publisher on the internal message bus:
```python
# service_layer/messagebus.py
from adapters import redis_eventpublisher

def publish_allocated_event(event: events.Allocated, uow: unit_of_work.AbstractUnitOfWork) -> None:
    redis_eventpublisher.publish("line_allocated", event)

EVENT_HANDLERS = {
    events.Allocated: [publish_allocated_event],
    events.OutOfStock: [handlers.send_out_of_stock_notification],
}
```
- **What it demonstrates**: When `Allocated` is raised internally, the message bus routes it to `publish_allocated_event`, broadcasting it to Redis without domain awareness.

### Inbound Event Consumer (Entry Point)

```python
# entrypoints/redis_eventconsumer.py
import json
import logging
import redis
import config
from domain import commands
from service_layer import messagebus, unit_of_work

logger = logging.getLogger(__name__)
r = redis.Redis(**config.get_redis_host_and_port())

def main():
    pubsub = r.pubsub(ignore_subscribe_messages=True)
    pubsub.subscribe("change_batch_quantity")

    for message in pubsub.listen():
        handle_change_batch_quantity(message)

def handle_change_batch_quantity(message):
    logging.debug("Handling %s", message)
    data = json.loads(message["data"])
    cmd = commands.ChangeBatchQuantity(ref=data["batchref"], qty=data["qty"])
    
    uow = unit_of_work.SqlAlchemyUnitOfWork()
    messagebus.handle(cmd, uow)

if __name__ == "__main__":
    main()
```
- **What it demonstrates**: The Redis consumer acts as an entry point (analogous to Flask), translating external JSON messages into internal commands and driving the message bus.

## Reference Tables

### Synchronous RPC (HTTP) vs. Asynchronous Messaging (Events)

| Dimension | Synchronous HTTP RPC | Asynchronous Event-Driven |
|---|---|---|
| **Coupling Type** | Connascence of Execution and Timing | Connascence of Name / Data |
| **Availability** | Multiplicative degradation ($0.99 \times 0.99 \times 0.99$) | Independent ($0.99$ per service) |
| **Latency** | Sum of all nested service round-trips | Immediate local response |
| **Failure Mode** | Cascades across entire call stack | Localized; consumer retries later |
| **Consistency** | Often attempts pseudo-immediate consistency | Explicitly eventual consistency |
| **Complexity** | Low initial tooling setup | Requires message brokers, idempotency, dlqs |

## Worked Example

### End-to-End Integration Testing with Redis

```python
# tests/e2e/test_external_events.py
import json
import pytest
from tenacity import Retrying, stop_after_delay
from . import api_client, redis_client

def test_external_batch_quantity_change_triggers_reallocation():
    # 1. Setup two batches via HTTP API
    sku, orderid = "HIGHBROW-LAMP", "order-456"
    earlier_batch = "batch-old"
    later_batch = "batch-new"
    
    api_client.post_to_add_batch(earlier_batch, sku, qty=10, eta="2026-05-01")
    api_client.post_to_add_batch(later_batch, sku, qty=10, eta="2026-05-02")
    
    # 2. Allocate 10 units -> allocates to earlier_batch
    resp = api_client.post_to_allocate(orderid, sku, 10)
    assert resp.json()["batchref"] == earlier_batch

    # 3. Subscribe to outbound Redis channel
    sub = redis_client.subscribe_to("line_allocated")

    # 4. Publish external event: earlier_batch quantity dropped to 5
    redis_client.publish_message(
        "change_batch_quantity",
        {"batchref": earlier_batch, "qty": 5}
    )

    # 5. Wait for consumer to process and publish new allocation to later_batch
    for attempt in Retrying(stop=stop_after_delay(5), reraise=True):
        with attempt:
            msg = sub.get_message(timeout=1)
            assert msg is not None
            data = json.loads(msg["data"])
            assert data["orderid"] == orderid
            assert data["batchref"] == later_batch
```

## Key Takeaways
1. Avoid the Distributed Ball of Mud by modeling business services around verbs and workflows rather than static database nouns.
2. Replace synchronous HTTP chains with asynchronous messaging to achieve temporal decoupling and fault isolation.
3. Use Connascence as an architectural guide: replace strong execution/timing coupling with weak name/data coupling.
4. Integrate the external broker symmetrically: use outbound publishers subscribed to internal events and inbound consumers that dispatch internal commands.
5. In distributed systems, networks duplicate and delay messages; design consumer handlers to be strictly idempotent.

## Connects To
- **Ch 09**: Going to Town on the Message Bus — the internal message processor driven by external event consumers.
- **Ch 10**: Commands and Command Handlers — translating incoming external JSON into typed commands.
- **Ch 12**: CQRS — separating the command/event write pipeline from high-performance read models.
