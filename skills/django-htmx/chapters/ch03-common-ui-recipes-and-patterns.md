# Chapter 3: Common UI Recipes & Patterns

## Core Idea
HTMX replaces hundreds of lines of complex client-side state management and component code with declarative HTML recipes for common web UI patterns, including active search, lazy loading, inline validation, modal dialogs, infinite scroll, and click-to-edit.

## Frameworks Introduced
- **Progressive Enhancement via Boosting (`hx-boost`)**:
  - Automatically transforms traditional `<a>` navigation links and `<form>` submissions into AJAX calls.
  - How: Put `hx-boost="true"` on a container (e.g. `<body>` or `<nav>`). When a link or form is triggered, HTMX intercepts the request, fetches the destination HTML via AJAX, extracts the `<body>` content, replaces the current body, and pushes the new URL into the browser history.
  - Fallback: If JavaScript is disabled or fails to load, links and forms continue to function as standard full-page HTTP requests.

- **The Active Search Recipe (Debounce + Changed)**:
  - Pattern: Search-as-you-type input that issues requests only when the user pauses typing and the value has actually changed.
  - Trigger formula: `hx-trigger="keyup changed delay:300ms, search"`.
  - `changed`: Suppresses requests if navigation keys (arrows, Shift, Ctrl) were pressed without altering the input text.
  - `delay:300ms`: Debounces keystrokes, resetting the timer with each character typed.
  - `search`: Listens for clearing the input via the browser search box clear icon.

- **The Click-to-Edit State Machine**:
  - Two-state hypermedia pattern:
    1. *Display State*: Element shows formatted read-only data with an "Edit" button (`hx-get="/item/1/edit/"` targeting the container with `hx-swap="outerHTML"`).
    2. *Edit State*: Server returns an HTML `<form>` containing pre-populated inputs and two buttons: "Save" (`hx-put="/item/1/"`) and "Cancel" (`hx-get="/item/1/"` returning the display view).
  - Eliminates client-side form toggling, state serialization, and validation synchronization.

- **Lazy Loading & Infinite Scroll via Viewport Triggers**:
  - `load`: Fires immediately when the element enters the DOM (used for deferring heavy charts or slow stats).
  - `revealed`: Fires when the element is scrolled into the visible browser viewport (used for infinite scrolling and lazy-loaded image lists).

## Key Concepts
- **`hx-boost`**: Progressive enhancement switch converting links and forms into AJAX calls with history updates.
- **`hx-confirm`**: Displays a native browser confirmation prompt (`window.confirm`) before sending the request.
- **`hx-prompt`**: Displays a prompt dialog, passing the user-entered string to the server via the `HX-Prompt` request header.
- **`hx-sync`**: Controls request concurrency on an element (`drop`, `abort`, `replace`, `queue`), preventing race conditions during rapid user input.
- **`hx-disabled-elt`**: Disables specific buttons or form controls while a request is in flight (`hx-disabled-elt="this"` or `hx-disabled-elt="find button"`).
- **Inline Validation**: Server-driven input validation firing on `blur` or `change`, returning targeted error messages next to the input.
- **Polling (`every <interval>`)**: Periodically re-executing an HTTP request to update dashboard counters or progress bars.

## Mental Models
- **Hypermedia State Swapping**: Instead of maintaining a boolean `isEditing = true` flag in JavaScript memory and conditionally rendering DOM branches, let the server return the markup for the exact state requested. State lives in the markup returned by the server.
- **The Debounce Dam**: Think of `delay:300ms` as a dam holding back network requests. Each keypress raises the dam; water only spills over when the user pauses typing.
- **Progressive Fallback**: `hx-boost` acts as an accelerator on standard web architecture, not a replacement. If HTMX fails, the web page still works like standard HTML 1.0.

## Anti-patterns
- **Unthrottled `keyup` Triggers**: Using `hx-trigger="keyup"` without `changed delay:300ms`, sending an HTTP request on every single letter, arrow key, and shift key press, flooding the backend database.
- **Client-Side Validation Only**: Validating forms only with JavaScript. HTMX encourages server-side validation that returns rich, styled error messages matching backend constraints precisely.
- **Infinite Polling Without Circuit Breakers**: Setting `hx-trigger="every 1s"` on elements that never stop polling, draining mobile batteries and overloading servers. Prefer event-triggered updates (`HX-Trigger`) or back off to longer intervals.
- **Missing Double-Submit Prevention**: Not disabling submit buttons during in-flight POST requests, allowing impatient users to click "Pay" or "Submit" multiple times. Always use `hx-disabled-elt="this"`.

## Code Examples

### 1. Active Search Table
```html
<!-- Search bar with debounce, change detection, and loading spinner -->
<div class="search-widget">
  <input type="search"
         name="q"
         placeholder="Filter by name, email, or role..."
         hx-get="/users/search/"
         hx-trigger="keyup changed delay:300ms, search"
         hx-target="#user-tbody"
         hx-indicator="#search-loading">
  
  <span id="search-loading" class="htmx-indicator">Searching...</span>
</div>

<table>
  <thead>
    <tr><th>Name</th><th>Email</th><th>Role</th></tr>
  </thead>
  <tbody id="user-tbody">
    <!-- Initial server-rendered rows -->
    <tr><td>Alice Smith</td><td>alice@corp.internal</td><td>Engineer</td></tr>
  </tbody>
</table>
```

### 2. Inline Field Validation
```html
<form hx-post="/accounts/register/" hx-target="#form-container">
  <div class="form-group">
    <label>Username</label>
    <input type="text"
           name="username"
           value="alicesmith"
           hx-post="/accounts/validate-username/"
           hx-trigger="blur"
           hx-target="next .error-message"
           hx-sync="this:replace">
    <div class="error-message">
      <!-- Empty if valid; server returns error markup if taken -->
    </div>
  </div>
  <button type="submit" hx-disabled-elt="this">Register</button>
</form>
```

### 3. Click-to-Edit Pattern
```html
<!-- Display State (rendered by /profile/1/ or cancel action) -->
<div id="contact-1" class="card">
  <p><strong>Name:</strong> Jane Doe</p>
  <p><strong>Email:</strong> jane@example.com</p>
  <button hx-get="/profile/1/edit/"
          hx-target="#contact-1"
          hx-swap="outerHTML">
    Edit Contact
  </button>
</div>

<!-- Edit State (returned by /profile/1/edit/) -->
<form id="contact-1"
      class="card edit-mode"
      hx-put="/profile/1/"
      hx-target="#contact-1"
      hx-swap="outerHTML">
  <label>Name: <input type="text" name="name" value="Jane Doe"></label>
  <label>Email: <input type="email" name="email" value="jane@example.com"></label>
  <div class="button-group">
    <button type="submit" class="btn-primary">Save Changes</button>
    <button type="button"
            class="btn-secondary"
            hx-get="/profile/1/"
            hx-target="#contact-1"
            hx-swap="outerHTML">
      Cancel
    </button>
  </div>
</form>
```

### 4. Infinite Scroll with Viewport Reveal
```html
<!-- Table rows ending with a sentinel row for the next page -->
<tr id="item-20">
  <td>Product 20</td>
  <td>$19.99</td>
</tr>

<!-- Sentinel row: triggers fetch when scrolled into view -->
<tr hx-get="/products/?page=2"
    hx-trigger="revealed"
    hx-target="this"
    hx-swap="outerHTML">
  <td colspan="2" class="text-center">Loading more products...</td>
</tr>
```

## Reference Tables

### Common UI Recipes Decision Matrix
| UI Requirement | Trigger Configuration | Target & Swap Strategy | Essential Attributes |
|:---|:---|:---|:---|
| **Search-as-you-type** | `keyup changed delay:300ms, search` | `hx-target="#results" hx-swap="innerHTML"` | `hx-indicator` |
| **Inline Validation** | `blur` or `change` | `hx-target="next .err" hx-swap="innerHTML"` | `hx-sync="this:replace"` |
| **Lazy Loading** | `load` | `hx-target="this" hx-swap="outerHTML"` | Skeleton placeholder |
| **Infinite Scroll** | `revealed` | `hx-target="this" hx-swap="outerHTML"` | Sentinel row / loader |
| **Click-to-Edit** | `click` (Edit), `submit` (Save) | `hx-target="closest .card" hx-swap="outerHTML"` | Display / Edit sub-templates |
| **Delete Row** | `click` | `hx-target="closest tr" hx-swap="outerHTML swap:300ms"` | `hx-confirm`, CSS fade |
| **Periodic Polling** | `every 5s` | `hx-target="this" hx-swap="innerHTML"` | Server load ceiling |
| **Modal Dialog** | `click` | `hx-target="#modal-container" hx-swap="innerHTML"` | Backdrop close handler |

### `hx-sync` Concurrency Control
| Setting | Behavior | Use Case |
|:---|:---|:---|
| `this:drop` | Drops new request if one is already in flight | Double-click protection |
| `this:abort` | Aborts current in-flight request and starts new one | Autocomplete typing |
| `this:replace` | Aborts pending request and replaces queue | Rapid field validation |
| `this:queue` | Queues requests to execute sequentially in order | Batch command execution |

## Worked Example

### Complete Modal Dialog Flow
A complete server-driven modal dialog lifecycle without frontend JavaScript modal frameworks:

**1. Base Page Container:**
```html
<main>
  <h1>Order Management</h1>
  <button hx-get="/orders/new/modal/"
          hx-target="#modal-host"
          hx-swap="innerHTML">
    Create Order
  </button>

  <!-- Empty mount point for modals -->
  <div id="modal-host"></div>
</main>
```

**2. Server Endpoint (`/orders/new/modal/`) Returns Modal HTML:**
```html
<div class="modal-backdrop"
     id="order-modal"
     hx-on:click="if(event.target === this) this.remove()">
  <div class="modal-content">
    <header>
      <h3>Create New Order</h3>
      <button type="button" class="close" onclick="document.getElementById('order-modal').remove()">✕</button>
    </header>
    
    <form hx-post="/orders/"
          hx-target="#order-table tbody"
          hx-swap="beforeend"
          hx-on::after-request="if(event.detail.successful) document.getElementById('order-modal').remove()">
      <div class="form-group">
        <label>Customer Name</label>
        <input type="text" name="customer" required>
      </div>
      <div class="form-group">
        <label>Total Amount ($)</label>
        <input type="number" step="0.01" name="amount" required>
      </div>
      <footer class="modal-actions">
        <button type="button" onclick="document.getElementById('order-modal').remove()">Cancel</button>
        <button type="submit" class="btn-primary" hx-disabled-elt="this">Submit Order</button>
      </footer>
    </form>
  </div>
</div>
```

**3. Execution Flow:**
1. User clicks "Create Order"; GET request fetches modal markup into `#modal-host`.
2. Modal renders on screen. Backdrop click or Cancel calls `.remove()` to dismiss.
3. Submitting the form issues POST to `/orders/`.
4. On success (`event.detail.successful`), the new row appends to `#order-table tbody`, and `hx-on::after-request` removes the modal from the DOM.

## Key Takeaways
1. Active search requires both `changed` and `delay:<time>` to protect backend servers from superfluous keystroke queries.
2. The Click-to-Edit pattern eliminates complex client-side UI state by replacing display markup with edit form markup on demand.
3. `hx-boost` delivers instant SPA-like navigation speed to classic multi-page applications with zero JavaScript configuration.
4. `hx-sync` provides bulletproof concurrency controls (`drop`, `abort`, `replace`, `queue`) for high-frequency user interactions.
5. Modal dialogs, infinite scroll, and lazy loading require only hypermedia swapping, eliminating heavyweight UI component libraries.

## Connects To
- **Ch 02**: Endpoints, Targets & Swaps — mechanics of target resolution and swap timing.
- **Ch 05**: HTMX JavaScript API & Lifecycle — customizing request lifecycle events like `htmx:afterRequest`.
- **Ch 09**: Django HTMX Interactive Patterns — implementing these exact recipes with Django ORM, Paginator, and ModelForms.
