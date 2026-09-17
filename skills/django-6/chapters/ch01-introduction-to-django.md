# Chapter 1: Introduction to Django

## Core Idea
Django is a high-level, batteries-included Python web framework built around the Model-View-Template (MVT) architecture, designed to take applications from concept to production rapidly by bundling an ORM, URL dispatcher, templating engine, and admin interface.

## Frameworks Introduced
- **The Model-View-Template (MVT) Paradigm**: Django's variation of the classic MVC architectural pattern:
  - *Model*: Defines data structures, relational schemas, and database operations.
  - *View*: Accepts an `HttpRequest`, interacts with models, and returns an `HttpResponse` (equivalent to the Controller in MVC).
  - *Template*: Defines presentation layout and HTML structure using Django Template Language (DTL) (equivalent to the View in MVC).
  - When to use: Across all Django applications to strictly separate data modeling, request orchestration, and presentation markup.
  - How: Define models in `models.py`, view logic in `views.py`, and presentation templates in `<app>/templates/<app>/`.
  - Why it works: Enforces separation of concerns; changes to visual layout do not break backend database contracts or request processing.
  - Failure mode: Writing database queries or business calculations directly inside presentation templates.

- **The HTTP Request-Response Lifecycle**:
  - The web server (WSGI/ASGI) receives an HTTP request and instantiates an `HttpRequest` object.
  - Django passes the request through configured middleware pipelines in `MIDDLEWARE`.
  - The URL dispatcher (`ROOT_URLCONF`) matches the requested path against `urlpatterns` using `path()` or `re_path()`.
  - The matched view function or class receives `request` and keyword arguments parsed from the URL pattern.
  - The view computes logic, optionally queries models, and returns an `HttpResponse` (often rendered via `render(request, template, context)`).
  - Middleware processes the outgoing response before sending it back to the client.

- **QueryDict Parameter Handling**:
  - `request.GET` and `request.POST` are dictionary-like `QueryDict` instances designed to handle multi-valued HTML form parameters.
  - Methods:
    - `request.GET.get(key, default)`: Retrieves the *last* submitted value for a key.
    - `request.GET.getlist(key)`: Retrieves *all* submitted values as a Python list (e.g. multi-select inputs or repeated checkboxes).
  - Note: `QueryDict` instances are immutable by default (`_mutable = False`).

## Key Concepts
- **Batteries-Included Philosophy**: Django provides out-of-the-box solutions for ORM, authentication, admin, forms, sessions, and security without requiring external third-party dependencies.
- **Project vs. App**: A *project* (`django-admin startproject`) is an entire web deployment containing global settings and URLs; an *app* (`manage.py startapp`) is a portable, modular Python package focusing on a specific business domain (e.g., `reviews`).
- **`manage.py`**: A project-local command-line wrapper script for configuring environment settings and orchestrating administrative tasks (`runserver`, `makemigrations`, `migrate`, `shell`).
- **`INSTALLED_APPS`**: A tuple or list in `settings.py` designating all active apps; required for Django to discover templates, static assets, models, and management commands.
- **`HttpRequest`**: The object passed to every view function containing request metadata (headers, method, user, GET/POST QueryDicts, cookies).
- **`HttpResponse`**: The object returned by views containing status codes, headers, and payload content (`str`, `bytes`, or rendered HTML).
- **`render()` Shortcut**: Helper function combining `loader.get_template()`, context processing, and `HttpResponse` instantiation into a single call.

## Mental Models
- **The Restaurant MVT Analogy**:
  - The *Model* is the kitchen pantry and recipes (stores ingredients, defines structure).
  - The *View* is the waiter/order coordinator (takes customer request, consults kitchen, decides what to serve).
  - The *Template* is the plate presentation (formats food visually for customer consumption).
- **The URL Traffic Cop**: The URL router does not handle business logic; it inspects the destination path and directs the traffic directly to the responsible view function.
- **App Isolation**: Treat every Django app as a self-contained component that could theoretically be packaged and reused across multiple Django projects.

## Anti-patterns
- **Template Directory Collisions**: Placing templates directly in `templates/index.html` instead of namespacing them as `templates/<app_name>/index.html`. When two apps have `index.html`, Django's template loader picks the first matching app in `INSTALLED_APPS`.
- **QueryDict Mutation**: Attempting to assign `request.GET['key'] = 'val'`, raising an `AttributeError` because QueryDicts are immutable. Use `request.GET.copy()` if mutation is necessary.
- **Single Giant App**: Stuffing an entire multi-faceted company platform into a single `core` app with 2,000-line `models.py` and `views.py` files.
- **Hardcoding URLs**: Writing `<a href="/reviews/search/">` in templates instead of using the `{% url 'search' %}` tag.

## Code Examples

### Scaffolding and App Registration

Terminal commands:
```bash
# Initialize project and modular app
django-admin startproject bookr
cd bookr
python manage.py startapp reviews
```

Registering app in `settings.py`:
```python
# bookr/settings.py
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Local application
    "reviews.apps.ReviewsConfig",
]
```
- **What it demonstrates**: Registering `ReviewsConfig` ensures Django locates model definitions, migrations, and namespaced templates.

### View and URL Configuration

Defining a view in `reviews/views.py`:
```python
from django.shortcuts import render
from django.http import HttpRequest, HttpResponse

def index(request: HttpRequest) -> HttpResponse:
    context = {"name": "Bookr"}
    return render(request, "reviews/index.html", context)

def search(request: HttpRequest) -> HttpResponse:
    search_term = request.GET.get("search", "").strip()
    return render(request, "reviews/search.html", {"search_term": search_term})
```

Routing in `bookr/urls.py`:
```python
from django.contrib import admin
from django.urls import path
import reviews.views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", reviews.views.index, name="index"),
    path("book-search/", reviews.views.search, name="book_search"),
]
```
- **What it demonstrates**: Binding path patterns to view callables and handling query string parameters via `request.GET`.

## Reference Tables

### Django Project vs. Django App

| Feature | Project (`startproject`) | App (`startapp`) |
|---|---|---|
| **Scope** | Entire website / deployment | Focused functional subdomain |
| **Configuration** | Global `settings.py`, root `urls.py` | Local `apps.py`, local `models.py`, `views.py` |
| **Quantity** | Exactly 1 per repository | Multiple (e.g. `reviews`, `accounts`, `billing`) |
| **Portability** | Deployment-specific | Reusable across projects |
| **Entry Point** | `manage.py`, `wsgi.py`, `asgi.py` | Referenced in `INSTALLED_APPS` |

### QueryDict Common Methods

| Method | Syntax | Behavior |
|---|---|---|
| `get()` | `request.GET.get("k", default)` | Returns last value for key; returns default if missing |
| `getlist()` | `request.GET.getlist("k")` | Returns all values as a Python list `['a', 'b']` |
| `__getitem__` | `request.GET["k"]` | Returns last value; raises `MultiValueDictKeyError` if missing |
| `copy()` | `params = request.GET.copy()` | Returns a mutable duplicate of the QueryDict |
| `items()` | `request.GET.items()` | Iterates over `(key, last_value)` pairs |

## Worked Example

### End-to-End Book Search View with QueryDict Extraction

Creating namespaced template in `reviews/templates/reviews/search.html`:
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Bookr - Search</title>
</head>
<body>
    <h1>Book Search</h1>
    <form method="get" action="{% url 'book_search' %}">
        <input type="text" name="search" value="{{ search_term }}" placeholder="Search by title or author...">
        <button type="submit">Search</button>
    </form>

    {% if search_term %}
        <p>Results for: <strong>{{ search_term }}</strong></p>
    {% else %}
        <p>Please enter a search query above.</p>
    {% endif %}
</body>
</html>
```

View implementation in `reviews/views.py`:
```python
from django.shortcuts import render
from django.http import HttpRequest, HttpResponse

def search(request: HttpRequest) -> HttpResponse:
    search_term = request.GET.get("search", "")
    context = {
        "search_term": search_term,
    }
    return render(request, "reviews/search.html", context)
```

URL configuration in `bookr/urls.py`:
```python
from django.urls import path
from reviews import views

urlpatterns = [
    path("book-search/", views.search, name="book_search"),
]
```

Execution flow:
1. Browser requests `GET /book-search/?search=Python`.
2. Django routes to `views.search`.
3. `request.GET.get("search")` extracts `"Python"`.
4. `render()` evaluates template tags and returns status 200 with rendered HTML.

## Key Takeaways
1. Django follows the Model-View-Template (MVT) pattern, separating data definitions from controllers and presentation.
2. A project houses configuration (`settings.py`, `urls.py`), while apps encapsulate modular domain logic.
3. Every custom app must be declared in `INSTALLED_APPS` to enable template, static file, and model discovery.
4. Always namespace templates inside `<app>/templates/<app>/` to prevent directory resolution conflicts.
5. Use `request.GET.get()` for single parameter extraction and `request.GET.getlist()` for repeated fields; QueryDicts are immutable.

## Connects To
- **Ch 02**: Models and Migrations — defining database schemas for the MVT Model layer.
- **Ch 03**: Django Views, URL Configuration, and Templates — advanced routing, URL parameters, and DTL template inheritance.
- **Ch 06**: Forms — replacing manual QueryDict extraction with validated form classes.
