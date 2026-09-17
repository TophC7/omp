# Chapter 8: Django HTMX Foundations & Architecture

## Core Idea
Integrating HTMX with Django marries Django's robust server-side architecture—ORM, ModelForms, CSRF middleware, template inheritance, and authentication—with modern client-side responsiveness by splitting views and templates into composable full-page containers and reusable partial snippets.

## Frameworks Introduced
- **The Django Partial Template Hierarchy**:
  - Instead of monolithic templates, organize presentation into two distinct tiers:
    1. *Container Templates* (`templates/promoters.html`): Inherit from `base.html` via `{% extends "base.html" %}`, establish page titles, layouts, navigation, and HTMX mount points.
    2. *Partial Snippets* (`templates/partials/promoters.html`): Contain only the specific HTML fragment being swapped (lists, table rows, form cards), with zero `<html>`, `<head>`, or `{% extends %}` wrappers.
  - *The Dual-Use Invariant*: A partial template can be rendered directly by an HTMX view *and* included inside an initial full-page render using `{% include "partials/my_snippet.html" %}` without code duplication.

- **Dual-Mode Django Views (Full Page vs HTMX Snippet)**:
  - Pattern: A single view function handles both initial direct browser navigation (returning full page) and subsequent HTMX interactions (returning only the partial):
    ```python
    def my_view(request):
        items = Item.objects.all()
        template = "partials/item_list.html" if request.headers.get("HX-Request") == "true" else "items.html"
        return render(request, template, {"items": items})
    ```
  - Eliminates redundant view definitions and URL routes while providing progressive enhancement.

- **Django CSRF Integration Framework**:
  - Django's `CsrfViewMiddleware` rejects any non-GET request that lacks a valid CSRF token.
  - In HTMX, handle CSRF via two reliable patterns:
    1. *Form Embedded*: In full `<form>` submissions, include `{% csrf_token %}` as usual.
    2. *Global HTMX Configuration*: Inject the token globally on the `<body>` element via `hx-headers='{"X-CSRFToken": "{{ csrf_token }}"}'`, or via an `htmx:configRequest` listener that reads Django's `csrftoken` cookie.

- **`django-htmx` Middleware Extension (Ecosystem Standard)**:
  - Adds `request.htmx` object to views with helper booleans (`request.htmx` is truthy if HTMX request, `request.htmx.boosted`, `request.htmx.target`, `request.htmx.trigger`).
  - Provides ergonomic response helpers: `HttpResponseClientRedirect`, `HttpResponseClientRefresh`, `reswap`, `retarget`, and `trigger_client_event`.

## Key Concepts
- **Partial (HTML Snippet)**: Sub-template designed to be rendered standalone in response to an AJAX call or included in a parent template.
- **`HX-Request` Header**: HTTP request header sent automatically by HTMX (`HX-Request: "true"`) allowing Django views to detect HTMX calls.
- **`request.headers.get("HX-Request")`**: Native Django 3.2+ idiom to inspect incoming HTMX headers without third-party dependencies.
- **`X-CSRFToken`**: HTTP header expected by Django's `CsrfViewMiddleware` for AJAX requests.
- **Object Ownership Guarding**: Validating that the logged-in user owns the record being swapped (`get_object_or_404(Room, id=room_id, venue__userprofile=request.user.userprofile)`).
- **`modelform_factory` / `ModelForm`**: Django forms library automatically generating form fields and validation rules directly from ORM models.

## Mental Models
- **The Cookie Cutter and the Pastry**: The container template is the pastry crust (`promoters.html`); the partial template is the fruit filling (`partials/promoters.html`). On initial visit, the baker serves the whole pie; on subsequent updates, the baker simply spoons fresh fruit filling into the existing crust.
- **The Invisible Security Guard**: Django's CSRF middleware watches every non-GET door. Without the `X-CSRFToken` badge pinned to the HTMX jacket, the guard shuts the door with a 403 Forbidden.

## Anti-patterns
- **Putting `{% extends "base.html" %}` in a Partial Template**: Extending the base template inside a partial returned to an `innerHTML` target, which causes an entire nested HTML page with header, navbar, and footer to be injected inside a table or div.
- **Exempting HTMX Views with `@csrf_exempt`**: Disabling CSRF protection to make HTMX requests work, introducing severe security vulnerabilities. Always provide the CSRF token properly.
- **Hardcoding Relative URLs in HTMX Attributes**: Writing `hx-get="partial_promoters/"` instead of using Django's reverse URL resolver `hx-get="{% url 'partial_promoters' %}"` or absolute path `/promoters/partial/`.
- **Forgetting Authorization Checks on Partial Endpoints**: Assuming that because an endpoint only returns a snippet (e.g. `/room/42/edit/`), it doesn't need `@login_required` or object ownership verification, allowing unauthorized data manipulation.

## Code Examples

### 1. Base Template Setup with HTMX & CSRF (`templates/base.html`)
```html
{% load static %}
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>{% block title %}RiffMates{% endblock %}</title>
  <!-- Load HTMX from static or CDN -->
  <script src="https://unpkg.com/htmx.org@1.9.10"
          integrity="sha384-D1Kt99CQMDuVetoL1lrYwg5t+9QdHe7NLX/SoJYkXDFfX37iInKRy5xLSi8nO7UC"
          crossorigin="anonymous"></script>
</head>
<!-- Configure global CSRF token for all child HTMX requests -->
<body hx-headers='{"X-CSRFToken": "{{ csrf_token }}"}'>
  <nav class="navbar">
    <a href="{% url 'home' %}">Home</a>
    <a href="{% url 'promoters' %}">Promoters</a>
    <a href="{% url 'search_musicians' %}">Musicians</a>
  </nav>

  <main class="container">
    {% block content %}{% endblock %}
  </main>
</body>
</html>
```

### 2. Dual-Mode View Pattern (Single View for Page & Partial)
```python
# RiffMates/bands/views.py
from django.shortcuts import render
from bands.models import Musician

def musician_directory(request):
    query = request.GET.get("q", "").strip()
    musicians = Musician.objects.all()
    if query:
        musicians = musicians.filter(first_name__icontains=query)
    
    context = {"musicians": musicians, "query": query}
    
    # If called via HTMX, return only the results snippet
    if request.headers.get("HX-Request") == "true":
        return render(request, "partials/musician_table_body.html", context)
    
    # Otherwise return the complete full-page template
    return render(request, "bands/musicians.html", context)
```

### 3. Container Template Composing Partial (`templates/bands/musicians.html`)
```html
{% extends "base.html" %}

{% block content %}
<h1>Musician Directory</h1>

<input type="search"
       name="q"
       placeholder="Search by first name..."
       hx-get="{% url 'musician_directory' %}"
       hx-trigger="keyup changed delay:300ms, search"
       hx-target="#musician-tbody">

<table>
  <thead>
    <tr><th>First Name</th><th>Last Name</th><th>Instrument</th></tr>
  </thead>
  <tbody id="musician-tbody">
    <!-- Reusable partial included on initial full-page load -->
    {% include "partials/musician_table_body.html" %}
  </tbody>
</table>
{% endblock %}
```

### 4. Standalone Partial Template (`templates/partials/musician_table_body.html`)
```html
<!-- Note: No {% extends %} or <html> wrappers here! -->
{% for musician in musicians %}
  <tr id="musician-{{ musician.id }}">
    <td>{{ musician.first_name }}</td>
    <td>{{ musician.last_name }}</td>
    <td>{{ musician.instrument }}</td>
  </tr>
{% empty %}
  <tr>
    <td colspan="3" class="text-muted">No musicians found matching your query.</td>
  </tr>
{% endfor %}
```

## Reference Tables

### Django Template Directory Organization
| Path | Template Role | Contains `{% extends %}`? | Rendered By |
|:---|:---|:---|:---|
| `templates/base.html` | Root layout, scripts, CSS, nav | N/A (Root) | Base wrapper |
| `templates/bands/promoters.html` | Main page view | **Yes** | Direct browser URL navigation |
| `templates/partials/promoters.html` | Dynamic fragment (list, card) | **No** | HTMX view & `{% include %}` |
| `templates/partials/room_form.html`| Interactive edit form | **No** | HTMX `hx-get` edit action |

### HTMX Request Headers in Django
| Header Name | Django `request.headers` Key | Value / Meaning |
|:---|:---|:---|
| `HX-Request` | `request.headers.get("HX-Request")` | `"true"` if request was initiated by HTMX |
| `HX-Boosted` | `request.headers.get("HX-Boosted")` | `"true"` if request originated from `hx-boost` |
| `HX-Target` | `request.headers.get("HX-Target")` | ID of the target element on the client |
| `HX-Trigger` | `request.headers.get("HX-Trigger")` | ID of the element that triggered the request |
| `HX-Prompt` | `request.headers.get("HX-Prompt")` | Value entered by user in `hx-prompt` dialog |

## Worked Example

### Complete Secure Partial Swapping Architecture (Trudeau's Promoters Feature)
End-to-end integration demonstrating how a slow-loading database listing is cleanly separated into container and partial in Django:

**1. URL Configuration (`promoters/urls.py`):**
```python
from django.urls import path
from promoters import views

urlpatterns = [
    path("", views.promoters, name="promoters"),
    path("partial_promoters/", views.partial_promoters, name="partial_promoters"),
]
```

**2. Views (`promoters/views.py`):**
```python
from time import sleep
from django.shortcuts import render
from promoters.models import Promoter

def promoters(request):
    """Renders the main page immediately with a placeholder."""
    return render(request, "promoters.html")

def partial_promoters(request):
    """Renders only the promoters list snippet after dynamic fetch."""
    # Simulate complex query or remote API latency
    promoters = Promoter.objects.all().order_by("name")
    return render(request, "partials/promoters.html", {"promoters": promoters})
```

**3. Main Container Template (`templates/promoters.html`):**
```html
{% extends "base.html" %}

{% block title %}{{ block.super }}: Promoter Listing{% endblock %}

{% block content %}
<h1>Promoters</h1>

<!-- HTMX dynamically swaps this div upon page load -->
<div hx-get="{% url 'partial_promoters' %}"
     hx-trigger="load"
     hx-swap="outerHTML">
  <p class="loading-placeholder">
    <img src="{% static 'img/spinner.gif' %}" alt="Loading">
    Loading promoters directory...
  </p>
</div>
{% endblock %}
```

**4. Snippet Template (`templates/partials/promoters.html`):**
```html
<ul class="promoter-list">
  {% for promoter in promoters %}
    <li id="promoter-{{ promoter.id }}">
      <strong>{{ promoter.name }}</strong> — {{ promoter.city }}
    </li>
  {% empty %}
    <li>No promoters registered in system.</li>
  {% endfor %}
</ul>
```

## Key Takeaways
1. The Partial Pattern is the cornerstone of Django + HTMX integration: separate full-page shells from reusable HTML snippets.
2. Never include `{% extends %}` in a partial template destined for an HTMX target.
3. Reuse partial snippets inside parent templates using `{% include %}` for initial load, eliminating template duplication.
4. Pass Django CSRF tokens to HTMX globally using `hx-headers='{"X-CSRFToken": "{{ csrf_token }}"}'` on the `<body>` tag.
5. Always apply `@login_required` and object ownership checks to partial endpoints; hypermedia snippets require the exact same authorization rigor as full pages.

## Connects To
- **Ch 01**: HTMX Foundations & Attributes — the core request model applied in Django.
- **Ch 06**: Security & Content Protection — CSRF and escaping in Django templates.
- **Ch 09**: Django HTMX Interactive Patterns — implementing Lazy Loading, Search-as-you-type, Infinite Scroll, and Click-to-Edit.
