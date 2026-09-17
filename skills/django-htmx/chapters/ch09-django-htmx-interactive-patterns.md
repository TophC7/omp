# Chapter 9: Django HTMX Interactive Patterns

## Core Idea
By combining HTMX triggers (`load`, `revealed`, `keyup delay`) with Django's core abstractions (ORM QuerySets, `Paginator`, `ModelForm`, and permission lookups), developers can build responsive, high-performance UI patterns—lazy loading, search-as-you-type, infinite scroll, and inline click-to-edit—using pure Python and Django template syntax.

## Frameworks Introduced
- **The Lazy Loading Component Pattern**:
  - *Problem*: A page contains expensive database queries, external API calls, or heavy aggregations that delay rendering the initial HTML response.
  - *Solution*: Render the container page immediately with a lightweight skeleton placeholder. An HTMX attribute (`hx-trigger="load"`) fires an asynchronous GET request as soon as the DOM renders, fetching and swapping the partial result.
  - *Django Implementation*:
    - Main view: `promoters(request)` renders `promoters.html`.
    - Partial view: `partial_promoters(request)` executes the query and renders `partials/promoters.html`.

- **The Debounced Search-as-you-type Pipeline**:
  - *Pattern*: Real-time database filtering as the user types without full page reload.
  - *Trigger Specification*: `hx-trigger="keyup changed delay:500ms, search"` prevents flooding the database by debouncing keystrokes.
  - *Django ORM Integration*: Views parse `request.GET.get("search_text", "")` and execute case-insensitive lookups across multiple fields using `Q` objects:
    ```python
    musicians = Musician.objects.filter(
        Q(first_name__icontains=search_text) | Q(last_name__icontains=search_text)
    )
    ```

- **The Sentinel-Based Infinite Scroll Pattern**:
  - *Mechanism*: At the bottom of a paginated list partial, insert a sentinel element containing `hx-trigger="revealed"`.
  - *Execution*:
    1. Browser viewport scrolls down to the sentinel element.
    2. `revealed` event fires, requesting the next page: `hx-get="{% url 'search_musicians' %}?page={{ next_page }}&search_text={{ search_text }}"`.
    3. `hx-swap="outerHTML"` replaces the sentinel element itself with the next page of rows plus a new sentinel element.
    4. When `has_more` is `False`, the view omits the sentinel, gracefully terminating the infinite stream.

- **The Click-to-Edit ModelForm State Machine**:
  - Replaces complex JavaScript modal or inline-editor frameworks with two coordinated Django partial templates:
    1. *Read/Display Partial (`partials/show_room.html`)*: Displays model values with an "Edit" anchor (`hx-get="{% url 'edit_room_form' room.id %}" hx-target="#room-row-{{ room.id }}"`).
    2. *Edit Form Partial (`partials/edit_room_form.html`)*: Renders a Django `ModelForm` with Save (`hx-post`) and Cancel (`hx-get`) buttons, both targeting `#room-row-{{ room.id }}`.
  - *Self-Healing Validation*: If the user submits invalid data, the view returns the edit partial with form error annotations; on success, it returns the updated read partial.

- **The Object-Level Ownership Guard**:
  - Because HTMX actions frequently take entity IDs directly from URLs (e.g. `/rooms/42/edit/`), secure endpoints against Insecure Direct Object Reference (IDOR) attacks.
  - Guard Pattern: Filter queries through the authenticated user's profile:
    ```python
    room = get_object_or_404(Room, id=room_id, venue__userprofile=request.user.userprofile)
    ```

## Key Concepts
- **`hx-trigger="load"`**: Triggers an HTTP request as soon as the element is mounted into the DOM.
- **`hx-trigger="revealed"`**: Triggers an HTTP request when the element scrolls into the visible browser viewport.
- **Django `Paginator`**: Django core pagination utility slicing QuerySets into manageable chunks.
- **`page.has_next()`**: Boolean method indicating if subsequent pages exist.
- **`modelform_factory`**: Utility function creating a Django `ModelForm` class dynamically from a model and field list.
- **`request.htmx`**: Middleware boolean indicating whether the incoming request was made by HTMX.
- **IDOR (Insecure Direct Object Reference)**: Vulnerability where an attacker modifies URL IDs to edit records belonging to other users.

## Mental Models
- **The Self-Propelling Conveyor Belt (Infinite Scroll)**: The sentinel `div` at the bottom of the list is a tripwire. As the user walks down the conveyor belt, they trip the wire; the server unrolls another 20 feet of conveyor belt and plants a fresh tripwire at the new end.
- **The In-Place Transformer (Click-to-Edit)**: A table row transforms into a form when clicked, and solidifies back into text when saved. No modal popups, no page redirects.

## Anti-patterns
- **Unprotected Entity IDs in HTMX URLs**: Calling `get_object_or_404(Room, id=room_id)` without checking `venue__userprofile=request.user.userprofile`, allowing any logged-in user to edit any room in the database.
- **Omitting `changed` on Search Inputs**: Using `hx-trigger="keyup delay:500ms"` without `changed`, causing queries to re-execute when users press arrow keys or shift.
- **Redirecting on Form Validation Errors**: Returning an HTTP 302 redirect after form validation failure instead of rendering the partial with `form.errors`, wiping out the user's input.
- **Missing Loading Indicators on Lazy Components**: Leaving lazy containers completely empty without a spinner or skeleton, making the page appear broken while data loads.

## Code Examples

### 1. Lazy Loading Slow Views (Trudeau Listings 12.1 – 12.4)
```python
# RiffMates/promoters/views.py
from time import sleep
from django.shortcuts import render
from promoters.models import Promoter

def promoters(request):
    """Main page container view."""
    return render(request, "promoters.html")

def partial_promoters(request):
    """Dynamically loaded partial view."""
    # sleep(2)  # Simulates network or heavy calculation latency
    promoters = Promoter.objects.all().order_by("name")
    return render(request, "partials/promoters.html", {"promoters": promoters})
```

```html
<!-- RiffMates/templates/promoters.html -->
{% extends "base.html" %}
{% block content %}
<h1>Promoters</h1>
<div hx-get="{% url 'partial_promoters' %}"
     hx-trigger="load"
     hx-swap="outerHTML">
  <p><i>Loading promoters list...</i></p>
</div>
{% endblock %}
```

```html
<!-- RiffMates/templates/partials/promoters.html -->
<ul class="promoter-list">
  {% for promoter in promoters %}
    <li>{{ promoter.name }} ({{ promoter.city }})</li>
  {% empty %}
    <li>No promoters registered.</li>
  {% endfor %}
</ul>
```

### 2. Search-as-You-Type with Infinite Scroll (Trudeau Listings 12.10 – 12.11)
```python
# RiffMates/bands/views.py
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render
from bands.models import Musician

def search_musicians(request):
    search_text = request.GET.get("search_text", "").strip()
    page_num = int(request.GET.get("page", 1))
    
    musicians = Musician.objects.all().order_by("last_name", "first_name")
    if search_text:
        musicians = musicians.filter(
            Q(first_name__icontains=search_text) | Q(last_name__icontains=search_text)
        )
    
    paginator = Paginator(musicians, per_page=10)
    page = paginator.get_page(page_num)
    
    context = {
        "search_text": search_text,
        "musicians": page.object_list,
        "has_more": page.has_next(),
        "next_page": page_num + 1,
    }
    
    # If called via HTMX, return the inner partial
    if request.headers.get("HX-Request") == "true":
        return render(request, "partials/musician_results.html", context)
    
    return render(request, "search_musicians.html", context)
```

```html
<!-- RiffMates/templates/search_musicians.html -->
{% extends "base.html" %}
{% block content %}
<h1>Search Musicians</h1>

<input type="search"
       name="search_text"
       placeholder="Search by name..."
       hx-get="{% url 'search_musicians' %}"
       hx-trigger="keyup changed delay:400ms, search"
       hx-target="#musician-results"
       autocomplete="off">

<ul id="musician-results">
  {% include "partials/musician_results.html" %}
</ul>
{% endblock %}
```

```html
<!-- RiffMates/templates/partials/musician_results.html -->
{% for musician in musicians %}
  <li>{{ musician.last_name }}, {{ musician.first_name }}</li>
{% empty %}
  {% if not has_more %}
    <li><i>No musicians found</i></li>
  {% endif %}
{% endfor %}

{% if has_more %}
  <!-- Sentinel element: triggers fetch when scrolled into view -->
  <li hx-get="{% url 'search_musicians' %}?page={{ next_page }}&search_text={{ search_text }}"
      hx-trigger="revealed"
      hx-swap="outerHTML">
    <i>Loading more musicians...</i>
  </li>
{% endif %}
```

### 3. Click-to-Edit with ModelForm (Trudeau Listings 12.12 – 12.18)
```python
# RiffMates/bands/forms.py
from django import forms
from bands.models import Room

RoomForm = forms.modelform_factory(Room, fields=["name"])
```

```python
# RiffMates/bands/views.py
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from bands.models import Venue, Room
from bands.forms import RoomForm

@login_required
def room_editor(request, venue_id):
    """Main room editor page for a venue."""
    venue = get_object_or_404(Venue, id=venue_id, userprofile=request.user.userprofile)
    return render(request, "room_editor.html", {"venue": venue})

@login_required
def edit_room_form(request, room_id):
    """Handles both rendering the edit form (GET) and saving changes (POST)."""
    room = get_object_or_404(Room, id=room_id, venue__userprofile=request.user.userprofile)
    
    if request.method == "POST":
        form = RoomForm(request.POST, instance=room)
        if form.is_valid():
            form.save()
            # On successful save, return the read-only display partial
            return render(request, "partials/show_room.html", {"room": room})
        # If invalid, re-render form partial with validation errors
        return render(request, "partials/edit_room_form.html", {"room": room, "form": form})
    
    # GET: return form pre-populated with current room data
    form = RoomForm(instance=room)
    return render(request, "partials/edit_room_form.html", {"room": room, "form": form})

@login_required
def show_room_partial(request, room_id):
    """Returns read-only partial when canceling edit."""
    room = get_object_or_404(Room, id=room_id, venue__userprofile=request.user.userprofile)
    return render(request, "partials/show_room.html", {"room": room})
```

```html
<!-- RiffMates/templates/partials/show_room.html -->
<li id="room-row-{{ room.id }}">
  <strong>{{ room.name }}</strong>
  <a hx-get="{% url 'edit_room_form' room.id %}"
     hx-target="#room-row-{{ room.id }}"
     hx-swap="outerHTML"
     style="cursor: pointer; text-decoration: underline; margin-left: 10px;">
    (Edit)
  </a>
</li>
```

```html
<!-- RiffMates/templates/partials/edit_room_form.html -->
<li id="room-row-{{ room.id }}">
  <form hx-post="{% url 'edit_room_form' room.id %}"
        hx-target="#room-row-{{ room.id }}"
        hx-swap="outerHTML">
    {% csrf_token %}
    {{ form.as_p }}
    <button type="submit">Save</button>
    <button type="button"
            hx-get="{% url 'show_room_partial' room.id %}"
            hx-target="#room-row-{{ room.id }}"
            hx-swap="outerHTML">
      Cancel
    </button>
  </form>
</li>
```

## Reference Tables

### Django HTMX Interactive Patterns Matrix
| Pattern | Trigger | HTMX Attributes | Key Django Component |
|:---|:---|:---|:---|
| **Lazy Loading** | `load` | `hx-get="{% url '...' %}" hx-swap="outerHTML"` | Lightweight shell + partial view |
| **Search Filter** | `keyup changed delay:400ms` | `hx-get="{% url '...' %}" hx-target="#results"` | `Q(field__icontains=...)` |
| **Infinite Scroll** | `revealed` | `hx-get="?page={{ next }}" hx-swap="outerHTML"` | Django `Paginator` + `has_next()` |
| **Click-to-Edit** | `click` (GET) / `submit` (POST) | `hx-target="#row-{{ id }}" hx-swap="outerHTML"`| `ModelForm(instance=...)` |
| **Cancel Edit** | `click` | `hx-get="{% url '...' %}" hx-swap="outerHTML"` | Standalone display partial view |

## Worked Example

### Complete Venue & Room Management Interface
Walking through a user editing a venue room:
1. User navigates to `/venues/5/rooms/`. `room_editor()` verifies venue ownership and renders `room_editor.html` containing a list of rooms using `{% include "partials/show_room.html" %}`.
2. User clicks `(Edit)` next to "Main Stage". HTMX issues `GET /rooms/12/edit/`.
3. `edit_room_form()` view loads `Room` 12, instantiates `form = RoomForm(instance=room)`, and renders `partials/edit_room_form.html`.
4. HTMX replaces `<li id="room-row-12">` with the form markup containing an input with value "Main Stage".
5. User changes name to "Acoustic Lounge" and clicks Save. Form issues `POST /rooms/12/edit/` with CSRF token.
6. Server validates `form.is_valid()`. It saves the model to SQLite/PostgreSQL and returns `partials/show_room.html`.
7. HTMX swaps `<li id="room-row-12">` back into a read-only list item showing "Acoustic Lounge" and the `(Edit)` button. No page reloads occurred; full validation and security checks were enforced by Django.

## Key Takeaways
1. Lazy loading using `hx-trigger="load"` prevents complex or slow queries from blocking initial page loads.
2. Search-as-you-type combines `keyup`, `changed`, and `delay:400ms` with Django ORM `Q` queries for efficient live filtering.
3. Infinite scroll is implemented with a sentinel element bearing `hx-trigger="revealed"` that replaces itself with the next page of results.
4. Click-to-edit uses Django `ModelForm` to transition seamlessly between display and edit states on the exact same DOM node.
5. Hypermedia endpoints must strictly enforce object ownership using queries like `get_object_or_404(Model, id=id, owner=request.user)` to prevent IDOR vulnerabilities.

## Connects To
- **Ch 01**: HTMX Foundations & Attributes — the core request/response model.
- **Ch 03**: Common UI Recipes & Patterns — generalized browser patterns.
- **Ch 08**: Django HTMX Foundations & Architecture — the underlying template and CSRF structure.
