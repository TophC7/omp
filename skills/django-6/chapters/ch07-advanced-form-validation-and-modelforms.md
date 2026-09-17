# Chapter 7: Advanced Form Validation and Model Forms

## Core Idea
Django's validation pipeline provides a structured three-tier execution hierarchy (validators, field cleaning, multi-field cleaning), while the `ModelForm` framework bridges the gap between database models and HTML forms by automatically generating fields, widgets, and persistence operations directly from model metadata.

## Frameworks Introduced
- **The Three-Tier Validation Pipeline**:
  - *Tier 1: Field Validators (`validators=[...]`)*: Standalone functions taking a value and raising `django.core.exceptions.ValidationError`. Reusable across multiple forms and models.
  - *Tier 2: Single-Field Cleaning (`clean_<fieldname>(self)`)*: Methods on the form class executing after field validators. Accesses `self.cleaned_data["field"]`, performs field-specific normalization (e.g. lowercasing or rounding), and **must return the cleaned value**.
  - *Tier 3: Multi-Field Form Cleaning (`clean(self)`)*: Form-wide method executing after all individual fields have been cleaned. Evaluates cross-field dependencies (e.g. "if checkbox X is checked, field Y is required"). Accesses `self.cleaned_data`, raises non-field `ValidationError` or attaches errors to specific fields via `self.add_error("field", msg)`, and returns the cleaned dictionary.

- **The ModelForm Framework (`forms.ModelForm`)**:
  - Automatically derives form fields, widgets, labels, validation rules, and error messages directly from a corresponding `models.Model`.
  - Inner `class Meta:` defines the mapping contract:
    - `model`: Target model class (e.g., `Book`).
    - `fields`: Explicit whitelist tuple of model field names to include (e.g., `("title", "isbn", "publisher")`).
    - `exclude`: Explicit blacklist tuple of field names to omit.
    - `widgets`: Dictionary overriding default HTML input elements (e.g., specifying HTML5 `<input type="date">`).

- **The ModelForm Persistence Lifecycle (`save()` & `commit=False`)**:
  - `form.save()`: Writes the instance to the database immediately and updates many-to-many relations.
  - `instance = form.save(commit=False)`: Creates and populates the model instance in memory *without* writing to the database. Allows views to attach non-form data (e.g., `instance.creator = request.user`) before saving.
  - `form.save_m2m()`: Required when using `commit=False` on models with `ManyToManyField` relationships.

- **Instance Binding for Updates**:
  - Distinguishes creation from modification:
    - Create: `form = BookForm(request.POST)` (instantiates a new record).
    - Update: `form = BookForm(request.POST, instance=existing_book)` (populates and updates the existing record).

## Key Concepts
- **`ValidationError`**: Special exception caught automatically by Django's form processing to populate `form.errors` without crashing the view.
- **`add_error(field, error)`**: Method on `Form` allowing multi-field cleaning logic in `clean()` to associate an error directly with a specific input field.
- **`save(commit=False)`**: Factory call returning an unsaved model instance from validated form data.
- **`save_m2m()`**: Method persisting many-to-many relationship junction records after an uncommitted instance has been saved.
- **Whitelisting Fields**: Security practice requiring developers to specify exact field names in `Meta.fields` rather than using `fields = '__all__'`.

## Mental Models
- **The Three-Gate Checkpoint**:
  - Gate 1 (Validators): Inspects individual items in isolation ("Is this string formatted as an ISBN?").
  - Gate 2 (`clean_<field>`): Normalizes the single item ("Strip whitespace and format uppercase").
  - Gate 3 (`clean`): Inspects the relationship between items ("You selected express shipping, so a phone number is required").
- **The Form as a Model Shadow**: A `ModelForm` is an interactive projection of a database row into the browser; edits made in the shadow project directly back onto the database row upon calling `.save()`.

## Anti-patterns
- **Forgetting to Return Value in `clean_<fieldname>()`**: Failing to write `return value` at the end of a `clean_title()` method. The method returns `None`, overwriting the user's data with `None` in `cleaned_data`.
- **Using `fields = '__all__'` on Sensitive Models**: Exposing all model fields to public forms, allowing malicious users to forge POST parameters that overwrite administrative or permission flags.
- **Omitting `form.save_m2m()` after `commit=False`**: Saving an instance with `instance.save()` after `commit=False` but forgetting `form.save_m2m()`, silently dropping all selected many-to-many relations.
- **Accessing Uncleaned Fields in `clean()` without `.get()`**: Writing `self.cleaned_data['email']` in `clean()` when a prior field-level validator failed. If a field fails validation, it is omitted from `cleaned_data`. Always use `self.cleaned_data.get('field')`.

## Code Examples

### Custom Validators and Cleaning Methods

```python
# reviews/forms.py
from django import forms
from django.core.exceptions import ValidationError
from .models import Publisher

def validate_email_domain(value: str) -> None:
    if not value.endswith("@example.com"):
        raise ValidationError("Only @example.com email addresses are permitted.")

class PublisherForm(forms.ModelForm):
    class Meta:
        model = Publisher
        fields = ("name", "website", "email")

    # Tier 1 validator attached to field
    email = forms.EmailField(validators=[validate_email_domain])

    # Tier 2: Single-field cleaning
    def clean_name(self) -> str:
        name = self.cleaned_data["name"].strip()
        if len(name) < 2:
            raise ValidationError("Publisher name is too short.")
        return name.title()

    # Tier 3: Multi-field cleaning
    def clean(self) -> dict:
        cleaned_data = super().clean()
        website = cleaned_data.get("website")
        email = cleaned_data.get("email")

        # Invariant: Publisher website cannot match email domain
        if website and email and website.split("://")[-1] in email:
            self.add_error("website", "Website domain cannot match email address exactly.")

        return cleaned_data
```
- **What it demonstrates**: Combining validator functions, `clean_name()` normalization, and cross-field `clean()` logic.

### ModelForm Creation and Update View (`commit=False`)

```python
# reviews/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpRequest, HttpResponse
from .forms import BookForm
from .models import Book

def book_edit(request: HttpRequest, pk: int = None) -> HttpResponse:
    # If pk provided, load existing instance for editing; otherwise create new
    book = get_object_or_404(Book, pk=pk) if pk else None

    if request.method == "POST":
        form = BookForm(request.POST, instance=book)
        if form.is_valid():
            # Create instance in memory without writing to database
            book_instance = form.save(commit=False)
            
            # Attach metadata (e.g. audit or logged-in user)
            # book_instance.created_by = request.user
            book_instance.save()
            
            # Persist many-to-many relations (contributors)
            form.save_m2m()
            
            return redirect("reviews:book_detail", pk=book_instance.pk)
    else:
        form = BookForm(instance=book)

    return render(request, "reviews/book_edit.html", {"form": form, "book": book})
```
- **What it demonstrates**: Handling both creation and editing in a single view, utilizing `commit=False` and `save_m2m()`.

## Reference Tables

### Validation Pipeline Execution Hierarchy

| Step | Scope | Target Method | Data Access | Return Requirement |
|---|---|---|---|---|
| **1. To Python** | Single Field | `Field.to_python()` | Raw string from POST | Native Python type |
| **2. Validators** | Single Field | Functions in `validators=[...]`| Coerced Python object | None (raises `ValidationError`) |
| **3. Field Cleaning**| Single Field | `Form.clean_<field>()` | `self.cleaned_data["field"]`| **Must return cleaned value** |
| **4. Form Cleaning** | Multi-Field | `Form.clean()` | `self.cleaned_data` dict | **Must return cleaned_data** |

### Key ModelForm `Meta` Options

| Meta Option | Type | Purpose |
|---|---|---|
| `model` | `Model` class | The model backing the form |
| `fields` | `tuple[str]` | Whitelist of model fields exposed on the form |
| `exclude` | `tuple[str]` | Blacklist of model fields hidden from the form |
| `widgets` | `dict[str, Widget]` | Custom HTML input widgets for specific fields |
| `labels` | `dict[str, str]` | Custom human-readable labels overriding model verbose_name |
| `help_texts` | `dict[str, str]` | Custom explanatory text beneath fields |
| `error_messages`| `dict[str, dict]` | Custom text overriding default validation errors |

## Worked Example

### Building Book ModelForm with Custom Date Widget

1. Define `BookForm` in `reviews/forms.py`:
```python
from django import forms
from .models import Book

class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ("title", "publication_date", "isbn", "publisher")
        widgets = {
            "publication_date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
        }

    def clean_isbn(self) -> str:
        isbn = self.cleaned_data["isbn"].replace("-", "").strip()
        if len(isbn) not in (10, 13):
            raise forms.ValidationError("ISBN must be exactly 10 or 13 digits long.")
        return isbn
```

2. Render in template:
```html
<form method="post">
    {% csrf_token %}
    {{ form.as_div }}
    <button type="submit">Save Book</button>
</form>
```

3. Execution flow:
   - Form renders native browser date-picker `<input type="date">` for `publication_date`.
   - User inputs `" 978-1-83620-207-3 "`.
   - `clean_isbn()` strips hyphens and spaces, verifies length is 13, and stores `"9781836202073"` in `cleaned_data`.
   - Calling `form.save()` writes the record to the PostgreSQL/SQLite `reviews_book` table.

## Key Takeaways
1. Single-field cleaning methods `clean_<field>()` must always return the cleaned value.
2. Cross-field validation belongs in `clean()`, using `self.add_error("field", msg)` to bind errors to inputs.
3. Always explicitly define `fields` in `ModelForm.Meta` to prevent unintended exposure of internal model fields.
4. When using `form.save(commit=False)` to attach metadata before saving, always call `form.save_m2m()` afterwards to preserve many-to-many records.
5. Pass `instance=obj` when instantiating forms to bind existing database rows for update operations.

## Connects To
- **Ch 02**: Models and Migrations — provides the database models converted into ModelForms.
- **Ch 06**: Forms — the foundational form validation and CSRF concepts expanded here.
- **Ch 08**: Media Serving and File Uploads — processing file and image uploads using ModelForms.
