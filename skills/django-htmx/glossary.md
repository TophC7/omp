# Glossary of HTMX & Django Hypermedia Terms

**Active Search** — UI pattern where typing into an input immediately filters and updates a target results list using debounced AJAX requests (Ch 03, Ch 09).

**Alpine.js** — Lightweight declarative client-side JavaScript library utilizing custom HTML directives (`x-data`, `x-show`, `x-on`) to manage local transient UI state without build steps (Ch 04).

**`APIKeyHeader`** — Security base class in Django Ninja validating API authentication tokens passed via HTTP request headers (Ch 10).

**Boosting (`hx-boost`)** — Progressive enhancement feature in HTMX converting standard `<a>` links and `<form>` submissions into AJAX requests that swap the `<body>` and update browser history (Ch 01, Ch 03).

**Click-to-Edit** — Hypermedia pattern where a read-only display element is swapped in-place with an editable form upon user action, and swapped back upon saving or canceling (Ch 03, Ch 09).

**Content Security Policy (CSP)** — HTTP header restricting script execution, style sources, and network connection destinations (`connect-src`), vital for securing hypermedia swaps (Ch 06).

**CSRF (Cross-Site Request Forgery)** — Security vulnerability where unauthorized commands are transmitted from a trusted user; mitigated in Django + HTMX via the `X-CSRFToken` header (Ch 06, Ch 08).

**Debounce (`delay:<time>`)** — Trigger modifier that postpones request dispatch until a specified interval of inactivity elapses, preventing request flooding during typing (Ch 03, Ch 09).

**`django-htmx`** — Django package providing middleware that attaches `request.htmx` with helper methods and custom response classes for HTMX-driven views (Ch 08).

**Dual-Mode View** — A Django view function that inspects the `HX-Request` header to conditionally render either a full HTML page or an isolated partial snippet (Ch 08).

**`FilterSchema`** — Declarative Pydantic schema in Django Ninja mapping URL query string parameters directly to QuerySet filters (Ch 10).

**HATEOAS (Hypermedia As The Engine Of Application State)** — Core REST architectural constraint where application state transitions are driven entirely by hypermedia (HTML links and forms) sent by the server (Ch 01).

**HOWL (Hypermedia On Whatever you'd Like)** — Architectural philosophy recognizing that HTMX server backends can be implemented in any language or framework capable of returning HTML (Ch 01).

**`_hyperscript`** — Natural-language client-side scripting language created for hypermedia applications, embedded in HTML via the `_="code"` attribute (Ch 04).

**`hx-confirm`** — HTMX attribute that presents a native browser confirmation prompt before dispatching an HTTP request (Ch 01, Ch 03).

**`hx-disabled-elt`** — HTMX attribute that disables specified form elements or buttons while a request is in flight to prevent duplicate submissions (Ch 01, Ch 03).

**`hx-indicator`** — HTMX attribute designating an element that gains the `.htmx-request` class while a network request is pending (Ch 01).

**`hx-select`** — HTMX attribute that selects a specific slice of the returned HTML response to swap, discarding the remainder (Ch 02).

**`hx-swap`** — Attribute defining the DOM insertion strategy (`innerHTML`, `outerHTML`, `beforebegin`, `afterbegin`, `beforeend`, `afterend`, `delete`, `none`) and timing modifiers (Ch 01, Ch 02).

**`hx-swap-oob` (Out-of-Band Swap)** — Attribute allowing elements in a response to update matching DOM nodes by ID outside the primary `hx-target` (Ch 02, Ch 07).

**`hx-sync`** — Attribute controlling request concurrency on an element (`drop`, `abort`, `replace`, `queue`) to prevent race conditions (Ch 03).

**`hx-target`** — Attribute specifying the destination DOM element for swapped HTML using CSS selectors or traversal keywords (`this`, `closest`, `find`) (Ch 01, Ch 02).

**`hx-trigger`** — Attribute specifying the DOM event that triggers the HTTP request, along with timing and filtering modifiers (Ch 01, Ch 03).

**`HX-Trigger`** — Server response header instructing HTMX to dispatch named client-side events upon receiving a response (Ch 02, Ch 05).

**IDOR (Insecure Direct Object Reference)** — Vulnerability where user-supplied IDs are trusted without ownership checks; mitigated by scoping queries to `request.user` (Ch 08, Ch 09).

**Infinite Scroll** — Pattern where new pages of data are fetched and appended automatically when a sentinel element at the bottom of the list enters the viewport (Ch 03, Ch 09).

**Lazy Loading** — Pattern where resource-intensive or slow UI components are deferred on initial render and fetched via `hx-trigger="load"` or `hx-trigger="revealed"` (Ch 03, Ch 09).

**Locality of Behavior (LoB)** — Design principle stating that the behavior of a code unit should be obvious and directly inspectable on that unit itself (Ch 01, Ch 04).

**`ModelForm`** — Django class automatically generating HTML form fields, validation logic, and database mapping from an ORM model (Ch 08, Ch 09).

**`ModelSchema`** — Bridge class in Django Ninja generating Pydantic request/response schemas directly from Django ORM models (Ch 10).

**`NinjaAPI`** — Central container class in Django Ninja defining API versioning, routing, and Swagger UI documentation endpoints (Ch 10).

**Partial Template** — A reusable sub-template containing only an HTML snippet without `<html>` or `{% extends %}` tags, used for HTMX swaps (Ch 08, Ch 09).

**Polling** — Periodically issuing an HTTP request at fixed intervals (`hx-trigger="every 5s"`) to check for updated server state (Ch 03).

**`revealed`** — HTMX trigger event firing the first time an element scrolls into the visible browser viewport (Ch 03, Ch 09).

**Sentinel Element** — An element placed at the end of a list that triggers the next paginated fetch via `hx-trigger="revealed"` and replaces itself (Ch 03, Ch 09).

**`Router`** — Modular endpoint collector in Django Ninja registered to a parent `NinjaAPI` instance (Ch 10).

**Server-Driven UI** — Architecture where the server controls and renders UI state in HTML fragments, treating the browser as a hypermedia renderer (Ch 01).

**Server-Sent Events (SSE)** — Unidirectional HTTP streaming protocol (`text/event-stream`) allowing servers to push real-time HTML updates to clients (Ch 07).

**Subresource Integrity (SRI)** — Security mechanism verifying that fetched CDN scripts match a predefined cryptographic hash before execution (Ch 06).

**View Transitions API (`transition:true`)** — Modern browser API enabled via HTMX swap modifier to provide smooth animated morphs between swapped states (Ch 02).

**WebSockets** — Full-duplex bidirectional TCP protocol upgraded from HTTP, supported in HTMX via the `ws` extension (Ch 07).

**XSS (Cross-Site Scripting)** — Code injection attack where malicious scripts execute in victim browsers; mitigated by template escaping and CSP (Ch 06).
