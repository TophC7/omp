# Chapter 5: The HTMX JavaScript API & Event Lifecycle

## Core Idea
While HTMX encourages declarative HTML attributes, it exposes a comprehensive JavaScript API and an event-driven lifecycle pipeline that allows developers to programmatically configure defaults, intercept requests, inject security tokens, handle network errors, and trigger imperatively controlled swaps.

## Frameworks Introduced
- **The Request/Swap/Settle Lifecycle Pipeline**:
  - Every HTMX operation traverses a strict, observable multi-stage pipeline:
    1. *Configuration Stage*: `htmx:configRequest` (read/mutate headers, inject parameters).
    2. *Dispatch Stage*: `htmx:beforeRequest` (cancellable via `preventDefault()`) → `htmx:afterRequest`.
    3. *Response Evaluation Stage*: `htmx:beforeSwap` (inspect status code, set `event.detail.shouldSwap = true` for error pages).
    4. *Mutation Stage*: `htmx:afterSwap` (DOM nodes replaced; initialize client widgets here).
    5. *Settlement Stage*: `htmx:beforeSettle` → CSS transitions execute → `htmx:afterSettle`.

- **Error Recovery & Status Interception**:
  - By default, HTMX does *not* swap response bodies for non-2xx status codes (400, 404, 500), treating them as silent errors.
  - Pattern: Intercept `htmx:beforeSwap` to force swapping of validation error bodies (e.g. 422 Unprocessable Entity or 400 Bad Request) so server-rendered form errors appear in the target.

- **Dynamic Element Reprocessing (`htmx.process`)**:
  - Rule: HTMX automatically parses and activates `hx-*` attributes on elements it inserts via its own swaps.
  - Problem: If external JavaScript (e.g. a chart library, modal script, or drag-and-drop widget) inserts raw HTML containing `hx-*` attributes into the DOM, those attributes remain inert.
  - Solution: Invoke `htmx.process(containerElement)` to instruct HTMX to scan, bind listeners, and activate the new subtree.

## Key Concepts
- **`htmx.config`**: Global configuration dictionary governing timeout limits, caching, security gates, and default CSS classes.
- **`htmx.ajax(verb, path, context)`**: Imperative JavaScript function executing a full HTMX-style AJAX request returning a Promise, respecting target, swap, and header rules.
- **`htmx:configRequest`**: Crucial event fired before any request is serialized; the standard integration point for injecting CSRF tokens and auth headers.
- **`htmx:beforeSwap`**: Event allowing fine-grained control over whether a response should mutate the DOM (`event.detail.shouldSwap`).
- **`htmx:afterSwap`**: Lifecycle hook executed immediately after DOM nodes are swapped; primary seam for wiring third-party JS widgets.
- **`htmx.takeClass(element, className)`**: Utility method applying a CSS class to a target element while stripping it from all sibling elements.
- **`htmx.on(element, event, handler)`**: Wrapper over standard `addEventListener` providing consistent cross-browser listener registration.

## Mental Models
- **The Assembly Line Pipeline**: An HTMX request is like a manufacturing conveyor belt. At Station 1 (`configRequest`), inspectors add tracking numbers and security stamps. At Station 2 (`beforeRequest`), the belt checks if the conveyor is clear. At Station 3 (`beforeSwap`), quality control checks the HTTP status tag. At Station 4 (`afterSwap`), technicians paint and polish the newly assembled parts.
- **The Inert Stone vs Living Cell**: HTML strings injected by third-party JavaScript are inert stones. Calling `htmx.process(el)` breathes life into the stones, transforming them into responsive hypermedia nodes.

## Anti-patterns
- **Relying on Global `window.onload` or `DOMContentLoaded` for Widget Setup**: Initializing libraries (like flatpickr, Select2, or Chart.js) only on page load. When HTMX swaps in new content, the newly arrived elements miss initialization. Always bind initialization to `htmx:afterSwap` or `htmx:load`.
- **Silencing 4xx Form Validation Responses**: Returning HTTP 400 or 422 for form validation errors without configuring `htmx:beforeSwap`. HTMX ignores the response, leaving the user with an unresponsive form.
- **Writing Imperative `fetch()` Calls When `htmx.ajax()` Exists**: Bypassing HTMX to write custom `fetch` code, manually parsing HTML, and manually setting `element.innerHTML`, which drops swap transitions and OOB processing.
- **Modifying `htmx.config` After Requests Have Begun**: Mutating configuration keys mid-session instead of setting them once in a `<script>` tag immediately following the HTMX script load.

## Code Examples

### 1. Global CSRF & Header Injection via `htmx:configRequest`
```javascript
// Automatically inject Django or Rails CSRF token into all outgoing HTMX requests
document.body.addEventListener('htmx:configRequest', function(evt) {
    // Read CSRF token from cookie or meta tag
    const csrfToken = getCookie('csrftoken');
    if (csrfToken) {
        evt.detail.headers['X-CSRFToken'] = csrfToken;
    }
    
    // Attach custom client telemetry or request IDs
    evt.detail.headers['X-Client-Timestamp'] = new Date().toISOString();
});
```

### 2. Enabling Swaps on HTTP 422 and 400 Error Responses
```javascript
// Force HTMX to swap error bodies (e.g. Django form validation failures) into the target
document.body.addEventListener('htmx:beforeSwap', function(evt) {
    if (evt.detail.xhr.status === 422 || evt.detail.xhr.status === 400) {
        // Mark as should swap even though HTTP status is non-2xx
        evt.detail.shouldSwap = true;
        // Mark as not an unhandled error so HTMX proceeds with normal swap
        evt.detail.isError = false;
    }
});
```

### 3. Third-Party Library Integration via `htmx:afterSwap`
```javascript
// Initialize a datepicker library on any newly swapped input elements
document.body.addEventListener('htmx:afterSwap', function(evt) {
    // Find all datepicker inputs within the swapped fragment
    const dateInputs = evt.detail.target.querySelectorAll('input.datepicker');
    dateInputs.forEach(input => {
        flatpickr(input, { dateFormat: "Y-m-d" });
    });
});
```

### 4. Imperative HTMX Invocations with `htmx.ajax`
```javascript
// Programmatically trigger a swap from a custom keyboard shortcut
document.addEventListener('keydown', function(evt) {
    if (evt.ctrlKey && evt.key === 'k') {
        evt.preventDefault();
        htmx.ajax('GET', '/search/modal/', {
            target: '#modal-container',
            swap: 'innerHTML'
        }).then(() => {
            console.log('Search modal loaded and mounted.');
        });
    }
});
```

## Reference Tables

### Complete HTMX Event Lifecycle Reference
| Event Name | Cancellable? | Key Detail Properties | Primary Purpose |
|:---|:---|:---|:---|
| `htmx:configRequest` | No | `headers`, `parameters`, `verb`, `path` | Inject auth headers, tokens, query params |
| `htmx:beforeRequest` | **Yes** | `xhr`, `requestConfig` | Last chance to abort request via `preventDefault()` |
| `htmx:afterRequest` | No | `xhr`, `successful`, `failed` | Hide global loading bars, cleanup spinners |
| `htmx:beforeSwap` | No | `xhr`, `shouldSwap`, `target`, `isError` | Override default status code handling (4xx/5xx) |
| `htmx:afterSwap` | No | `target`, `xhr` | Initialize plugins (datepickers, tooltips, charts) |
| `htmx:beforeSettle` | No | `target` | Hook before settle transition begins |
| `htmx:afterSettle` | No | `target` | Post-animation callback |
| `htmx:responseError` | No | `xhr`, `error` | Handle 4xx/5xx errors (toast notifications) |
| `htmx:sendError` | No | `xhr` | Handle offline / network disconnect errors |
| `htmx:timeout` | No | `xhr` | Display timeout retry prompts |

### Critical `htmx.config` Properties
| Property | Default | Production Recommendation | Purpose |
|:---|:---|:---|:---|
| `timeout` | `0` (none) | `10000` (10s) | Prevents requests from hanging indefinitely on dead connections |
| `defaultSwapStyle` | `"innerHTML"` | `"innerHTML"` | Default swap behavior when `hx-swap` is omitted |
| `selfRequestsOnly` | `true` | `true` | Restricts HTMX requests to same-origin URLs (anti-SSRF/XSS) |
| `allowScriptTags` | `true` | `false` (with strict CSP) | Disables execution of `<script>` tags embedded in HTML swaps |
| `allowEval` | `true` | `false` (with strict CSP) | Disables `eval()` evaluation in expressions |
| `refreshOnHistoryMiss`| `false` | `true` | Forces full page reload if history cache lacks target snapshot |

## Worked Example

### Complete Global Network Error Handler & Toast Banner
A resilient client-side error handling architecture capturing dropped connections, 500 errors, and timeouts without crashing the UI:

```html
<!-- Persistent error toast tray in base template -->
<div id="error-toast" class="toast hidden" role="alert">
  <span id="error-toast-message"></span>
  <button type="button" onclick="document.getElementById('error-toast').classList.add('hidden')">✕</button>
</div>

<script>
// Configure HTMX global defaults
htmx.config.timeout = 8000; // 8 second network timeout

// 1. Connection dropped or DNS failure
document.body.addEventListener('htmx:sendError', function(evt) {
    showToast('Network connection lost. Please check your internet connection.');
});

// 2. Network timeout
document.body.addEventListener('htmx:timeout', function(evt) {
    showToast('The server took too long to respond. Please try again.');
});

// 3. Server 500 Internal Errors
document.body.addEventListener('htmx:responseError', function(evt) {
    const status = evt.detail.xhr.status;
    if (status >= 500) {
        showToast('A server error occurred (HTTP ' + status + '). Engineering has been alerted.');
    } else if (status === 403) {
        showToast('You do not have permission to perform this action.');
    }
});

function showToast(msg) {
    const toast = document.getElementById('error-toast');
    const msgEl = document.getElementById('error-toast-message');
    msgEl.textContent = msg;
    toast.classList.remove('hidden');
    setTimeout(() => { toast.classList.add('hidden'); }, 5000);
}
</script>
```

## Key Takeaways
1. `htmx:configRequest` is the primary integration seam for injecting CSRF tokens and authentication credentials into every outgoing request.
2. By default, HTMX ignores non-2xx responses; intercept `htmx:beforeSwap` and set `event.detail.shouldSwap = true` to render 400/422 validation error partials.
3. Use `htmx:afterSwap` to initialize third-party JavaScript libraries (datepickers, charts, rich text editors) on dynamically swapped elements.
4. Calling `htmx.process(element)` activates `hx-*` attributes on DOM nodes added by external client scripts.
5. `htmx.ajax()` provides a type-safe, promise-based bridge to trigger hypermedia requests imperatively from custom JavaScript event handlers.

## Connects To
- **Ch 02**: Endpoints, Targets & Swaps — DOM mutation mechanics underlying the lifecycle.
- **Ch 06**: Security & Content Protection — hardening `htmx.config` and managing CSRF tokens.
- **Ch 08**: Django HTMX Foundations — pairing `htmx:configRequest` with Django's CSRF cookie system.
