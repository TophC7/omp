# Chapter 2: Endpoints, Targets & Swaps

## Core Idea
HTMX decouples the network request trigger from the DOM mutation target, allowing endpoints to update multiple disparate regions of the page in a single HTTP response using flexible target selectors, fine-grained swap strategies, Out-of-Band (OOB) swaps, and server response headers.

## Frameworks Introduced
- **The Target Resolution Hierarchy**:
  - Direct Selector: Specific ID or class query (`#cart-count`, `.panel-body`).
  - Relative Traversal:
    - `this`: Targets the element issuing the request.
    - `closest <selector>`: Traverses up ancestor chain to find nearest matching parent (ideal for table rows `closest tr` or cards `closest .card`).
    - `find <selector>`: Searches descendants within the current element.
    - `next <selector>` / `previous <selector>`: Scans adjacent siblings in the DOM.

- **The Out-of-Band (OOB) Swap Pattern**:
  - Problem: An action updates a primary element (e.g. adding an item to a list) but also needs to update distant secondary widgets (e.g. updating a badge counter in the navbar, showing a toast notification, clearing a summary banner).
  - Solution: Return the primary HTML fragment alongside secondary elements marked with `hx-swap-oob="true"` (matching by ID) or `hx-swap-oob="<swap-style>:<selector>"`.
  - Invariant: A response may contain multiple OOB elements, but at most one element without `hx-swap-oob` (which populates the primary `hx-target`).

- **Server-Driven Control via Response Headers (`HX-*`)**:
  - The server controls client behavior dynamically through HTTP headers without embedding script tags:
    - Event dispatching: `HX-Trigger`, `HX-Trigger-After-Swap`, `HX-Trigger-After-Settle`.
    - History & URL state: `HX-Push-Url`, `HX-Replace-Url`.
    - Client navigation: `HX-Redirect`, `HX-Refresh`.
    - Dynamic targeting override: `HX-Retarget`, `HX-Reswap`.

## Key Concepts
- **`hx-target`**: Attribute specifying which DOM element receives the server response.
- **`hx-swap`**: Attribute controlling insertion mechanics and animation timings.
- **`hx-swap-oob`**: Attribute placed on response HTML elements to update DOM nodes outside the primary target.
- **`hx-select`**: Selects a subset of the returned HTML response to swap, discarding the rest (allows reusing full-page templates as partial endpoints).
- **`hx-select-oob`**: Selects fragments from the response specifically for out-of-band updates.
- **`HX-Trigger`**: Response header sending event names (or JSON event payloads) dispatched on the `<body>` upon response arrival.
- **`HX-Push-Url`**: Response header updating the browser address bar and history stack without full reload.
- **Swap Lifecycle Timing**: Phased DOM update: (1) content fetched, (2) `swap:<time>` transition delay, (3) DOM swap, (4) `settle:<time>` transition settlement.

## Mental Models
- **Target as the Destination Port**: Think of `hx-target` as the delivery address. If omitted, delivery returns to sender (`this`). Relative targets (`closest tr`) make list items portable and reusable.
- **The Trojan Horse Response (OOB Swaps)**: The primary response delivers the main payload to the designated target port, but smuggles secondary payloads (`hx-swap-oob="true"`) that independently fly to their respective IDs across the document.
- **Headers as Remote Control Signals**: Response headers act as an out-of-band control channel. While the body delivers markup, headers instruct the browser to re-route, push history, or ring event bells.

## Anti-patterns
- **Hardcoding Global Element IDs on Repeated Components**: Using `hx-target="#delete-btn"` inside a list template instead of relative targeting `hx-target="closest tr"`. In a loop of 50 items, every button targets the first item's ID.
- **Multiple Simultaneous AJAX Calls Instead of One OOB Response**: Firing 3 separate HTTP requests to update a list, a counter, and a flash message, causing race conditions and server overhead.
- **Returning Full Pages When `hx-select` Is Omitted**: Returning a complete 50KB HTML document with `<head>` and scripts into an `innerHTML` target without `hx-select`, producing nested `<html>` tags and memory leaks.
- **Using 204 No Content When Expecting `HX-Trigger` Execution**: Browsers and HTMX process 204 responses differently; if returning empty content with headers, return `200 OK` with an empty body to ensure HTMX triggers process cleanly.

## Code Examples

### Target Selection & Swap Modifiers
```html
<!-- Table with relative row targeting and animated deletion -->
<table>
  <tbody>
    <tr id="row-42">
      <td>Database Backup</td>
      <td>
        <button hx-delete="/backups/42/"
                hx-target="closest tr"
                hx-swap="outerHTML swap:400ms settle:200ms"
                hx-confirm="Delete backup?">
          Delete
        </button>
      </td>
    </tr>
  </tbody>
</table>

<style>
/* HTMX adds .htmx-swapping during the swap delay */
tr.htmx-swapping {
  opacity: 0;
  transition: opacity 400ms ease-out;
}
</style>
```

### Out-of-Band Response from Server
When a user clicks "Add to Cart", the server returns this single payload:

```html
<!-- Primary payload swapped into #item-card -->
<div class="alert alert-success">Item added to cart!</div>

<!-- Out-of-Band payload 1: updates cart counter in navbar -->
<span id="cart-counter" hx-swap-oob="true" class="badge">
  5 items
</span>

<!-- Out-of-Band payload 2: appends to toast notification tray -->
<div id="toast-tray" hx-swap-oob="beforeend">
  <div class="toast">Added "Mechanical Keyboard" to cart.</div>
</div>
```

### Server Event Dispatching (`HX-Trigger`)
```python
# Server endpoint (Python/Django example)
from django.http import HttpResponse
import json

def update_status(request, task_id):
    task = Task.objects.get(id=task_id)
    task.completed = True
    task.save()
    
    response = HttpResponse(f'<span class="badge completed">Done</span>')
    # Trigger client-side events with optional data payloads
    response["HX-Trigger"] = json.dumps({
        "taskCompleted": {"taskId": task_id},
        "refreshSummary": True
    })
    return response
```

```html
<!-- Client element listening for the event from body -->
<div hx-get="/tasks/summary/"
     hx-trigger="refreshSummary from:body"
     hx-target="this">
  <!-- Re-renders summary automatically whenever any task completes -->
</div>
```

## Reference Tables

### The 8 Swap Strategies (`hx-swap`)
| Strategy | Action | Target Kept? | Common Use Case |
|:---|:---|:---|:---|
| `innerHTML` *(default)* | Replaces child elements of target | Yes | Updating panel contents, list bodies |
| `outerHTML` | Replaces target element entirely | No | Replacing row, toggling edit form |
| `beforebegin` | Inserts response immediately before target | Yes | Adding item before an anchor |
| `afterbegin` | Inserts response inside target before first child | Yes | Prepending newest items to a feed |
| `beforeend` | Inserts response inside target after last child | Yes | Appending items, infinite scroll |
| `afterend` | Inserts response immediately after target | Yes | Expanding an inline details row |
| `delete` | Deletes target element regardless of response | No | Deletion buttons |
| `none` | Does not mutate the DOM at all | Yes | Requests only running for side-effects or headers |

### Swap Modifiers Syntax
| Modifier | Example | Effect |
|:---|:---|:---|
| `swap:<time>` | `hx-swap="outerHTML swap:300ms"` | Delays DOM swap to allow CSS fade/slide out animations |
| `settle:<time>` | `hx-swap="innerHTML settle:200ms"` | Delays removal of `.htmx-settling` class after swap |
| `transition:true` | `hx-swap="innerHTML transition:true"` | Triggers browser View Transitions API for animated cross-fades |
| `scroll:top\|bottom` | `hx-swap="beforeend scroll:bottom"` | Automatically scrolls target to top or bottom after insertion |
| `show:top\|bottom` | `hx-swap="innerHTML show:#top-nav:top"` | Scrolls window to show selected element |
| `focus-scroll:true\|false` | `hx-swap="innerHTML focus-scroll:false"` | Disables browser auto-scrolling to focused inputs |

### HTMX Response Headers Reference
| Header | Value / Type | Purpose |
|:---|:---|:---|
| `HX-Trigger` | Event name or JSON map | Dispatches events on `<body>` immediately upon receiving response |
| `HX-Trigger-After-Swap` | Event name or JSON map | Dispatches events after DOM insertion completes |
| `HX-Trigger-After-Settle` | Event name or JSON map | Dispatches events after animation settling finishes |
| `HX-Push-Url` | URL string or `false` | Pushes URL into browser history stack (or prevents history push) |
| `HX-Replace-Url` | URL string or `false` | Replaces current URL in browser history |
| `HX-Redirect` | URL string | Forces client to perform a full-window navigation to URL |
| `HX-Refresh` | `"true"` | Forces client browser to reload the current page entirely |
| `HX-Retarget` | CSS selector | Overrides `hx-target` on the client dynamically from the server |
| `HX-Reswap` | Swap strategy string | Overrides `hx-swap` on the client dynamically from the server |

## Worked Example

### Out-of-Band Multi-Region Dashboard Update
A project task dashboard where completing a task:
1. Replaces the task item with a completed state.
2. Updates the project progress bar out-of-band.
3. Decrements the open task counter badge in the header out-of-band.

**Client Page Markup:**
```html
<!-- Header with badge -->
<header>
  <h1>Project Delta</h1>
  <span id="open-count" class="badge">3 open</span>
</header>

<!-- Progress Bar -->
<div id="progress-container">
  <div id="progress-bar" style="width: 25%;">25% Completed</div>
</div>

<!-- Task List -->
<ul id="task-list">
  <li id="task-1">
    <span>Write architectural specs</span>
    <button hx-post="/tasks/1/complete/"
            hx-target="#task-1"
            hx-swap="outerHTML">
      Mark Done
    </button>
  </li>
</ul>
```

**Server Response (Single HTTP POST response to `/tasks/1/complete/`):**
```html
<!-- 1. Primary Target Replacement (#task-1) -->
<li id="task-1" class="task-done">
  <s>Write architectural specs</s>
  <span class="checkmark">✓ Completed</span>
</li>

<!-- 2. OOB Swap for Header Badge -->
<span id="open-count" hx-swap-oob="true" class="badge">
  2 open
</span>

<!-- 3. OOB Swap for Progress Bar -->
<div id="progress-bar" hx-swap-oob="true" style="width: 50%;">
  50% Completed
</div>
```

**Result**: All three UI components update in a single round-trip without page flicker or custom client JavaScript.

## Key Takeaways
1. Flexible target selectors (`this`, `closest`, `find`) allow writing reusable, component-local markup without brittle global IDs.
2. Out-of-Band (OOB) swaps allow a single HTTP response to update multiple disconnected DOM regions cleanly.
3. Swap timing modifiers (`swap:<time>`, `settle:<time>`) coordinate with CSS classes for smooth exit and entry animations.
4. Response headers (`HX-*`) give backend views direct programmatic control over client history, event buses, and redirects.
5. `hx-select` allows endpoints to return full templates while HTMX extracts only the desired sub-element.

## Connects To
- **Ch 01**: HTMX Foundations & Attributes — the core request/response model.
- **Ch 03**: Common UI Recipes & Patterns — applying targets, swaps, and OOB in common interactive widgets.
- **Ch 08**: Django HTMX Foundations — implementing `HX-Trigger` and OOB templates using Django views and partials.
