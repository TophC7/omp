# Concrete Patterns & Techniques

## The Six Questions Checklist
**When to use**: Designing, authoring, or troubleshooting any HTMX element.
**How**:
Explicitly specify or verify the six answers on the markup:
1. *What triggers it?* → `hx-trigger`
2. *What HTTP method?* → `hx-get`, `hx-post`, `hx-put`, `hx-patch`, `hx-delete`
3. *Where is it sent?* → URL attribute value
4. *What data is sent?* → Enclosed inputs, `hx-include`, or `hx-vals`
5. *Where is it placed?* → `hx-target`
6. *How is it swapped?* → `hx-swap`
**Trade-offs**: Requires disciplined attribute naming, but eliminates entire classes of missing-target, duplicate-trigger, or unexpected-swap defects.

---

## Django Partials Dual-Use Pattern
**When to use**: Building views that serve both full-page direct loads and dynamic HTMX updates without duplicating template markup.
**How**:
1. Create a partial snippet in `templates/partials/my_component.html` with no `<html>` or `{% extends %}` tags.
2. In the full-page container template (`my_page.html`), include the snippet on initial render using `{% include "partials/my_component.html" %}`.
3. In the Django view, inspect `request.headers.get("HX-Request") == "true"` (or `request.htmx`). Return the snippet template if True, or the full-page container if False.
**Trade-offs**: Slightly more template files to organize, but guarantees 100% DRY presentation and flawless progressive enhancement.

---

## Active Search-as-You-Type
**When to use**: Table, directory, or catalog filtering where results update instantly as the user types.
**How**:
1. Attach `hx-get="/search/"`, `hx-target="#results-tbody"`, and `hx-indicator="#spinner"` to an `<input type="search">`.
2. Configure trigger: `hx-trigger="keyup changed delay:400ms, search"`.
3. In backend view, filter QuerySet using `icontains` or `Q` objects across relevant fields.
**Trade-offs**: Fast user experience; requires `delay` and `changed` to avoid query flooding on high-traffic databases.

---

## Out-of-Band Multi-Region Updates (OOB)
**When to use**: An interaction updates a primary element (e.g. adding an item to a list) while simultaneously needing to update distant secondary widgets (e.g. cart counter badge, flash message tray, progress bar).
**How**:
1. Server returns the primary target HTML without `hx-swap-oob`.
2. Server includes secondary elements marked with `hx-swap-oob="true"` (matching client elements by ID) or `hx-swap-oob="beforeend:#tray"`.
3. HTMX swaps primary content into `hx-target` and routes OOB elements to their respective DOM IDs automatically.
**Trade-offs**: Consolidates multiple network requests into one round-trip; requires IDs to remain stable across client templates.

---

## Sentinel-Based Infinite Scroll
**When to use**: Long feeds, catalogs, or logs where loading more data on scroll is preferred over pagination links.
**How**:
1. Paginate QuerySets using Django's `Paginator(queryset, per_page)`.
2. Render the current page's items in the partial.
3. If `page.has_next()`, append a sentinel element:
   ```html
   <div hx-get="{% url 'list' %}?page={{ next_page }}"
        hx-trigger="revealed"
        hx-swap="outerHTML">Loading...</div>
   ```
4. When revealed, the sentinel swaps itself with the next page of rows plus the next sentinel.
**Trade-offs**: Eliminates pagination click friction; can make reaching the page footer difficult unless combined with a "Load More" button.

---

## Click-to-Edit State Machine
**When to use**: Editable profiles, table rows, or configuration items where editing should occur in-place without page navigation.
**How**:
1. *Display Partial*: Render data with an "Edit" button (`hx-get="{% url 'edit' item.id %}" hx-target="#item-{{ item.id }}" hx-swap="outerHTML"`).
2. *Edit Partial*: Render a `<form>` pre-populated via Django `ModelForm(instance=item)`. Include "Save" (`hx-post`) and "Cancel" (`hx-get` to display route).
3. *View Handler*: On POST, validate form. If valid, save and return Display Partial; if invalid, re-render Edit Partial with form error messages.
**Trade-offs**: Zero client-side form state management; requires two partial templates and dedicated edit/display view handlers.

---

## Lazy Loading with Placeholder Skeletons
**When to use**: Dashboard widgets, expensive reports, or external API integrations that take >500ms to calculate.
**How**:
1. Render container page immediately with a placeholder skeleton:
   ```html
   <div hx-get="{% url 'slow_widget' %}"
        hx-trigger="load"
        hx-swap="outerHTML">
     <div class="skeleton-shimmer">Loading analytics...</div>
   </div>
   ```
2. Partial view executes heavy query asynchronously after initial page has rendered.
**Trade-offs**: Fast perceived initial page load time; causes layout shifts if placeholder dimensions do not match final rendered widget dimensions.

---

## Global CSRF Header Injection
**When to use**: Ensuring all HTMX AJAX requests pass Django's `CsrfViewMiddleware` without manual token inclusion on every button.
**How**:
Either attach globally to the body:
```html
<body hx-headers='{"X-CSRFToken": "{{ csrf_token }}"}'>
```
Or register a JavaScript event listener:
```javascript
document.body.addEventListener('htmx:configRequest', function(evt) {
    evt.detail.headers['X-CSRFToken'] = getCookie('csrftoken');
});
```
**Trade-offs**: Eliminates repetitive `{% csrf_token %}` boilerplate across partials; requires ensuring token is refreshed if user session rotates.

---

## Error Status Swapping (`htmx:beforeSwap`)
**When to use**: Displaying server-side form validation errors (HTTP 400 or 422) in the targeted DOM container instead of having HTMX treat them as silent failures.
**How**:
Intercept `htmx:beforeSwap` globally in client JavaScript:
```javascript
document.body.addEventListener('htmx:beforeSwap', function(evt) {
    if (evt.detail.xhr.status === 400 || evt.detail.xhr.status === 422) {
        evt.detail.shouldSwap = true;
        evt.detail.isError = false;
    }
});
```
**Trade-offs**: Restores standard HTTP error semantics without breaking HTMX UI swaps; requires consistent backend status code conventions.

---

## Real-Time SSE Stream with Out-of-Band Updates
**When to use**: Live metrics, continuous background job logs, or notification feeds.
**How**:
1. Mount extension and connect:
   ```html
   <div hx-ext="sse" sse-connect="/stream/events/">
     <div sse-swap="job-status">Processing...</div>
   </div>
   ```
2. Server broadcasts `Content-Type: text/event-stream` with named events.
3. Messages can include `hx-swap-oob="true"` to update headers, badges, and counters across the page in real time.
**Trade-offs**: Lightweight, firewall-friendly, and auto-reconnecting compared to WebSockets; unidirectional only (client actions still use standard HTMX HTTP calls).

---

## The Dual-Protocol Split (HTMX + Django Ninja)
**When to use**: Architecting a Django project that requires both first-party interactive browser web pages and programmatic REST endpoints for mobile apps or external integrations.
**How**:
1. Keep domain models, validation, and business logic centralized in Django models/services.
2. Route first-party human browser interactions through Django views returning HTMX partial templates (`HX-Request` detection, session auth, CSRF tokens).
3. Route programmatic API consumers through Django Ninja `NinjaAPI` and `Router` endpoints (`api/v1/`), using Pydantic `ModelSchema`, `FilterSchema`, and `APIKeyHeader`.
**Trade-offs**: Avoids shoehorning JSON into hypermedia or forcing mobile apps to parse HTML; requires maintaining both template partials and Pydantic schemas over the same underlying ORM models.
