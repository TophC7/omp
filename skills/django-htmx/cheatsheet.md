# HTMX & Django Hypermedia Cheatsheet

## 1. Architectural Decision Rules

- **When designing first-party browser UI**, do **HTMX server-rendered partials**, because it eliminates client state duplication, maintains one source of truth, and leverages Django's native ORM and templates.
- **When building for mobile apps or external integrations**, do **Django Ninja REST APIs (`/api/v1/`)**, because native clients require type-checked JSON payloads and automated OpenAPI documentation.
- **When toggling ephemeral UI state (accordions, modals, local dropdowns)**, do **Alpine.js (`@click="open = !open"`) or _hyperscript**, because transient browser state does not warrant network latency.
- **When an action updates multiple disconnected regions (e.g. cart badge + toast + list)**, do **Out-of-Band Swaps (`hx-swap-oob="true"`) in one response**, because it prevents race conditions and eliminates multiple redundant AJAX round-trips.
- **When implementing live metrics, feeds, or progress bars**, do **Server-Sent Events (`hx-ext="sse"`)**, because SSE runs over standard HTTP, multiplexes over HTTP/2, and provides automatic browser reconnection unlike WebSockets.
- **When an entity is updated or deleted via URL ID (e.g. `/room/42/edit/`)**, do **scope the query to `request.user` (`get_object_or_404(Room, id=id, venue__userprofile=request.user.userprofile)`)**, because untrusted client IDs cause catastrophic IDOR data leaks.
- **When declaring Django Ninja router endpoints**, do **include trailing slashes (`@router.post("/items/")`)**, because Django's `APPEND_SLASH` redirect converts un-slashed POST requests to GET and strips payloads.

---

## 2. Interaction Flowchart

```
Is user interaction intended for first-party browser UI?
 ├── YES ── Does it persist data or require database/auth checks?
 │           ├── YES ── Use HTMX (hx-get, hx-post, hx-put, hx-delete)
 │           │           ├── Multiple regions update? ──> Use Out-of-Band Swaps (hx-swap-oob)
 │           │           ├── Continuous push updates? ──> Use Server-Sent Events (hx-ext="sse")
 │           │           └── Long list?               ──> Use Infinite Scroll (hx-trigger="revealed")
 │           └── NO  ── Local transient toggle only? ──> Use Alpine.js / _hyperscript
 └── NO  ── Programmatic consumer (mobile app, CLI, external partner)?
             └── Use Django Ninja (NinjaAPI + Router + ModelSchema)
```

---

## 3. Swap Strategy Decision Matrix

| Requirement | Strategy (`hx-swap`) | Replaces Target? | Common Pattern |
|:---|:---|:---|:---|
| Update list or panel contents | `innerHTML` *(default)* | No | Search results, tab bodies |
| Transform display row into edit form | `outerHTML` | **Yes** | Click-to-edit, row toggle |
| Prepend newest item to activity feed | `afterbegin` | No | Real-time event log, comments |
| Append item or load next page | `beforeend` | No | Chat log, message append |
| Insert adjacent row or card | `beforebegin` / `afterend` | No | Contextual expansion |
| Remove item on delete | `outerHTML swap:300ms` | **Yes** | Table row animated deletion |
| Execute side-effect or fire header | `none` | No | Background ping, analytics |

---

## 4. Thresholds, Defaults & Guardrails

| Parameter | Recommended Default | Rationale |
|:---|:---|:---|
| **Search Debounce Delay** | `delay:300ms` – `delay:500ms` | Balances responsive feel with database query protection |
| **HTMX Network Timeout** | `htmx.config.timeout = 10000` | Prevents frozen UI on dropped mobile connections |
| **Paginator Page Size** | `per_page = 10` – `per_page = 25` | Prevents oversized DOM nodes during infinite scrolling |
| **CSRF Header** | `hx-headers='{"X-CSRFToken": "{{ csrf_token }}"}'` | Enforces CSRF validation on all child mutations |
| **Security Hardening** | `htmx.config.selfRequestsOnly = true` | Blocks unauthorized requests to external domains |
| **Script Execution** | `htmx.config.allowScriptTags = false` | Disables execution of injected `<script>` tags |
| **Ninja API Docs** | `/api/v1/docs` (OpenAPI Swagger) | Automated schema documentation for external teams |

---

## 5. Tells & Smells (Fast Diagnostic Heuristics)

- **Smell**: Entire webpage flashes and re-renders with header and navbar inside a table row.
  - *Cause*: Partial template includes `{% extends "base.html" %}`. Partial snippets must contain only target markup.
- **Smell**: POST request turns into GET and payload is mysteriously empty.
  - *Cause*: URL in `hx-post` or `@router.post` omitted the trailing slash. Django issued a 301 redirect.
- **Smell**: Form submit fails silently with no visual error on the page.
  - *Cause*: Backend returned HTTP 400/422 and HTMX ignored non-2xx response. Intercept `htmx:beforeSwap` and set `event.detail.shouldSwap = true`.
- **Smell**: Typing in search bar issues 15 queries for a 15-letter word.
  - *Cause*: `hx-trigger="keyup"` used without `changed delay:300ms`.
- **Smell**: Any authenticated user can edit another user's records by guessing the ID.
  - *Cause*: View calls `get_object_or_404(Model, id=id)` without filtering by `userprofile=request.user.userprofile`.
