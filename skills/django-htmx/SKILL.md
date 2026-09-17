---
name: django-htmx
description: "Knowledge base from \"Server-Driven Web Apps with htmx\" by R. Mark Volkmann and \"Django in Action\" (Chapters 11 & 12) by Christopher Trudeau. Use when applying HTMX hypermedia architectures, building interactive server-driven web apps in Python and Django, implementing partials, click-to-edit, infinite scroll, active search, Django Ninja REST APIs, or referencing HTMX attributes and patterns."
---

<!-- argument-hint: [topic, framework name, or chapter number] -->

# Django & HTMX: Server-Driven Web Applications
**Authors**: R. Mark Volkmann & Christopher Trudeau | **Chapters**: 10 | **Generated**: 2026-09-06

## How to Use This Skill

- **Without arguments** — loads the core hypermedia frameworks, Django integration rules, and architectural guidelines below.
- **With a topic** — ask about `infinite-scroll`, `click-to-edit`, `oob-swaps`, `csrf`, or `django-ninja`; I load and apply the corresponding chapter.
- **With a chapter** — ask for `ch01` through `ch10` to inspect detailed source code, reference tables, and worked examples.
- **Browse** — ask for the chapter index or cheatsheet decision rules.

When you ask about a topic not fully covered in Core Frameworks below, I will read the relevant chapter file before answering.

---

## Core Frameworks & Mental Models

### 1. The Six Questions Framework for HTMX
Every HTMX interaction answers six concrete questions declared directly on HTML markup:
1. *What causes the request?* → `hx-trigger` (`click`, `submit`, `change`, `load`, `revealed`, with modifiers like `delay:300ms`, `changed`, `once`).
2. *What HTTP method is used?* → `hx-get`, `hx-post`, `hx-put`, `hx-patch`, or `hx-delete`.
3. *Where is the request sent?* → The URL attribute value (e.g. `hx-get="{% url 'search' %}"`).
4. *What data is sent?* → Enclosed form inputs, extended via `hx-include` or `hx-vals`.
5. *Where should the response be placed?* → `hx-target` (`this`, `closest tr`, `find .status`, or CSS selector).
6. *How should the response replace target content?* → `hx-swap` (`innerHTML`, `outerHTML`, `beforebegin`, `afterbegin`, `beforeend`, `afterend`, `delete`, `none`).

### 2. Locality of Behavior (LoB)
The behavior of a unit of code should be discoverable and understandable directly by inspecting that unit, rather than spread across external JavaScript files, decoupled event listeners, and selector bindings. Declare triggers, targets, swaps, and indicators right on the HTML tag.

### 3. The Django Partial Template Pattern
Decouple templates into two composable tiers:
- *Container Templates* (`templates/promoters.html`): Inherit from `base.html` via `{% extends %}`, establishing layouts, navigation, and HTMX mount points.
- *Partial Snippets* (`templates/partials/promoters.html`): Contain only the specific HTML fragment being swapped (lists, rows, form cards), with zero `<html>` or `{% extends %}` tags.
- *The Dual-Use Invariant*: Include snippets inside initial full-page renders via `{% include "partials/snippet.html" %}`, and render them directly from views when `request.headers.get("HX-Request") == "true"`.

### 4. Out-of-Band (OOB) Swaps (`hx-swap-oob`)
When an action updates a primary element (e.g. adding an item to a list) and also requires updating distant secondary widgets (e.g. cart badge counter, notification tray, summary stats), return the primary HTML alongside elements tagged with `hx-swap-oob="true"`. HTMX routes each OOB element to its matching DOM ID automatically in a single round-trip.

### 5. Flagship Interactive Patterns in Django
- **Lazy Loading**: Render the container page immediately with a lightweight skeleton placeholder. Attach `hx-get="{% url 'slow_view' %}" hx-trigger="load" hx-swap="outerHTML"` to load and swap heavy data asynchronously.
- **Search-as-you-type**: Attach `hx-trigger="keyup changed delay:400ms, search"` to an input targeting a results container. Backend views filter QuerySets using ORM `icontains` or `Q` objects.
- **Sentinel Infinite Scroll**: Place a sentinel element at the bottom of a list partial with `hx-trigger="revealed"`. When scrolled into view, it fetches the next page using Django's `Paginator` and replaces itself (`outerHTML`) with the new items and the next sentinel.
- **Click-to-Edit State Machine**: Toggle between a read-only display partial (`partials/show_room.html`) and an edit form partial (`partials/edit_room_form.html`) using Django `ModelForm`. On validation error, return the form with errors; on success, return the display partial.

### 6. The Dual-Protocol Split (HTMX + Django Ninja)
- **HTMX (HTML over the wire)**: Drives first-party human browser interactions using Django templates, sessions, and CSRF protection.
- **Django Ninja (JSON over the wire)**: Drives programmatic consumers (mobile apps, webhooks, external partners) using `NinjaAPI`, `Router`, and Pydantic `ModelSchema`/`FilterSchema` mounted at `/api/v1/`.
- Both layers share the exact same underlying Django ORM models and business logic.

### 7. Hypermedia Security Invariants
- **Object Ownership Guarding**: Always scope entity lookups to the authenticated user (`get_object_or_404(Model, id=id, owner=request.user)`) to prevent IDOR attacks.
- **CSRF Token Injection**: Attach `hx-headers='{"X-CSRFToken": "{{ csrf_token }}"}'` globally to the `<body>` element.
- **Runtime Hardening**: Configure `htmx.config.selfRequestsOnly = true` and `htmx.config.allowScriptTags = false` immediately after loading HTMX.
- **Context-Aware Escaping**: Never use `|safe` on unescaped user inputs; sanitize rich HTML on the server with allowlist parsers (`nh3`).

---

## Chapter Index

| # | Title | Core Focus & Key Frameworks |
|:---|:---|:---|
| [ch01](chapters/ch01-htmx-foundations-and-attributes.md) | HTMX Foundations & Core Attributes | HOWL, Six Questions Framework, Locality of Behavior, CRUD flow |
| [ch02](chapters/ch02-endpoints-targets-and-swaps.md) | Endpoints, Targets & Swaps | Target selectors (`this`, `closest`, `find`), 8 swap styles, OOB swaps, `HX-*` headers |
| [ch03](chapters/ch03-common-ui-recipes-and-patterns.md) | Common UI Recipes & Patterns | Boosting (`hx-boost`), active search, debouncing, modals, transitions, `hx-sync` |
| [ch04](chapters/ch04-client-side-interactivity-alpine-and-hyperscript.md) | Client Interactivity: Alpine & _hyperscript | Ephemeral UI state, Alpine directives (`x-data`, `x-show`), _hyperscript natural syntax |
| [ch05](chapters/ch05-htmx-javascript-api-and-lifecycle.md) | HTMX JavaScript API & Event Lifecycle | Lifecycle pipeline, `htmx:configRequest`, `htmx:beforeSwap`, `htmx.process`, `htmx.ajax` |
| [ch06](chapters/ch06-security-csp-and-content-protection.md) | Security, CSP & Content Protection | XSS mitigation, Content Security Policy, SRI, cookie flags, runtime hardening |
| [ch07](chapters/ch07-real-time-streaming-websockets-and-sse.md) | Real-Time Streaming: WebSockets & SSE | Push hypermedia, Server-Sent Events (`hx-ext="sse"`), WebSockets (`ws`), OOB over stream |
| [ch08](chapters/ch08-django-htmx-foundations-and-architecture.md) | Django HTMX Foundations & Architecture | Partial template hierarchy, dual-mode views, CSRF integration, `django-htmx` middleware |
| [ch09](chapters/ch09-django-htmx-interactive-patterns.md) | Django HTMX Interactive Patterns | Lazy loading, search-as-you-type, infinite scroll, click-to-edit with ModelForms, IDOR |
| [ch10](chapters/ch10-django-ninja-rest-apis.md) | Building Modern REST APIs with Django Ninja | `NinjaAPI`, `Router`, `ModelSchema`, `FilterSchema`, APIKeyHeader, OpenAPI Swagger docs |

---

## Topic Index

- **Active Search** → [ch03](chapters/ch03-common-ui-recipes-and-patterns.md), [ch09](chapters/ch09-django-htmx-interactive-patterns.md)
- **Alpine.js Integration** → [ch04](chapters/ch04-client-side-interactivity-alpine-and-hyperscript.md)
- **API Key Security** → [ch10](chapters/ch10-django-ninja-rest-apis.md)
- **Boosting (`hx-boost`)** → [ch01](chapters/ch01-htmx-foundations-and-attributes.md), [ch03](chapters/ch03-common-ui-recipes-and-patterns.md)
- **Click-to-Edit** → [ch03](chapters/ch03-common-ui-recipes-and-patterns.md), [ch09](chapters/ch09-django-htmx-interactive-patterns.md)
- **Content Security Policy (CSP)** → [ch06](chapters/ch06-security-csp-and-content-protection.md)
- **CSRF Token Handling** → [ch06](chapters/ch06-security-csp-and-content-protection.md), [ch08](chapters/ch08-django-htmx-foundations-and-architecture.md)
- **Django Ninja REST APIs** → [ch10](chapters/ch10-django-ninja-rest-apis.md)
- **Dual-Mode Django Views** → [ch08](chapters/ch08-django-htmx-foundations-and-architecture.md)
- **Error Handling (`htmx:beforeSwap`)** → [ch05](chapters/ch05-htmx-javascript-api-and-lifecycle.md)
- **FilterSchema** → [ch10](chapters/ch10-django-ninja-rest-apis.md)
- **HATEOAS & HOWL** → [ch01](chapters/ch01-htmx-foundations-and-attributes.md)
- **_hyperscript** → [ch04](chapters/ch04-client-side-interactivity-alpine-and-hyperscript.md)
- **IDOR Object Ownership** → [ch08](chapters/ch08-django-htmx-foundations-and-architecture.md), [ch09](chapters/ch09-django-htmx-interactive-patterns.md)
- **Infinite Scroll** → [ch03](chapters/ch03-common-ui-recipes-and-patterns.md), [ch09](chapters/ch09-django-htmx-interactive-patterns.md)
- **JavaScript API (`htmx.ajax`, `htmx.process`)** → [ch05](chapters/ch05-htmx-javascript-api-and-lifecycle.md)
- **Lazy Loading** → [ch03](chapters/ch03-common-ui-recipes-and-patterns.md), [ch09](chapters/ch09-django-htmx-interactive-patterns.md)
- **Locality of Behavior (LoB)** → [ch01](chapters/ch01-htmx-foundations-and-attributes.md), [ch04](chapters/ch04-client-side-interactivity-alpine-and-hyperscript.md)
- **ModelForm in HTMX** → [ch08](chapters/ch08-django-htmx-foundations-and-architecture.md), [ch09](chapters/ch09-django-htmx-interactive-patterns.md)
- **ModelSchema** → [ch10](chapters/ch10-django-ninja-rest-apis.md)
- **Out-of-Band Swaps (`hx-swap-oob`)** → [ch02](chapters/ch02-endpoints-targets-and-swaps.md), [ch07](chapters/ch07-real-time-streaming-websockets-and-sse.md)
- **Partials Hierarchy** → [ch08](chapters/ch08-django-htmx-foundations-and-architecture.md)
- **Paginator (Django)** → [ch09](chapters/ch09-django-htmx-interactive-patterns.md)
- **Polling (`every <time>`)** → [ch03](chapters/ch03-common-ui-recipes-and-patterns.md)
- **Response Headers (`HX-*`)** → [ch02](chapters/ch02-endpoints-targets-and-swaps.md), [ch08](chapters/ch08-django-htmx-foundations-and-architecture.md)
- **Router (Django Ninja)** → [ch10](chapters/ch10-django-ninja-rest-apis.md)
- **Server-Sent Events (SSE)** → [ch07](chapters/ch07-real-time-streaming-websockets-and-sse.md)
- **Swap Modifiers (`transition`, `swap:ms`)** → [ch02](chapters/ch02-endpoints-targets-and-swaps.md)
- **Target Traversal (`this`, `closest`, `find`)** → [ch02](chapters/ch02-endpoints-targets-and-swaps.md)
- **WebSockets** → [ch07](chapters/ch07-real-time-streaming-websockets-and-sse.md)
- **XSS Prevention** → [ch06](chapters/ch06-security-csp-and-content-protection.md)

---

## Supporting Files

- [glossary.md](glossary.md) — complete alphabetized definitions of all HTMX and Django hypermedia terms.
- [patterns.md](patterns.md) — concrete architectural design patterns, when to use, how to implement, and trade-offs.
- [cheatsheet.md](cheatsheet.md) — decision rules, flowchart, swap matrix, thresholds, and diagnostic code smells.

---

## Scope & Limits

This skill covers the complete hypermedia concepts and patterns from *Server-Driven Web Apps with htmx* by R. Mark Volkmann and *Django in Action* (Chapters 11 & 12) by Christopher Trudeau. For general Django ORM models, migrations, authentication setup, and deployment configurations, refer to the `django-6` skill.
