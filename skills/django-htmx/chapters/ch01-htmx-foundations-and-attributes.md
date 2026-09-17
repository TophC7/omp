# Chapter 1: HTMX Foundations & Core Attributes

## Core Idea
HTMX extends HTML into a full-featured hypermedia engine, enabling any HTML element to issue any HTTP request on any event and swap the returned HTML fragment directly into the DOM without full page reloads or client-side JavaScript boilerplate.

## Frameworks Introduced
- **HOWL (Hypermedia On Whatever you'd Like)**:
  - Core philosophy: The server can be built in any language or framework (Python/Django, Go, Rust, TypeScript) that can route HTTP requests and render HTML templates.
  - When to use: Architecting web applications where backend logic, domain rules, and validation reside centrally on the server instead of being duplicated in client-side JavaScript.
  - Invariant: Endpoints return HTML fragments (hypermedia representations), not raw JSON payloads meant for client-side template rendering.

- **The Six Questions Framework for HTMX**:
  - Every HTMX interaction answers six concrete questions declarative in HTML:
    1. *What causes the request?* → `hx-trigger` (default: `change` for `<input>`, `<select>`, `<textarea>`; `submit` for `<form>`; `click` for everything else).
    2. *What HTTP method is used?* → `hx-get`, `hx-post`, `hx-put`, `hx-patch`, or `hx-delete`.
    3. *Where is the request sent?* → The URL value of the method attribute (e.g., `hx-get="/items/"`).
    4. *What data is sent?* → Form inputs enclosed by default, or explicitly expanded with `hx-include` and `hx-vals`.
    5. *Where should the response be placed?* → `hx-target` (default: element issuing the request).
    6. *How should the response replace target content?* → `hx-swap` (default: `innerHTML`).

- **Locality of Behavior (LoB)**:
  - Software design principle: The behavior of a unit of code should be discoverable and understandable directly by inspecting that unit, rather than spread across distant JavaScript files, event listeners, and selector bindings.
  - How: Put the trigger, endpoint, target, and swap rules right on the HTML tag performing the action.

## Key Concepts
- **HATEOAS (Hypermedia As The Engine Of Application State)**: Architectural constraint where client state is managed entirely through hypermedia (HTML) provided dynamically by the server, rather than client-side state stores (Redux, Pinia).
- **`hx-get` / `hx-post` / `hx-put` / `hx-delete` / `hx-patch`**: Primary attributes triggering asynchronous AJAX requests using the respective HTTP verbs.
- **`hx-target`**: CSS selector or keyword (`this`, `closest <sel>`, `find <sel>`, `next`, `previous`) designating where the response HTML will be inserted.
- **`hx-swap`**: Strategy specifying how response content replaces or appends to the target (`innerHTML`, `outerHTML`, `beforebegin`, `afterbegin`, `beforeend`, `afterend`, `delete`, `none`).
- **`hx-trigger`**: Event specification controlling when an HTTP request fires, supporting modifiers like `once`, `changed`, `delay:<time>`, `throttle:<time>`, and `from:<selector>`.
- **`hx-indicator`**: CSS selector pointing to an element (like a spinner) that gains the `htmx-request` class while a network request is in flight.
- **`hx-vals`**: JSON or JavaScript-evaluated values appended to the outgoing request payload.
- **Server-Driven Web App**: An application where the server renders and owns all UI markup and state transitions, and the browser functions as a dumb hypermedia terminal.

## Mental Models
- **HTML as the Complete Hypermedia Engine**: Native HTML restricts links (`<a>`) and forms (`<form>`) to `GET` and `POST`, always refreshing the full window. Think of HTMX as lifting these artificial 1995-era restrictions: now *any* element can make *any* HTTP call and swap *any* slice of the DOM.
- **The Six-Question Declarative Contract**: Whenever authoring or debugging an HTMX tag, mentally step through the Six Questions. If an unexpected behavior occurs, one of the six questions has an incorrect or omitted answer.
- **Server as the Single Source of Truth**: Eliminate state synchronization bugs by refusing to store UI state in the browser. The server renders the state; the browser simply paints the returned fragment.

## Anti-patterns
- **JSON Over-the-Wire for First-Party UI**: Building a JSON API, writing client-side fetch calls, parsing the JSON, and manually mutating DOM nodes when the server already knows how to render HTML templates.
- **Duplicating Validation Logic**: Writing complex client-side regex and rules in JavaScript that duplicate backend model constraints. With HTMX, let the server validate on change and return error partials.
- **Violating Locality of Behavior with Sprawling Event Handlers**: Attaching vanilla `document.querySelector().addEventListener()` listeners across multiple decoupled `.js` files instead of declaring behavior directly on HTML attributes.
- **Forgetting `hx-indicator` on Latent Actions**: Leaving users with zero visual feedback during asynchronous network operations, leading to repeated clicks and double-submissions.

## Code Examples

### Basic CRUD Operations in Declarative HTML
```html
<!-- Create / Submit Form -->
<form hx-post="/contacts/"
      hx-target="#contact-table tbody"
      hx-swap="beforeend"
      hx-indicator="#loading-spinner">
    <input type="text" name="name" placeholder="Full Name" required>
    <input type="email" name="email" placeholder="Email Address" required>
    <button type="submit">Add Contact</button>
</form>

<!-- Read / Search Input with Debounced Trigger -->
<input type="search"
       name="q"
       placeholder="Search contacts..."
       hx-get="/contacts/search/"
       hx-trigger="keyup changed delay:300ms, search"
       hx-target="#contact-table tbody"
       hx-indicator="#search-spinner">

<!-- Delete Action on Table Row -->
<button hx-delete="/contacts/42/"
        hx-target="closest tr"
        hx-swap="outerHTML swap:300ms"
        hx-confirm="Are you sure you want to delete this contact?">
    Delete
</button>

<!-- Shared Loading Indicator -->
<div id="loading-spinner" class="htmx-indicator">
    <img src="/static/img/spinner.svg" alt="Loading..."> Saving...
</div>
```
- **What it demonstrates**: Full CRUD interactions (create, filter/search, delete) declared cleanly in HTML without a single line of imperative JavaScript.

## Reference Tables

### Core Request Attributes & Defaults
| Attribute | Default Trigger Event | Default Target | Default Swap | Purpose |
|:---|:---|:---|:---|:---|
| `hx-get="url"` | Element default (`click` / `change`) | `this` | `innerHTML` | Issues HTTP GET to fetch HTML fragment |
| `hx-post="url"` | `submit` on `<form>`, `click` on others | `this` | `innerHTML` | Issues HTTP POST submitting form or payload |
| `hx-put="url"` | `click` / element default | `this` | `innerHTML` | Issues HTTP PUT for full entity replacement |
| `hx-patch="url"` | `click` / element default | `this` | `innerHTML` | Issues HTTP PATCH for partial entity updates |
| `hx-delete="url"` | `click` / element default | `this` | `innerHTML` | Issues HTTP DELETE to destroy a resource |

### Evaluation Criteria for Server Stacks (Volkmann's HOWL Matrix)
| Dimension | High Rating Requirement | Why It Matters in HTMX |
|:---|:---|:---|
| **Templating Ergonomics** | Fast, partial-friendly template engine | Server renders dozens of sub-template snippets per interaction |
| **Routing Simplicity** | Declarative route definition with URL parameter parsing | Every widget interaction maps to a specific backend route |
| **Live Reload / Dev Speed** | Fast sub-second process restart on file change | Speeds iterative UI testing of server templates |
| **Ecosystem & ORM** | Mature database abstraction with validation rules | Server directly drives form validation and database writes |

## Worked Example

### Complete Server-Driven Item List
Below is a complete hypermedia-driven item management interface demonstrating the Six Questions:

```html
<!-- Container for the Item Management Component -->
<section class="item-manager">
    <h2>Project Task Tracker</h2>

    <!-- Creation Form -->
    <form hx-post="/tasks/"
          hx-target="#task-list"
          hx-swap="afterbegin"
          hx-on::after-request="if(event.detail.successful) this.reset()">
        <input type="text" name="title" placeholder="New task..." required>
        <button type="submit">Create Task</button>
    </form>

    <!-- Task List -->
    <ul id="task-list">
        <!-- Rendered items returned by server -->
        <li id="task-101">
            <span>Audit dependencies</span>
            <button hx-delete="/tasks/101/"
                    hx-target="#task-101"
                    hx-swap="outerHTML"
                    hx-confirm="Remove task?">
                ✕
            </button>
        </li>
        <li id="task-102">
            <span>Configure PostgreSQL pool</span>
            <button hx-delete="/tasks/102/"
                    hx-target="#task-102"
                    hx-swap="outerHTML"
                    hx-confirm="Remove task?">
                ✕
            </button>
        </li>
    </ul>
</section>
```

**Step-by-Step Flow:**
1. User types "Verify migrations" and clicks "Create Task".
2. Form catches `submit`, packages form fields (`title=Verify+migrations`), and issues `POST /tasks/`.
3. Server validates title, creates database record (ID: 103), and renders the snippet:
   `<li id="task-103"><span>Verify migrations</span><button hx-delete="/tasks/103/" ...>✕</button></li>`.
4. HTMX targets `#task-list` and swaps the snippet into `afterbegin` (top of list).
5. `hx-on::after-request` detects success and resets the input field without a page reload.

## Key Takeaways
1. HTMX replaces heavyweight client-side single-page application (SPA) architectures with modern hypermedia driven directly by server templates.
2. Any HTML element can issue any HTTP request method to any URL, targeting any DOM node.
3. Locality of Behavior keeps interaction logic on the relevant markup, making applications easier to read and maintain.
4. The Six Questions framework guarantees clarity when creating or troubleshooting any HTMX interaction.
5. Hypermedia applications eliminate client/server state synchronization bugs by keeping the server as the single source of truth.

## Connects To
- **Ch 02**: Developing Endpoints, Target Selection & Swapping — deep dive into swap styles, out-of-band updates, and response headers.
- **Ch 08**: Django HTMX Foundations — integrating these core attributes with Django views, templates, and CSRF protection.
