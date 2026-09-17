---
name: django-6
description: "Knowledge base from \"Web Development with Django 6\" (Third Edition) by Chris Guest, Mark Walker, Ben Shaw, Saurabh Badhwar, and Bharath Chandra K S. Use when building Python web applications with Django 6, configuring MVT, ORM models and migrations, views, templates, forms, admin, DRF REST APIs, testing, or production deployment."
---

<!-- argument-hint: [topic, framework name, or chapter number] -->

# Web Development with Django 6
**Authors**: Chris Guest, Mark Walker, Ben Shaw, Saurabh Badhwar, Bharath Chandra K S | **Pages**: ~758 | **Chapters**: 15 | **Generated**: 2026-09-05

## How to Use This Skill

- **Without arguments** — load core architectural frameworks, MVT concepts, and best practices
- **With a topic** — ask about `models`, `migrations`, `views`, `forms`, `admin`, `static-files`, `drf-api`, `testing`, or `deployment`; I load and reason from the relevant chapter
- **With a chapter** — ask for `ch01` through `ch15` to inspect a specific chapter
- **Browse** — ask "what chapters do you have?" to see the full chapter index

When you ask about a topic not covered in Core Frameworks below, I will read the relevant chapter file under `chapters/` before answering.

---

## Core Frameworks & Mental Models

### 1. Model-View-Template (MVT) Architecture
- **Model**: Python classes subclassing `models.Model` defining database schemas, relational constraints, and business data logic.
- **View**: Request handlers (functions or classes) processing an incoming `HttpRequest`, executing queries, and returning an `HttpResponse`.
- **Template**: Presentation layout written in Django Template Language (DTL), combining HTML structure with variables (`{{ }}`), tags (`{% %}`), and filters (`|`).
- **Rule**: Templates never mutate data or execute raw SQL; views orchestrate; models store and validate.

### 2. Django ORM & Migration Lifecycle
- **Schema Blueprint**: Models act as the declarative blueprint for database tables. Fields enforce column data types and constraints.
- **Two-Step Migration Engine**:
  1. `python manage.py makemigrations [app]`: Inspects `models.py` and writes declarative Python migration operations into `<app>/migrations/`.
  2. `python manage.py migrate`: Executes unapplied migrations within database transactions, recording state in `django_migrations`.
- **Relational Integrity**: Foreign keys require explicit `on_delete` behavior (`CASCADE`, `PROTECT`, `SET_NULL`).
- **Lazy Evaluation**: QuerySets do not execute SQL queries when defined; they execute only upon evaluation (iteration, slicing, `list()`, `bool()`, `len()`).
- **Query Optimization**: Prevent N+1 query bottlenecks using `.select_related()` for single foreign keys (SQL JOIN) and `.prefetch_related()` for multi-valued M2M relations (batched lookups).

### 3. URL Dispatching & Path Converters
- **Modular Routing**: Root `urls.py` delegates subdomain routing to app-specific routers via `include("app.urls")`.
- **Typed Converters**: Path patterns extract typed parameters into view keyword arguments: `<int:pk>`, `<slug:slug>`, `<uuid:id>`.
- **Reverse Resolution**: Never hardcode URL strings. Reverse view names dynamically using `reverse("app:name", kwargs={...})` in Python and `{% url 'app:name' arg %}` in templates.

### 4. Template Inheritance & Component Sockets
- **Skeleton & Muscle Model**:
  - Base skeleton template (`base.html`) defines global markup, metadata, navigation, and placeholder sockets (`{% block content %}{% endblock %}`).
  - Child templates inherit via `{% extends "base.html" %}` and fill in specific blocks.
- **Namespacing Rule**: Always store templates in `<app>/templates/<app>/` to prevent directory resolution collisions across installed apps.
- **Inclusion Tags**: Use `@register.inclusion_tag` to encapsulate reusable HTML card and widget components.

### 5. Forms & The Three-Tier Validation Pipeline
- **Role**: Forms generate HTML input widgets, validate incoming client data, and coerce strings into native Python objects (`cleaned_data`).
- **Post/Redirect/Get (PRG)**: Always redirect after a successful POST request to prevent duplicate submissions on page refresh.
- **CSRF Defense**: Every state-changing form must include `{% csrf_token %}` to guard against Cross-Site Request Forgery.
- **Validation Execution Hierarchy**:
  1. *Validators*: Standalone functions in `validators=[...]` validating isolated field values.
  2. *Field Cleaning (`clean_<field>`)*: Single-field method on `Form` that normalizes data and **must return the value**.
  3. *Multi-field Cleaning (`clean`)*: Cross-field method on `Form` validating inter-field dependencies and returning `cleaned_data`.
- **ModelForms**: Subclass `forms.ModelForm` to generate form fields automatically from models; use `form.save(commit=False)` to attach metadata before saving, followed by `form.save_m2m()`.

### 6. Asset Management: Static vs. Media Files
- **Static Assets** (`STATIC_*`): Authored by developers (CSS, JS, site logos); compiled to `STATIC_ROOT` via `collectstatic` and served with cache-busting hashes via `ManifestStaticFilesStorage`.
- **Media Files** (`MEDIA_*`): Uploaded by users at runtime (avatars, document attachments); stored in `MEDIA_ROOT` via `FileField` and `ImageField` (powered by Pillow).
- **Security Invariant**: Never point `STATIC_ROOT` and `MEDIA_ROOT` to the same directory.
- **Multipart Uploads**: Forms uploading files must declare `enctype="multipart/form-data"` and views must bind `request.FILES`.

### 7. Stateful Identity & Access Control
- **Middleware Pipeline**: `SessionMiddleware` reads `sessionid` cookies and attaches `request.session`; `AuthenticationMiddleware` resolves credentials and attaches `request.user`.
- **Authentication Lifecycle**: Verify credentials with `authenticate()`, attach user and rotate session key with `login()`, and clear state with `logout()`.
- **Access Control**: Protect views using `@login_required`, `@permission_required`, or `LoginRequiredMixin` on CBVs.
- **Custom User Models**: Always configure a custom `AUTH_USER_MODEL` at project inception before initial migrations.

### 8. Django REST Framework (DRF) & Decoupled APIs
- **Stateless Communication**: Endpoints exchange JSON payloads over HTTP, using standard status codes (`200`, `201`, `204`, `400`, `401`, `403`, `404`).
- **ModelSerializers**: Provide two-way translation: models to JSON (serialization) and JSON to validated models (deserialization).
- **ViewSets & Routers**: Consolidate complete CRUD operations into `viewsets.ModelViewSet` and map routes automatically using `DefaultRouter`.
- **Token Authentication**: Secure APIs by passing `Authorization: Token <key>` headers.

### 9. Automated Testing Framework
- **Test Sandboxing**: Subclass `django.test.TestCase` to execute each test method inside an atomic database transaction that is rolled back on completion.
- **Fixture Optimization**: Use `@classmethod def setUpTestData(cls):` to build shared database records once per test class.
- **Test Client**: Use `self.client` to simulate HTTP requests passing through middleware and URL dispatching without network overhead; use `force_login()` to accelerate authenticated testing.

### 10. Hardened Production Deployment
- **Two-Tier Architecture**: Reverse proxy (Nginx) terminates SSL, buffers requests, and serves static/media files; WSGI server (Gunicorn) executes Python workers (`(2 * CPU) + 1`).
- **Security Verification**: Run `python manage.py check --deploy`.
- **Production Checklist**: `DEBUG = False`, externalize `SECRET_KEY`, set strict `ALLOWED_HOSTS`, enable `SECURE_SSL_REDIRECT`, and enforce `SESSION_COOKIE_SECURE` and `CSRF_COOKIE_SECURE`.

---

## Chapter Index

| Chapter | Title | Key Frameworks & Topics |
|---|---|---|
| [ch01](chapters/ch01-introduction-to-django.md) | Introduction to Django | MVT paradigm, Request-response lifecycle, `manage.py`, settings, QueryDict |
| [ch02](chapters/ch02-models-and-migrations.md) | Models & Migrations | ORM, Field types, Relationships, `makemigrations`/`migrate`, Q objects, bulk ops |
| [ch03](chapters/ch03-views-urls-and-templates.md) | Views, URLs & Templates | Path converters, reverse resolution, FBVs, `get_object_or_404`, DTL inheritance |
| [ch04](chapters/ch04-introduction-to-django-admin.md) | Introduction to Admin | `ModelAdmin`, `list_display`, `list_filter`, `search_fields`, `fieldsets`, superusers |
| [ch05](chapters/ch05-serving-static-files.md) | Serving Static Files | `STATIC_URL`, `STATIC_ROOT`, `STATICFILES_DIRS`, `collectstatic`, Manifest storage |
| [ch06](chapters/ch06-forms.md) | Forms | `forms.Form`, GET vs POST, CSRF protection, bound/unbound forms, `cleaned_data` |
| [ch07](chapters/ch07-advanced-form-validation-and-modelforms.md) | Validation & ModelForms | 3-tier validation (`clean_<field>`, `clean`), `ModelForm`, `commit=False`, `save_m2m` |
| [ch08](chapters/ch08-media-serving-and-file-uploads.md) | Media & File Uploads | `MEDIA_ROOT`, `MEDIA_URL`, `multipart/form-data`, `request.FILES`, `ImageField` |
| [ch09](chapters/ch09-sessions-and-authentication.md) | Sessions & Authentication | Middleware pipeline, `authenticate()`, `login()`, `@login_required`, session engines |
| [ch10](chapters/ch10-advanced-django-admin-and-customizations.md) | Advanced Admin & Identity | `AUTH_USER_MODEL`, `TabularInline`, `StackedInline`, Admin Actions, custom views |
| [ch11](chapters/ch11-advanced-templating-and-class-based-views.md) | Advanced CBVs & Tags | Generic CBVs (`ListView`, `DetailView`), Mixin MRO, custom filters & inclusion tags |
| [ch12](chapters/ch12-building-a-rest-api.md) | Building a REST API | DRF, `ModelSerializer`, `ModelViewSet`, `DefaultRouter`, `TokenAuthentication` |
| [ch13](chapters/ch13-generating-csv-pdf-and-binary-files.md) | Binary Files & Exports | `io.BytesIO`, CSV streaming, Excel (`xlsxwriter`), PDF (`WeasyPrint`), Content-Disposition |
| [ch14](chapters/ch14-testing-your-django-applications.md) | Testing Applications | `TestCase`, `SimpleTestCase`, `setUpTestData`, Test Client, `RequestFactory`, assertions |
| [ch15](chapters/ch15-deploying-a-django-project.md) | Deploying a Project | Gunicorn, Nginx, WhiteNoise, `check --deploy`, Docker, production security headers |

---

## Topic Index

- **Admin Actions** → [ch10](chapters/ch10-advanced-django-admin-and-customizations.md)
- **Admin Customization (`ModelAdmin`)** → [ch04](chapters/ch04-introduction-to-django-admin.md), [ch10](chapters/ch10-advanced-django-admin-and-customizations.md)
- **ASGI & Asynchronous Views** → [ch15](chapters/ch15-deploying-a-django-project.md)
- **Authentication & Users** → [ch09](chapters/ch09-sessions-and-authentication.md), [ch10](chapters/ch10-advanced-django-admin-and-customizations.md)
- **Binary Exports (CSV, PDF, Excel)** → [ch13](chapters/ch13-generating-csv-pdf-and-binary-files.md)
- **Bulk Operations (`bulk_create`, `bulk_update`)** → [ch02](chapters/ch02-models-and-migrations.md)
- **Class-Based Views (CBVs)** → [ch03](chapters/ch03-views-urls-and-templates.md), [ch11](chapters/ch11-advanced-templating-and-class-based-views.md)
- **CSRF Protection** → [ch06](chapters/ch06-forms.md)
- **Custom User Models (`AUTH_USER_MODEL`)** → [ch10](chapters/ch10-advanced-django-admin-and-customizations.md)
- **Deployment & Security Hardening** → [ch15](chapters/ch15-deploying-a-django-project.md)
- **Django REST Framework (DRF)** → [ch12](chapters/ch12-building-a-rest-api.md)
- **Docker Containerization** → [ch15](chapters/ch15-deploying-a-django-project.md)
- **DTL (Template Inheritance & Filters)** → [ch01](chapters/ch01-introduction-to-django.md), [ch03](chapters/ch03-views-urls-and-templates.md), [ch11](chapters/ch11-advanced-templating-and-class-based-views.md)
- **Field Lookups & Q Objects** → [ch02](chapters/ch02-models-and-migrations.md)
- **File & Image Uploads (`request.FILES`)** → [ch08](chapters/ch08-media-serving-and-file-uploads.md)
- **Forms & Validation** → [ch06](chapters/ch06-forms.md), [ch07](chapters/ch07-advanced-form-validation-and-modelforms.md)
- **Gunicorn & Reverse Proxy** → [ch15](chapters/ch15-deploying-a-django-project.md)
- **Inlines (`TabularInline`, `StackedInline`)** → [ch10](chapters/ch10-advanced-django-admin-and-customizations.md)
- **Media Files (`MEDIA_ROOT`, `MEDIA_URL`)** → [ch08](chapters/ch08-media-serving-and-file-uploads.md)
- **Middleware Pipeline** → [ch09](chapters/ch09-sessions-and-authentication.md)
- **Migrations (`makemigrations`, `migrate`)** → [ch02](chapters/ch02-models-and-migrations.md)
- **ModelForms** → [ch07](chapters/ch07-advanced-form-validation-and-modelforms.md)
- **Models & Relationships (ORM)** → [ch02](chapters/ch02-models-and-migrations.md)
- **MVT Architecture** → [ch01](chapters/ch01-introduction-to-django.md)
- **N+1 Query Optimization (`select_related`)** → [ch02](chapters/ch02-models-and-migrations.md)
- **Pagination (`ListView`, DRF)** → [ch11](chapters/ch11-advanced-templating-and-class-based-views.md), [ch12](chapters/ch12-building-a-rest-api.md)
- **Post/Redirect/Get (PRG)** → [ch06](chapters/ch06-forms.md)
- **QueryDict Parameters** → [ch01](chapters/ch01-introduction-to-django.md), [ch06](chapters/ch06-forms.md)
- **RequestFactory** → [ch14](chapters/ch14-testing-your-django-applications.md)
- **Serializers & ViewSets** → [ch12](chapters/ch12-building-a-rest-api.md)
- **Sessions & Cookies** → [ch09](chapters/ch09-sessions-and-authentication.md)
- **Static Files (`STATIC_ROOT`, `collectstatic`)** → [ch05](chapters/ch05-serving-static-files.md)
- **Template Tags & Inclusion Tags** → [ch11](chapters/ch11-advanced-templating-and-class-based-views.md)
- **Testing (`TestCase`, `setUpTestData`)** → [ch14](chapters/ch14-testing-your-django-applications.md)
- **Token Authentication** → [ch12](chapters/ch12-building-a-rest-api.md)
- **URL Configuration & Reverse Resolution** → [ch03](chapters/ch03-views-urls-and-templates.md)
- **WhiteNoise** → [ch05](chapters/ch05-serving-static-files.md), [ch15](chapters/ch15-deploying-a-django-project.md)

---

## Supporting Files

- [glossary.md](glossary.md) — Alphabetical glossary defining key Django, ORM, REST, and deployment terms with chapter citations.
- [patterns.md](patterns.md) — Comprehensive pattern catalog detailing When to use, How to implement, and Trade-offs for 10 core Django patterns.
- [cheatsheet.md](cheatsheet.md) — High-density decision guide featuring "When X, do Y, because Z" rules, view selection decision trees, operational thresholds, and diagnostic smells.

---

## Scope & Limits

This skill covers the web development practices, architectural patterns, and security guidelines presented in *Web Development with Django 6* (Packt Publishing). It provides practical implementation recipes and configuration standards. For niche third-party extensions, custom Wagtail CMS setups, or distributed Celery task worker architectures, refer to the respective package documentation.
