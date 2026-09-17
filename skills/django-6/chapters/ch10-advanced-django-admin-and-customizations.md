# Chapter 10: Advanced Django Admin and Customizations

## Core Idea
The Django Admin can be extended from a simple CRUD panel into a bespoke enterprise operational console by customizing the user identity model (`AUTH_USER_MODEL`), embedding parent-child editing workflows (`InlineModelAdmin`), defining bulk actions, and mounting custom administrative views.

## Frameworks Introduced
- **Custom User Model Strategies (`AUTH_USER_MODEL`)**:
  - *Strategy A (One-to-One Profile Model)*: Retains default `auth.User`, adding a satellite profile (`ReviewerProfile`) linked via `models.OneToOneField(settings.AUTH_USER_MODEL)`. Best for simple metadata additions on existing projects.
  - *Strategy B (Subclassing `AbstractUser`)*: Replaces default user model while keeping standard username/password/permission mechanisms, adding custom fields directly (`telephone`, `date_of_birth`). Must be configured in `settings.py` before initial migrations.
  - *Strategy C (Subclassing `AbstractBaseUser` + `PermissionsMixin`)*: Complete rewrite of identity mechanics (e.g. using `email` as the unique identifier and eliminating `username`). Requires implementing a custom `BaseUserManager`.
  - *Golden Rule*: Always configure a custom `AUTH_USER_MODEL` at the very start of a project, even if it merely inherits `AbstractUser` without new fields, to prevent migration nightmares later.

- **Inline ModelAdmin Framework (`TabularInline` & `StackedInline`)**:
  - Allows editing related child records directly within the parent model's change form page.
  - Subclasses:
    - `admin.TabularInline`: Renders child records as compact, tabular spreadsheet rows.
    - `admin.StackedInline`: Renders each child record as an individual stacked form box.
  - Attach to parent: `inlines = [BookContributorInline, ReviewInline]`.
  - Attributes: `extra` (number of blank rows to display), `max_num`, `can_delete`.

- **Custom Admin Actions**:
  - Custom functions executing bulk business operations over user-selected change list rows.
  - Signature: `def action_name(modeladmin, request, queryset): ...`.
  - Configured via `@admin.action(description="...")` and registered in `ModelAdmin.actions = [action_name]`.
  - Executed within a single HTTP request; should use `queryset.update()` for bulk database operations.

- **Custom AdminSite & Subclassed Admin Views**:
  - Subclass `admin.AdminSite` to override global templates (`login_template`, `index_template`) and register isolated administrative dashboards.
  - Mount custom URL endpoints into the admin via `ModelAdmin.get_urls()` or `AdminSite.get_urls()`.
  - Wrap custom views with `self.admin_view(view_func)` to enforce staff authentication, permission checks, and CSRF protection automatically.

## Key Concepts
- **`AUTH_USER_MODEL`**: Setting pointing to the active user model (`"accounts.User"`).
- **`get_user_model()`**: Function returning the currently active user model class; never import `from django.contrib.auth.models import User` directly in reusable apps.
- **`TabularInline`**: Compact table layout for child models in admin forms.
- **`StackedInline`**: Expanded block layout for child models in admin forms.
- **`admin_view()`**: Security wrapper ensuring an admin view cannot be accessed by unauthenticated or non-staff users.
- **Action Description**: Human-readable label displayed in the admin actions dropdown menu.

## Mental Models
- **Nested Russian Dolls (Inlines)**: Instead of visiting the Book page, noting the ID, navigating to the Review page, and selecting the Book, inlines open the Book doll and let you inspect and edit its child Review dolls directly inside.
- **The Mass Operations Toolbar**: Admin actions treat the change list as a queue; select 50 rows, pull the action lever ("Publish Selected"), and update all rows in a single swipe.
- **The Fortress Gatekeeper (`admin_view`)**: Any custom page mounted inside the admin must pass through the fortress gatekeeper (`self.admin_view`), which checks staff credentials before letting requests through.

## Anti-patterns
- **Switching `AUTH_USER_MODEL` Mid-Project**: Attempting to change `AUTH_USER_MODEL` after foreign keys and initial migrations have already run in production. This breaks relational schema consistency and requires complex database migrations.
- **Row-by-Row Loops in Admin Actions**: Writing `for obj in queryset: obj.status = 'p'; obj.save()` inside a bulk action for 1,000 selected rows, triggering 1,000 queries. Use `queryset.update(status='p')`.
- **Importing `auth.models.User` Directly**: Hardcoding `from django.contrib.auth.models import User` across models and views, breaking compatibility whenever a custom user model is configured. Always use `settings.AUTH_USER_MODEL` in models and `get_user_model()` in views.
- **Exposing Unprotected Views in Admin**: Adding a custom URL to admin `get_urls()` without wrapping it in `self.admin_view()`, creating an unauthorized access loophole.

## Code Examples

### Custom User Model with Email as Primary Identifier

```python
# accounts/models.py
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models

class CustomUserManager(BaseUserManager):
    def create_user(self, email: str, password: str = None, **extra_fields):
        if not email:
            raise ValueError("Email is required.")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email: str, password: str = None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50, blank=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self) -> str:
        return self.email
```

Configuring `settings.py`:
```python
# bookr/settings.py
AUTH_USER_MODEL = "accounts.CustomUser"
```
- **What it demonstrates**: Email-based authentication using `AbstractBaseUser` and a custom manager.

### Inline Model Editing and Custom Bulk Actions

```python
# reviews/admin.py
from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest
from .models import Book, BookContributor, Review

class BookContributorInline(admin.TabularInline):
    model = BookContributor
    extra = 1  # Display 1 blank row for new entries
    autocomplete_fields = ("contributor",)

class ReviewInline(admin.StackedInline):
    model = Review
    extra = 0
    readonly_fields = ("date_created", "date_edited")

@admin.action(description="Reset rating to 5 for selected reviews")
def set_rating_five(modeladmin: admin.ModelAdmin, request: HttpRequest, queryset: QuerySet):
    updated = queryset.update(rating=5)
    modeladmin.message_user(request, f"Successfully updated {updated} reviews to 5 stars.")

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ("title", "isbn", "publisher")
    inlines = [BookContributorInline, ReviewInline]
    search_fields = ("title", "isbn")

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("book", "rating", "date_created")
    actions = [set_rating_five]
```
- **What it demonstrates**: Tabular and stacked inlines on `BookAdmin`, plus bulk action updates.

### Adding a Custom View to AdminSite

```python
# bookr/admin.py
from django.contrib import admin
from django.urls import path
from django.template.response import TemplateResponse
from django.http import HttpRequest

class CustomAdminSite(admin.AdminSite):
    site_header = "Bookr Control Room"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            # Wrap view with self.admin_view to enforce staff access
            path("system-health/", self.admin_view(self.system_health_view), name="system_health"),
        ]
        return custom_urls + urls

    def system_health_view(self, request: HttpRequest):
        context = {
            **self.each_context(request),
            "title": "System Health",
            "db_status": "Operational",
            "cache_status": "Operational",
        }
        return TemplateResponse(request, "admin/system_health.html", context)

custom_admin_site = CustomAdminSite(name="custom_admin")
```
- **What it demonstrates**: Adding custom endpoints into the admin URL space with staff-protected permissions.

## Reference Tables

### User Customization Approaches

| Strategy | Base Class | When to Use | Trade-offs |
|---|---|---|---|
| **One-to-One Profile** | `models.Model` | Adding metadata to existing legacy projects | Extra SQL join; two separate admin forms |
| **`AbstractUser`** | `AbstractUser` | Standard username login with extra fields | Cleanest approach for new projects |
| **`AbstractBaseUser`** | `AbstractBaseUser` | Non-standard login (email-only, phone-only) | Must write custom user manager from scratch |

### `StackedInline` vs. `TabularInline`

| Property | `TabularInline` | `StackedInline` |
|---|---|---|
| **Layout Style** | Horizontal spreadsheet row | Vertical form card |
| **Visual Density** | Compact; displays many records | Expansive; spacious |
| **Best Used For** | Relations with 1–4 small fields | Relations with long textareas or many fields |

## Worked Example

### Complete Bookr Administration Experience

1. Configure `BookContributorInline` with `extra = 1` inside `BookAdmin`.
2. Configure `ReviewInline` with `extra = 0` inside `BookAdmin`.
3. Open `http://127.0.0.1:8000/admin/reviews/book/add/`:
   - Admin displays Book details at top.
   - Beneath Book fields, a tabular grid lets editors assign Contributors and Roles without leaving the page.
   - Click "Save": Django writes the Book record, then loops through the formset to insert all `BookContributor` rows within a single atomic database transaction.

## Key Takeaways
1. Always configure a custom `AUTH_USER_MODEL` at the start of every Django project.
2. Use `get_user_model()` and `settings.AUTH_USER_MODEL` to keep code decoupled from specific user classes.
3. Embed child model editing inside parent forms using `TabularInline` or `StackedInline`.
4. Perform bulk database updates in custom Admin Actions via `queryset.update()` to prevent N-query loops.
5. Always wrap custom admin views with `self.admin_view()` to enforce staff authentication.

## Connects To
- **Ch 04**: An Introduction to Django Admin — foundational admin configuration.
- **Ch 09**: Sessions and Authentication — user permissions and authentication backends.
- **Ch 11**: Advanced Templating and Class-Based Views — building advanced views and custom templates.
