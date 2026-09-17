# Chapter 6: Forms

## Core Idea
The Django Forms library acts as an automated gatekeeper between raw HTTP client input and Python application code, performing a threefold responsibility: generating accessible HTML form controls, validating incoming data against strict rules, and coercing raw strings into clean Python primitives.

## Frameworks Introduced
- **The Form Class Framework (`django.forms.Form`)**:
  - Declarative Python class mapping fields and widgets to HTML form inputs.
  - When to use: Whenever an application accepts user input via HTTP GET (searches, filters) or HTTP POST (creations, updates, actions).
  - How: Subclass `forms.Form`, define field attributes (`CharField`, `IntegerField`, `ChoiceField`), and bind widgets for custom HTML styling.
  - Why it works: Serves as a single source of truth for both frontend HTML rendering and backend server-side validation.
  - Failure mode: Relying on frontend HTML5 or JavaScript validation alone without server-side validation.

- **GET vs. POST Semantics & CSRF Protection**:
  - *GET Requests*: Used for idempotent queries (searches, list filters). Data is appended to the query string, bookmarkable, and does not alter server state. Does not require CSRF tokens.
  - *POST Requests*: Used for operations that mutate state (creating accounts, submitting reviews, purchasing goods). Data is transmitted in the HTTP request body.
  - *Cross-Site Request Forgery (CSRF)*: Django protects POST requests via `CsrfViewMiddleware`. Every POST `<form>` must include the `{% csrf_token %}` template tag, which renders a cryptographically signed hidden input matching a user session cookie.

- **Bound vs. Unbound Form Lifecycle**:
  - *Unbound Form*: Instantiated without data (`form = ReviewForm()`). Renders blank inputs with default values. Calling `form.is_valid()` on an unbound form returns `False`.
  - *Bound Form*: Instantiated with incoming request data (`form = ReviewForm(request.POST)`).
  - Calling `form.is_valid()` executes validation pipelines:
    - If valid: Populates the `form.cleaned_data` dictionary with typed Python objects (`int`, `date`, `bool`).
    - If invalid: Populates `form.errors` and allows re-rendering the template with contextual error feedback.

- **Modern Form Rendering API**:
  - Template shortcuts:
    - `{{ form.as_div }}`: Modern default rendering form fields wrapped in semantic `<div>` elements.
    - `{{ form.as_p }}`, `{{ form.as_table }}`, `{{ form.as_ul }}`: Legacy wrapper methods.
  - Granular field rendering: Looping through `{% for field in form %}` allows explicit control over `{{ field.label_tag }}`, `{{ field }}`, `{{ field.help_text }}`, and `{{ field.errors }}`.

## Key Concepts
- **Form Widget**: The Python class responsible for rendering raw HTML form inputs (e.g. `TextInput`, `Textarea`, `Select`, `CheckboxInput`).
- **`cleaned_data`**: A dictionary containing validated and type-coerced Python primitives available only after calling `form.is_valid()`.
- **`is_valid()`**: Method executing field validation, populating `cleaned_data` on success, or populating `errors` on failure.
- **CSRF Token**: A unique secret token required on all state-mutating requests to verify requests originated from the genuine website.
- **Field Normalization**: Converting raw string inputs (`" 2026-05-01 "` or `"42"`) into native Python objects (`datetime.date(2026, 5, 1)` or `int(42)`).
- **Initial Data**: Default values supplied to unbound forms via `form = MyForm(initial={"rating": 5})`.

## Mental Models
- **The Bouncer and Data Coercer**: The form stands at the door of your view; it checks IDs and searches luggage (validation), unpacks messy strings into tidy Python objects (coercion), and only lets clean data into `cleaned_data`.
- **The Unbound vs. Bound Document**: An unbound form is a blank paper form waiting to be filled out; a bound form is a completed form submitted by an applicant, ready for approval or red-pen error corrections.
- **Flipping the Light Switch**: Idempotent GET searches merely inspect the room; POST actions flick the switch and modify state, requiring the CSRF padlock.

## Anti-patterns
- **Omitting `{% csrf_token %}` on POST Forms**: Submitting an HTML POST form without `{% csrf_token %}` causes Django to reject the request with an HTTP 403 Forbidden error.
- **Bypassing `cleaned_data`**: Reading directly from `request.POST["qty"]` inside views instead of `form.cleaned_data["qty"]`, bypassing type-checking, string stripping, and validation rules.
- **Mutating State on GET Requests**: Writing views that delete or update database rows on GET requests, exposing the site to destructive web crawler clicks.
- **Client-Side-Only Validation**: Assuming HTML5 `required` or JavaScript regexes prevent malicious input. Attackers bypass browsers using `curl` or Postman.

## Code Examples

### Form Class Definition with Fields and Widgets

```python
# reviews/forms.py
from django import forms

class SearchForm(forms.Form):
    search = forms.CharField(
        required=False,
        min_length=3,
        max_length=100,
        widget=forms.TextInput(attrs={"placeholder": "Search by title or author..."}),
        help_text="Enter at least 3 characters to search."
    )
    search_in = forms.ChoiceField(
        required=False,
        choices=(("title", "Title"), ("contributor", "Contributor")),
        initial="title",
        widget=forms.Select(attrs={"class": "form-select"})
    )

class ReviewForm(forms.Form):
    content = forms.CharField(
        widget=forms.Textarea(attrs={"rows": 4, "cols": 40}),
        help_text="Write your honest review here."
    )
    rating = forms.IntegerField(
        min_value=1,
        max_value=5,
        widget=forms.NumberInput(attrs={"class": "rating-input"}),
        help_text="Rate from 1 to 5 stars."
    )
```
- **What it demonstrates**: Defining required/optional fields, range boundaries, choice tuples, and custom widget attributes.

### Standard View Pattern for Form Handling

```python
# reviews/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpRequest, HttpResponse
from .forms import ReviewForm
from .models import Book, Review

def book_review(request: HttpRequest, pk: int) -> HttpResponse:
    book = get_object_or_404(Book, pk=pk)

    if request.method == "POST":
        # 1. Bind form to POST data
        form = ReviewForm(request.POST)
        # 2. Validate input
        if form.is_valid():
            # 3. Access clean data
            Review.objects.create(
                book=book,
                content=form.cleaned_data["content"],
                rating=form.cleaned_data["rating"],
            )
            # 4. Redirect after POST (PRG pattern)
            return redirect("reviews:book_detail", pk=book.pk)
    else:
        # Unbound initial form for GET request
        form = ReviewForm()

    return render(request, "reviews/review_form.html", {"form": form, "book": book})
```
- **What it demonstrates**: The Post/Redirect/Get (PRG) pattern: checking `request.method == "POST"`, validating, extracting `cleaned_data`, and redirecting.

### Modern Template Rendering (`as_div` and Granular Loops)

Using `as_div`:
```html
<!-- reviews/templates/reviews/review_form.html -->
{% extends "reviews/base.html" %}

{% block content %}
    <h1>Write a Review for {{ book.title }}</h1>
    <form method="post">
        {% csrf_token %}
        {{ form.as_div }}
        <button type="submit">Submit Review</button>
    </form>
{% endblock %}
```

Granular loop with custom markup:
```html
<form method="post">
    {% csrf_token %}
    {% for field in form %}
        <div class="form-group mb-3">
            {{ field.label_tag }}
            {{ field }}
            {% if field.help_text %}
                <small class="form-text text-muted">{{ field.help_text }}</small>
            {% endif %}
            {% for error in field.errors %}
                <div class="invalid-feedback d-block">{{ error }}</div>
            {% endfor %}
        </div>
    {% endfor %}
    <button type="submit" class="btn btn-primary">Submit</button>
</form>
```
- **What it demonstrates**: Applying CSRF tokens, semantic `as_div` output, and manual field component rendering with error feedback.

## Reference Tables

### Common Form Fields and Default Widgets

| Field Class | Default Widget | Coerced Python Data Type |
|---|---|---|
| `CharField` | `TextInput` | `str` |
| `IntegerField` | `NumberInput` | `int` |
| `FloatField` | `NumberInput` | `float` |
| `DecimalField` | `NumberInput` | `decimal.Decimal` |
| `DateField` | `DateInput` | `datetime.date` |
| `DateTimeField`| `DateTimeInput` | `datetime.datetime` |
| `BooleanField` | `CheckboxInput` | `bool` |
| `ChoiceField` | `Select` | `str` (or matched choice type) |
| `MultipleChoiceField` | `SelectMultiple` | `list[str]` |
| `EmailField` | `EmailInput` | `str` |

### Bound vs. Unbound Form Comparison

| Dimension | Unbound Form (`ReviewForm()`) | Bound Form (`ReviewForm(request.POST)`) |
|---|---|---|
| **Data Attached** | None (or initial defaults) | `request.POST` dictionary |
| **`is_bound` Property**| `False` | `True` |
| **`is_valid()` Result**| Always returns `False` | Evaluates fields; returns `True` or `False` |
| **`cleaned_data`** | Not available (raises `AttributeError`) | Available if `is_valid()` is `True` |
| **`errors`** | Empty | Populated if validation fails |
| **HTML Output** | Blank or initial values | User-entered values + validation error lists |

## Worked Example

### Building Search Form with QueryDict Binding

1. Form definition in `reviews/forms.py`:
```python
class BookSearchForm(forms.Form):
    search = forms.CharField(min_length=3, required=True)
```

2. Search view in `reviews/views.py`:
```python
def search_books(request: HttpRequest) -> HttpResponse:
    form = BookSearchForm(request.GET or None)
    books = []
    
    if form.is_valid():
        query = form.cleaned_data["search"]
        books = Book.objects.filter(title__icontains=query)
        
    return render(request, "reviews/search_results.html", {"form": form, "books": books})
```

3. Template execution:
   - Initial visit to `/search/`: `form` is unbound (or bound to empty dict), displaying clean search input without error messages.
   - User submits `"py"` (<3 characters): `form.is_valid()` returns `False`. Page re-renders displaying: *"Ensure this value has at least 3 characters (it has 2)."*
   - User submits `"Python"`: Form validates, queries `Book.objects.filter(title__icontains="Python")`, and displays results.

## Key Takeaways
1. Django forms streamline three operations: generating HTML widgets, validating input, and coercing strings into Python primitives.
2. Every state-changing form must use HTTP POST and include the `{% csrf_token %}` tag.
3. Use the Post/Redirect/Get (PRG) pattern for all successful form submissions to prevent duplicate form submissions on page refresh.
4. Always read submitted values from `form.cleaned_data` rather than `request.POST`.
5. Render forms easily with `{{ form.as_div }}` or loop through `{% for field in form %}` for customized CSS frameworks.

## Connects To
- **Ch 01**: Introduction to Django — where basic QueryDict inspection was introduced.
- **Ch 03**: Django Views, URL Configuration, and Templates — rendering forms inside template layouts.
- **Ch 07**: Advanced Form Validation and Model Forms — creating forms tied directly to ORM models.
