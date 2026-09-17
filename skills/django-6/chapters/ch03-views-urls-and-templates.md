# Chapter 3: Django Views, URL Configuration, and Templates

## Core Idea
Django connects HTTP requests to application logic via a flexible URL dispatcher with typed path converters, processes data using Function-Based or Class-Based views, and renders structured responses using the Django Template Language (DTL) and template inheritance.

## Frameworks Introduced
- **The URL Dispatcher & Path Converters**:
  - `path(route, view, name=None)` routes URL patterns to view callables.
  - Dynamic path converters extract typed parameters from URL segments directly into view kwargs:
    - `str`: Matches any non-empty string excluding `/` (default).
    - `int`: Matches zero or any positive integer, converting to Python `int`.
    - `slug`: Matches ASCII letters, numbers, hyphens, and underscores.
    - `uuid`: Matches formatted UUID strings, converting to `uuid.UUID`.
    - `path`: Matches any non-empty string including `/`.
  - Reverse resolution: `reverse("view-name", kwargs={"pk": 1})` in Python and `{% url "view-name" pk=1 %}` in templates eliminate hardcoded URLs.
  - Modular routing: Root `urls.py` delegates app-specific routing via `include("reviews.urls")`.

- **Function-Based Views (FBVs) & Helper Shortcuts**:
  - Standard view signature: `def view_name(request: HttpRequest, **kwargs) -> HttpResponse`.
  - Shortcut `get_object_or_404(Model, **lookup)`: Queries the database using `.get()` and automatically raises `django.http.Http404` if the record does not exist, eliminating verbose `try...except Model.DoesNotExist` blocks.
  - Shortcut `render(request, template_name, context=None, status=200)`: Loads template, merges request context, and returns rendered `HttpResponse`.

- **Django Template Language (DTL) & Inheritance**:
  - Modular layout via the "Skeleton & Muscle" inheritance model:
    - Base skeleton template (`base.html`) defines global HTML structure and placeholder blocks (`{% block title %}`, `{% block content %}`).
    - Child templates declare `{% extends "base.html" %}` and override specific blocks.
  - Variable evaluation: Dot notation (`{{ book.publisher.name }}`) automatically traverses dictionary keys, object attributes, list indices, and callable methods.
  - Control flow: `{% for item in items %}{% empty %}...{% endfor %}`, `{% if cond %}...{% elif %}...{% else %}...{% endif %}`.

## Key Concepts
- **FBV (Function-Based View)**: Explicit Python function receiving `request` and returning `HttpResponse`.
- **CBV (Class-Based View)**: Object-oriented view inheriting generic behaviors from `django.views.generic` (e.g. `TemplateView`, `ListView`).
- **Path Converter**: A regex-backed type parser (`<int:id>`) that matches URL segments and converts them to Python primitives.
- **`reverse()`**: Function resolving an internal view name and arguments into a valid relative URL path string.
- **`include()`**: Function allowing root URL configurations to reference sub-app `urls.py` files.
- **`get_object_or_404`**: Safe object retrieval raising standard 404 Not Found error pages on missing keys.
- **Template Context**: A dictionary mapping variable names to Python objects passed into templates for rendering.
- **Template Filter**: A pipeline modifier applied to variables (e.g., `{{ text|lower }}`) using pipe syntax.

## Mental Models
- **The Tree Branch Router**: Root `urls.py` acts as the trunk, branching via `include()` into modular app routers, which terminate at view leaves.
- **Skeleton and Muscle (Template Inheritance)**: `base.html` is the rigid bone skeleton (header, footer, navigation); child templates supply the muscle (unique page content) by filling in `{% block %}` sockets.
- **Safe Dot Traversal**: In DTL, `object.attribute` silently handles missing attributes (rendering empty string) instead of crashing with `AttributeError` or `KeyError`.

## Anti-patterns
- **Hardcoding URL Strings**: Writing `<a href="/books/12/">` in templates or redirecting to `"/success/"` in views. If routing changes, hardcoded links break silently. Always use `{% url %}` and `reverse()`.
- **Business Logic in Templates**: Attempting complex calculations, data mutations, or filtering inside templates. Move data manipulation into views, model methods, or custom template tags.
- **Verbose Manual 404 Handling**: Writing 6 lines of `try: Model.objects.get() except: raise Http404` in every view instead of using `get_object_or_404()`.
- **Missing App URL Namespacing**: Defining generic names like `name="index"` across multiple apps without `app_name = "reviews"` in `urls.py`, causing URL name collisions.

## Code Examples

### URL Routing with Path Converters & Modular Inclusion

Root URL configuration (`bookr/urls.py`):
```python
# bookr/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("reviews.urls")),
]
```

App-specific URL configuration with namespacing (`reviews/urls.py`):
```python
# reviews/urls.py
from django.urls import path
from . import views

app_name = "reviews"

urlpatterns = [
    path("", views.index, name="index"),
    path("books/", views.book_list, name="book_list"),
    path("books/<int:pk>/", views.book_detail, name="book_detail"),
]
```
- **What it demonstrates**: Delegating app URLs and extracting the primary key via `<int:pk>`.

### Function-Based Views with Shortcuts

```python
# reviews/views.py
from django.shortcuts import render, get_object_or_404
from django.http import HttpRequest, HttpResponse
from .models import Book

def book_list(request: HttpRequest) -> HttpResponse:
    books = Book.objects.select_related("publisher").all()
    return render(request, "reviews/book_list.html", {"books": books})

def book_detail(request: HttpRequest, pk: int) -> HttpResponse:
    book = get_object_or_404(Book, pk=pk)
    reviews = book.review_set.all()
    
    # Calculate average rating if reviews exist
    avg_rating = (
        round(sum(r.rating for r in reviews) / len(reviews)) if reviews else None
    )
    
    context = {
        "book": book,
        "reviews": reviews,
        "avg_rating": avg_rating,
    }
    return render(request, "reviews/book_detail.html", context)
```
- **What it demonstrates**: Clean `get_object_or_404()` retrieval, reverse relational traversal (`book.review_set.all()`), and context passing.

### Template Inheritance (DTL)

Base layout template (`reviews/templates/reviews/base.html`):
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{% block title %}Bookr{% endblock %}</title>
</head>
<body>
    <nav>
        <a href="{% url 'reviews:index' %}">Home</a> |
        <a href="{% url 'reviews:book_list' %}">All Books</a>
    </nav>
    <main>
        {% block content %}{% endblock %}
    </main>
</body>
</html>
```

Child template (`reviews/templates/reviews/book_detail.html`):
```html
{% extends "reviews/base.html" %}

{% block title %}{{ book.title }} - Bookr{% endblock %}

{% block content %}
    <h1>{{ book.title }}</h1>
    <p><strong>Publisher:</strong> {{ book.publisher.name }}</p>
    <p><strong>Published:</strong> {{ book.publication_date|date:"F j, Y" }}</p>
    <p><strong>ISBN:</strong> {{ book.isbn }}</p>

    {% if avg_rating %}
        <p><strong>Average Rating:</strong> {{ avg_rating }} / 5</p>
    {% endif %}

    <h2>Reviews</h2>
    {% for review in reviews %}
        <div class="review">
            <p><strong>Rating:</strong> {{ review.rating }}/5 ({{ review.date_created|timesince }} ago)</p>
            <p>{{ review.content|linebreaks }}</p>
        </div>
    {% empty %}
        <p>No reviews yet for this book.</p>
    {% endfor %}
{% endblock %}
```
- **What it demonstrates**: `{% extends %}`, block overriding, filters (`date`, `timesince`, `linebreaks`), and `{% for %}...{% empty %}` loops.

## Reference Tables

### Built-in Path Converters

| Converter | Regex Pattern | Python Returned Type | Example Match |
|---|---|---|---|
| `str` | `[^/]+` | `str` | `"python-guide"` |
| `int` | `[0-9]+` | `int` | `42` |
| `slug` | `[-a-zA-Z0-9_]+` | `str` | `"django-6-tips"` |
| `uuid` | `[0-9a-f-]{36}` | `uuid.UUID` | `123e4567-e89b-12d3-a456-426614174000` |
| `path` | `.+` | `str` | `"media/2026/05/cover.png"` |

### Essential DTL Tags & Filters

| Syntax | Category | Behavior |
|---|---|---|
| `{% extends "path" %}` | Tag | Declares parent skeleton template (must be first tag) |
| `{% block name %}` | Tag | Defines an overridable section in a layout |
| `{% url 'name' arg %}` | Tag | Resolves reverse URL dynamically |
| `{% for x in list %}` | Tag | Loops over collection; supports `{% empty %}` fallback |
| `{{ val|default:"N/A" }}` | Filter | Replaces falsy values with fallback string |
| `{{ val|date:"Y-m-d" }}` | Filter | Formats dates using PHP/Django date formatting codes |
| `{{ val|linebreaks }}` | Filter | Converts newlines to `<p>` and `<br>` tags |
| `{{ val|truncatewords:20 }}` | Filter | Truncates text after N words, appending ellipsis |

## Worked Example

### Building Book List & Detail Workflow

1. Configure app routes in `reviews/urls.py` with `app_name = "reviews"`.
2. Implement `book_list` view in `reviews/views.py`:
   - Fetch books with `Book.objects.select_related("publisher").all()`.
   - Render `reviews/book_list.html`.
3. In `book_list.html`, link to the detail page:
   `<a href="{% url 'reviews:book_detail' pk=book.pk %}">{{ book.title }}</a>`
4. Implement `book_detail` view:
   - Retrieve book via `get_object_or_404(Book, pk=pk)`.
   - Pass book and related reviews to `reviews/book_detail.html`.
5. Testing:
   - Navigating to `/books/1/` renders book metadata and reviews.
   - Navigating to `/books/99999/` raises an `Http404` exception and displays standard 404 page.

## Key Takeaways
1. Use typed path converters (`<int:pk>`) in URL routes to validate parameters before views execute.
2. Always assign unique `name` attributes to URL patterns and reverse them using `{% url %}` and `reverse()`.
3. Use `include()` and `app_name` to keep app URL routing modular and collision-free.
4. Replace repetitive `try...except DoesNotExist` queries with the `get_object_or_404()` shortcut.
5. Base all HTML pages on a shared `base.html` template using DTL template inheritance (`{% extends %}` and `{% block %}`).

## Connects To
- **Ch 01**: Introduction to Django — where basic views and MVT architecture were introduced.
- **Ch 02**: Models and Migrations — provides the data models queried by views.
- **Ch 04**: An Introduction to Django Admin — the admin counterpart for viewing and editing models.
- **Ch 11**: Advanced Templating and Class-Based Views — extending views with generic CBVs and custom template filters.
