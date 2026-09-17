# Chapter 7: Real-Time Streaming with WebSockets & SSE

## Core Idea
HTMX extends hypermedia beyond classic request/response cycles through official extensions for Server-Sent Events (SSE) and WebSockets, enabling servers to push live HTML updates directly into the DOM over persistent connections without client-side message parsing or state management.

## Frameworks Introduced
- **The Push Hypermedia Architecture**:
  - In traditional web sockets or stream implementations, servers push JSON payloads, and client-side JavaScript must parse the JSON, locate target DOM nodes, and construct HTML elements.
  - In HTMX Push Hypermedia, the server pushes raw HTML fragments directly over the stream. HTMX intercepts the incoming message and performs target swapping or Out-of-Band (`hx-swap-oob`) mutations identically to regular HTTP responses.
  - Result: The exact same partial templates used for HTTP GET/POST requests can be broadcast over WebSockets and SSE streams with zero frontend code modification.

- **The Real-Time Protocol Decision Framework**:
  - *Server-Sent Events (SSE)*:
    - Unidirectional (Server → Client).
    - Runs over standard HTTP/1.1 or HTTP/2 (`Content-Type: text/event-stream`).
    - Built-in automatic browser reconnection and connection retry backoff.
    - Works through existing corporate firewalls, HTTP proxies, and load balancers without special routing.
    - *Best for*: Live status feeds, dashboard telemetry, notification bells, progress bars, background task monitors.
  - *WebSockets (WS)*:
    - Bidirectional, full-duplex TCP communication.
    - Requires protocol upgrade handshake (`101 Switching Protocols`).
    - Supports sending client commands directly across the socket (`ws-send`).
    - Requires custom heartbeat / reconnection logic if connection drops.
    - *Best for*: High-frequency two-way chats, collaborative document editing, real-time multiplayer applications.

## Key Concepts
- **`hx-ext="sse"`**: HTMX extension enabling Server-Sent Events integration.
- **`sse-connect="url"`**: Opens a persistent SSE connection to the specified endpoint on element mount.
- **`sse-swap="eventName"`**: Listens for a specific named event within the SSE stream and swaps its HTML payload into the target.
- **`hx-ext="ws"`**: HTMX extension enabling full-duplex WebSocket integration.
- **`ws-connect="url"`**: Opens a WebSocket connection to the specified URL (`ws://` or `wss://`).
- **`ws-send`**: Form or element attribute that serializes and transmits values across the active WebSocket without an HTTP request.
- **Streaming Out-of-Band Swaps**: Incoming SSE or WebSocket HTML frames containing elements with `hx-swap-oob="true"` immediately update matching DOM elements anywhere on the page.

## Mental Models
- **The Ticker Tape vs The Walkie-Talkie**:
  - SSE is a stock ticker tape: The machine in the room continuously prints printed strips of paper (HTML) from headquarters. The client never talks back to the machine; if the client wants to place an order, they pick up the phone (an HTMX `hx-post` request).
  - WebSockets is a walkie-talkie: Both parties hold open lines and transmit messages directly back and forth on the same radio frequency.
- **The Universal Payload Format**: Whether an HTML fragment arrives via HTTP 200, an SSE stream line, or a WebSocket frame, the browser treats it identically: it is hypermedia swapped directly into place.

## Anti-patterns
- **Using WebSockets When Unidirectional SSE Suffices**: Adopting full WebSockets for read-only notifications, requiring complex ASGI infrastructure, protocol upgrade handling, and manual reconnection managers when simple SSE over HTTP is sufficient.
- **Transmitting JSON Over HTMX WebSockets**: Sending `{ "id": 4, "text": "Hello" }` across an HTMX WebSocket and writing client-side JavaScript to render it, defeating the entire hypermedia paradigm. Always transmit server-rendered HTML fragments over the socket.
- **Unbounded SSE Stream Memory Leaks**: Holding database connections or server threads open indefinitely per client without periodic ping heartbeats, causing server connection pool exhaustion under load.
- **Forgetting Out-of-Band Swaps in Live Streams**: Creating separate WebSocket channels for each individual UI widget instead of broadcasting a single HTML message containing OOB tags (`hx-swap-oob="true"`) to update the feed, counter, and status bar at once.

## Code Examples

### 1. Real-Time Dashboard Metrics via Server-Sent Events (SSE)
```html
<!-- Load the SSE extension -->
<script src="https://unpkg.com/htmx.org@1.9.10/dist/ext/sse.js"></script>

<!-- Connect to SSE stream on dashboard container -->
<div class="dashboard-grid"
     hx-ext="sse"
     sse-connect="/stream/system-metrics/">

  <!-- Panel 1: CPU Usage (listens for 'cpu-update' events) -->
  <div class="metric-card">
    <h3>CPU Utilization</h3>
    <div sse-swap="cpu-update" hx-swap="innerHTML">
      <div class="bar" style="width: 15%;">15%</div>
    </div>
  </div>

  <!-- Panel 2: Live Activity Feed (prepends new events) -->
  <div class="feed-card">
    <h3>Recent Events</h3>
    <ul id="event-log" sse-swap="system-log" hx-swap="afterbegin">
      <li>Server initialized</li>
    </ul>
  </div>
</div>
```

**Server SSE Event Stream Output (`Content-Type: text/event-stream`):**
```http
event: cpu-update
data: <div class="bar" style="width: 74%;">74%</div>

event: system-log
data: <li>Backup job #402 completed in 1.2s</li>

```

### 2. Real-Time Chat Room with WebSockets
```html
<!-- Load the WebSockets extension -->
<script src="https://unpkg.com/htmx.org@1.9.10/dist/ext/ws.js"></script>

<!-- Establish WebSocket connection -->
<div class="chat-container"
     hx-ext="ws"
     ws-connect="/ws/chat/room-general/">

  <!-- Message Log (Incoming messages append here by default or via OOB) -->
  <div id="chat-messages" class="message-window">
    <div class="msg system">Connected to #general</div>
  </div>

  <!-- Message Input Form (Submits over WebSocket via ws-send) -->
  <form ws-send
        hx-on::ws-after-send="this.reset()">
    <input type="text"
           name="message"
           placeholder="Type your message..."
           autocomplete="off"
           required>
    <button type="submit">Send</button>
  </form>
</div>
```

**Incoming WebSocket Frame from Server (Pushed to all room participants):**
```html
<div id="chat-messages" hx-swap-oob="beforeend">
  <div class="msg user-msg">
    <strong>Gabriel:</strong> All test suites passed!
  </div>
</div>
```

## Reference Tables

### SSE vs WebSockets Comparison Matrix
| Architectural Dimension | Server-Sent Events (SSE) | WebSockets (WS) |
|:---|:---|:---|
| **Directionality** | Unidirectional (Server → Client) | Bidirectional (Server ↔ Client) |
| **Protocol** | Standard HTTP (`text/event-stream`) | Upgraded TCP protocol (`ws://`, `wss://`) |
| **Reconnection** | Automatic native browser retry | Manual retry / extension reconnection logic |
| **HTTP/2 Multiplexing** | Fully supported (multiple streams over 1 TCP) | No (each socket is a distinct TCP stream) |
| **Firewall & Proxy Compatibility**| Seamless (standard port 80/443 HTTP traffic)| Can be blocked or terminated by strict corporate proxies |
| **Message Format** | UTF-8 Text only (ideal for HTML) | Text and Binary |
| **Best Used With HTMX** | Metrics, notifications, progress, logs | Collaborative boards, high-speed gaming, chat |

### HTMX Streaming Attributes
| Attribute | Extension | Placement | Purpose |
|:---|:---|:---|:---|
| `hx-ext="sse"` | SSE | Parent container | Activates SSE extension for descendants |
| `sse-connect="url"` | SSE | Element holding stream | Connects to specified SSE streaming endpoint |
| `sse-swap="eventName"` | SSE | Target element | Swaps HTML whenever named event is pushed |
| `hx-ext="ws"` | WebSockets | Parent container | Activates WebSockets extension |
| `ws-connect="url"` | WebSockets | Connection root | Opens WebSocket to target endpoint |
| `ws-send` | WebSockets | `<form>` or button | Sends form payload directly across WebSocket |

## Worked Example

### Live Long-Running Background Task Progress Monitor
A user kicks off a heavy background report generation job (e.g. exporting 100,000 database records) and receives continuous real-time progress updates without polling:

**1. Initial Trigger Page:**
```html
<div id="export-panel">
  <button hx-post="/reports/generate/"
          hx-target="#export-panel"
          hx-swap="outerHTML">
    Start Comprehensive Data Export
  </button>
</div>
```

**2. Server Endpoint Starts Background Job & Returns SSE Monitor:**
When POST is received, server enqueues worker job with ID `exp-99` and immediately returns:

```html
<div id="export-panel"
     hx-ext="sse"
     sse-connect="/reports/progress/exp-99/">
  <h3>Export in Progress...</h3>
  <div id="progress-bar-container" sse-swap="progress-tick" hx-swap="innerHTML">
    <div class="progress-bar" style="width: 0%;">0%</div>
  </div>
  <p id="export-status" sse-swap="status-tick" hx-swap="innerHTML">
    Initializing database snapshot...
  </p>
</div>
```

**3. Worker Publishes SSE Updates:**
```http
event: progress-tick
data: <div class="progress-bar" style="width: 45%;">45%</div>

event: status-tick
data: Processed 45,000 of 100,000 records...

event: progress-tick
data: <div class="progress-bar completed" style="width: 100%;">100%</div>

event: status-tick
data: <span>Export finished! <a href="/reports/download/exp-99.csv">Download CSV</a></span>
```

**Result**: Progress updates fluidly in real-time over a single lightweight HTTP connection without client polling or JavaScript framework overhead.

## Key Takeaways
1. HTMX extensions (`sse` and `ws`) enable real-time streaming using server-rendered HTML fragments instead of raw JSON.
2. Server-Sent Events (SSE) should be the default choice for real-time web UI updates due to native auto-reconnection and HTTP/2 multiplexing.
3. Reserve WebSockets for applications requiring high-frequency two-way communication directly from the browser.
4. Out-of-Band swaps (`hx-swap-oob`) work seamlessly over streaming connections, allowing one push event to update multiple page components.
5. Hypermedia streaming drastically simplifies backend architectures by allowing the same template fragments used for REST views to power live stream broadcasts.

## Connects To
- **Ch 02**: Endpoints, Targets & Swaps — mechanics of Out-of-Band (`hx-swap-oob`) updates.
- **Ch 03**: Common UI Recipes & Patterns — comparing polling against real-time push streams.
- **Ch 08**: Django HTMX Foundations — pairing Django Channels / streaming responses with HTMX.
