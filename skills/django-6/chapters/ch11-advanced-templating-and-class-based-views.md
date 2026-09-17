# Chapter 11: Advanced Templating and Class-Based Views

## Core Idea
Class-Based Views (CBVs) organize request-handling logic into reusable, object-oriented class hierarchies with explicit HTTP-verb dispatching, while custom template tags, filters, and inclusion partials eliminate template duplication and encapsulate reusable UI components.

## Frameworks Introduced
- **The Generic Class-Based View (GCBV) Hierarchy**:
  - Encapsulates common web patterns (rendering templates, listing querysets, displaying single objects, editing forms) in pre-built subclasses of `django.views.generic`:
    - `TemplateView`: Renders static/informational pages; override `get_context_data(**kwargs)`.
    - `ListView`: Queries a model collection, automatically handles pagination (`paginate_by = 10`), and injects `page_obj` and `object_list` into template context. Override `get_queryset()` for dynamic filtering.
    - `DetailView`: Resolves a single model instance using primary key (`<int:pk>`) or slug (`<slug:slug>`) and injects `object` into context.
    - `CreateView` / `UpdateView`: Binds a `ModelForm`, handles GET rendering and POST validation, and redirects to `success_url` upon successful `.save()`.
    - `DeleteView`: Confirms and executes model deletion on POST.

- **View Mixins & Method Resolution Order (MRO)**:
  - Mixins provide pluggable behaviors (authentication, permissions, form prefixes) through multiple inheritance.
  - *MRO Invariant*: Mixins must always precede the generic base class in class declaration:
    `class BookCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):`
  - Python resolves left-to-right; placing `CreateView` before `LoginRequiredMixin` prevents the mixin's `dispatch()` method from intercepting unauthenticated requests.

- **Custom Template Filters Framework**:
  - Pure Python functions that transform a variable value inside template evaluation pipelines.
  - Requirements:
    1. Located inside `<app>/templatetags/<module_name>.py` (alongside an empty `__init__.py`).
    2. Instantiate `register = template.Library()`.
    3. Decorate with `@register.filter(name="custom_name")`.
    4. Loaded in templates via `{% load module_name %}`.
  - Signature: `def filter_func(value, arg=None) -> Any`.

- **Custom Simple Tags & Inclusion Tags**:
  - *Simple Tags (`@register.simple_tag`)*: Takes arbitrary positional/keyword arguments and returns a raw string or HTML safe string.
  - *Inclusion Tags (`@register.inclusion_tag("partial.html")`)*: Encapsulates reusable visual components (user badges, star ratings, book cards). Computes data and returns a context dictionary used to render the specified partial template.

## Key Concepts
- **Method Dispatching**: CBVs inspect `request.method` and dynamically route calls to `self.get()`, `self.post()`, `self.put()`, or `self.delete()`.
- **`as_view()`**: Class method transforming a CBV into a callable view function compatible with `path()` in `urls.py`.
- **`get_queryset()`**: Hook method on generic views allowing dynamic filtering based on URL kwargs or `request.user`.
- **`get_context_data()`**: Hook method allowing views to inject additional variables into template context alongside default model objects.
- **Inclusion Tag**: A template tag that renders a sub-template with calculated context, functioning like a modern UI component.
- **`reverse_lazy()`**: Lazy variant of `reverse()` evaluated when the URL is accessed, required for class-level attributes like `success_url`.

## Mental Models
- **The Lego Class Assembly**: Function-based views are hand-carved wooden blocks; Class-Based Views are Lego bricks that snap together (mix in `LoginRequired`, snap on `ListView`, plug in `Book` model).
- **Component Sockets (Inclusion Tags)**: Instead of copy-pasting 30 lines of HTML badge code across 10 templates, define a socket (`{% render_book_card book %}`) that renders the pre-fabricated card widget.
- **Left-to-Right Mixin Shield**: Mixins sit on the left to act as protective shields, intercepting and inspecting the request before it reaches the heavy generic view engine on the right.

## Anti-patterns
- **Incorrect Mixin Inheritance Order**: Declaring `class MyView(ListView, LoginRequiredMixin)`. `ListView.dispatch` executes first, allowing unauthenticated users to view private records before `LoginRequiredMixin` runs.
- **Mutating State Inside `get_queryset()` or `get_context_data()`**: Performing database updates or external API calls inside read-only query hooks, violating idempotent GET semantics.
- **Fat Template Tags with Business Rules**: Embedding core business algorithms (e.g. calculating tax discounts or executing database mutations) inside template tags. Template tags should only format or display data.
- **Forgetting `templatetags` Package Structure**: Creating `reviews/templatetags.py` as a single file instead of a package directory (`reviews/templatetags/__init__.py`), causing Django's template engine to fail loading tags.

## Code Examples

### Generic Class-Based Views with Filtering and Context

```python
# reviews/views.py
from django.views.generic import ListView, DetailView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse_lazy
from django.db.models import Avg
from .models import Book, Review

class BookListView(ListView):
    model = Book
    template_name = "reviews/book_list.html"
    context_object_name = "books"
    paginate_by = 10

    def get_queryset(self):
        # Annotate books with average rating and filter active
        return (
            Book.objects.select_related("publisher")
            .annotate(average_rating=Avg("review__rating"))
            .order_by("-publication_date")
        )

class BookDetailView(DetailView):
    model = Book
    template_name = "reviews/book_detail.html"
    context_object_name = "book"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Inject additional context data
        context["recent_reviews"] = self.object.review_set.order_by("-date_created")[:5]
        return context

class BookCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Book
    fields = ("title", "isbn", "publication_date", "publisher")
    template_name = "reviews/book_form.html"
    permission_required = "reviews.add_book"
    success_url = reverse_lazy("reviews:book_list")
```
- **What it demonstrates**: Proper mixin ordering (`LoginRequiredMixin` first), queryset customization, context injection, and `reverse_lazy`.

URL binding:
```python
# reviews/urls.py
from django.urls import path
from .views import BookListView, BookDetailView, BookCreateView

urlpatterns = [
    path("books/", BookListView.as_view(), name="book_list"),
    path("books/<int:pk>/", BookDetailView.as_view(), name="book_detail"),
    path("books/add/", BookCreateView.as_view(), name="book_add"),
]
```

### Custom Template Tags and Inclusion Tags

Package layout:
`reviews/templatetags/__init__.py` (empty)
`reviews/templatetags/review_tags.py`

Tag definitions:
```python
# reviews/templatetags/review_tags.py
from django import template
from reviews.models import Book

register = template.Library()

# 1. Custom Filter: Format rating as stars
@register.filter(name="star_rating")
def star_rating(value: int) -> str:
    if not value:
        return "Unrated"
    return "★" * int(value) + "☆" * (5 - int(value))

# 2. Simple Tag: Count reviews for a book
@register.simple_tag
def review_count(book: Book) -> int:
    return book.review_set.count()

# 3. Inclusion Tag: Render reusable book card widget
@register.inclusion_tag("reviews/partials/book_card.html")
def render_book_card(book: Book, show_publisher: bool = True):
    return {
        "book": book,
        "show_publisher": show_publisher,
        "review_count": book.review_set.count(),
    }
```

Partial template (`reviews/templates/reviews/partials/book_card.html`):
```html
<div class="card p-3 mb-2 shadow-sm">
    <h3><a href="{% url 'reviews:book_detail' pk=book.pk %}">{{ book.title }}</a></h3>
    {% if show_publisher %}
        <p class="text-muted">Published by: {{ book.publisher.name }}</p>
    {% endif %}
    <span class="badge bg-info">{{ review_count }} reviews</span>
</div>
```

Using tags in templates:
```html
{% extends "reviews/base.html" %}
{% load review_tags %}

{% block content %}
    <h1>All Books</h1>
    {% for book in books %}
        <!-- Render custom inclusion tag component -->
        {% render_book_card book show_publisher=True %}
    {% endfor %}
{% endblock %}
```
- **What it demonstrates**: Registering filters, simple tags, and inclusion tags rendering reusable partials.

## Reference Tables

### Core Generic Class-Based Views

| View Class | Target Operation | Required Attributes | Key Hook Methods |
|---|---|---|---|
| `TemplateView` | Render static/contextual page | `template_name` | `get_context_data()` |
| `ListView` | Render paginated list | `model` or `queryset` | `get_queryset()`, `get_context_data()` |
| `DetailView` | Render single object | `model`, URL `pk` or `slug` | `get_object()`, `get_context_data()` |
| `CreateView` | Create new instance via form | `model`, `fields` or `form_class` | `form_valid()`, `get_success_url()` |
| `UpdateView` | Update instance via form | `model`, `fields` or `form_class` | `form_valid()`, `get_success_url()` |
| `DeleteView` | Delete instance on POST | `model`, `success_url` | `delete()`, `get_success_url()` |

### Template Tag Types Comparison

| Tag Type | Decorator | Return Type | Use Case |
|---|---|---|---|
| **Filter** | `@register.filter` | Modified primitive/string | In-line data formatting (`{{ date\|date }}`) |
| **Simple Tag** | `@register.simple_tag` | String or Python object | Calculation, count, or query injection |
| **Inclusion Tag**| `@register.inclusion_tag`| Context `dict` | Reusable HTML component partials |

## Worked Example

### Refactoring Book Detail to CBV with Star Rating Component

1. Implement `star_rating` filter in `reviews/templatetags/review_tags.py`:
   - Takes integer rating (1–5) and returns star glyph string (`"★★★★☆"`).
2. Refactor view in `reviews/views.py`:
   ```python
   class BookDetailView(DetailView):
       model = Book
       template_name = "reviews/book_detail.html"
       context_object_name = "book"
   ```
3. Update `reviews/templates/reviews/book_detail.html`:
   ```html
   {% extends "reviews/base.html" %}
   {% load review_tags %}

   {% block content %}
       <h1>{{ book.title }}</h1>
       {% for review in book.review_set.all %}
           <div class="review">
               <p>{{ review.rating|star_rating }} ({{ review.rating }}/5)</p>
               <p>{{ review.content }}</p>
           </div>
       {% endfor %}
   {% endblock %}
   ```
4. Testing:
   - Navigating to `/books/1/` renders `★★★★★ (5/5)` for a 5-star review and `★★★☆☆ (3/5)` for a 3-star review.

## Key Takeaways
1. Class-Based Views (CBVs) eliminate repetitive request-handling boilerplate through object-oriented inheritance.
2. Mixins must always be declared *before* the generic base view in Python's class inheritance list (`MRO`).
3. Use `get_queryset()` on `ListView` for dynamic filtering and optimization (`select_related`, `prefetch_related`).
4. Custom template tags and filters must be housed within an app's `<app>/templatetags/` package.
5. Use `@register.inclusion_tag` to encapsulate reusable HTML card and widget components.

## Connects To
- **Ch 03**: Django Views, URL Configuration, and Templates — the foundational view concepts upgraded here to CBVs.
- **Ch 09**: Sessions and Authentication — supplies `LoginRequiredMixin` and `PermissionRequiredMixin`.
- **Ch 12**: Building a REST API — contrasting Django HTML CBVs with Django REST Framework API views.
