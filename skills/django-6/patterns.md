# Web Development with Django 6 — Patterns Reference

## Model-View-Template (MVT) Pattern
**When to use**: For structuring every standard Django application to cleanly separate data models, request orchestration, and presentation layout.
**How**:
1. Define entities and schema constraints in `models.py` by subclassing `models.Model`.
2. Write request-processing and database queries in `views.py` using function-based views or class-based views.
3. Define layout and visual markup in HTML templates using Django Template Language (DTL).
4. Connect URL routes to views using `path()` in `urls.py`.
**Trade-offs**:
- *Pros*: Strict separation of concerns; templates cannot execute arbitrary database mutations; models remain presentation-agnostic.
- *Cons*: For single-page applications (SPAs) or pure API backends, the Template layer is bypassed in favor of JSON serializers.

## Post/Redirect/Get (PRG) Pattern
**When to use**: Whenever handling state-changing HTML form submissions (POST requests) in web views.
**How**:
1. In the view, inspect `request.method == "POST"`.
2. Bind the form (`form = MyForm(request.POST)`).
3. If valid, save the data or execute the action.
4. Immediately return an HTTP redirect (`return redirect("target_view", pk=obj.pk)`).
5. If invalid, fall through to re-render the form template with validation errors.
**Trade-offs**:
- *Pros*: Prevents accidental duplicate form submissions and double-charges when users refresh the browser after submitting.
- *Cons*: Requires temporary flash messaging (`messages` framework) to display success notifications across the redirect boundary.

## Three-Tier Form Validation Pipeline
**When to use**: For validating and sanitizing user inputs across varying degrees of field isolation and cross-field interdependency.
**How**:
1. *Tier 1 (Validators)*: Add reusable validator functions (`validators=[validate_isbn]`) to individual field constructors.
2. *Tier 2 (Field Cleaning)*: Implement `def clean_<fieldname>(self):` on the `Form` class to normalize single values (must return value).
3. *Tier 3 (Multi-field Cleaning)*: Implement `def clean(self):` to evaluate cross-field dependencies, calling `self.add_error("field", msg)` or raising `ValidationError` (must return `cleaned_data`).
**Trade-offs**:
- *Pros*: Reusable logic; errors attach directly to the responsible form fields; invalid forms re-render automatically.
- *Cons*: Requires understanding Django's strict execution order; forgetting to return values in `clean_<field>` overwrites data with `None`.

## ModelForm Persistence with `commit=False`
**When to use**: When saving a form that creates or updates a model instance, but extra attributes (such as the logged-in user or an audit IP) must be attached before database insertion.
**How**:
1. Call `instance = form.save(commit=False)` to obtain an in-memory model object populated with validated form data.
2. Set extra model attributes: `instance.author = request.user`.
3. Save the model instance explicitly: `instance.save()`.
4. If the form contains many-to-many fields, explicitly invoke `form.save_m2m()`.
**Trade-offs**:
- *Pros*: Avoids exposing hidden or administrative form fields to the user; securely sets server-side attributes.
- *Cons*: Forgetting to call `form.save_m2m()` silently drops all selected many-to-many junction records.

## QuerySet Optimization (`select_related` and `prefetch_related`)
**When to use**: Whenever accessing related model instances across relationships in views, templates, or serializers to prevent N+1 query bottlenecks.
**How**:
1. Use `.select_related("foreign_key_field")` for single-valued relationships (ForeignKey, OneToOne) to generate an SQL `INNER JOIN` or `LEFT OUTER JOIN` in a single query.
2. Use `.prefetch_related("m2m_field")` for multi-valued relationships (ManyToManyField, reverse ForeignKey) to execute a secondary batched `WHERE IN` query and join in Python memory.
**Trade-offs**:
- *Pros*: Reduces database queries from hundreds down to 1 or 2; dramatically improves page response latency.
- *Cons*: Over-fetching deeply nested relationships with `select_related` can result in massive SQL join result sets that consume high memory.

## Generic Class-Based View Assembly with Mixins
**When to use**: For rapidly implementing standard CRUD endpoints with built-in pagination, form handling, and authentication.
**How**:
1. Inherit from generic base classes (`ListView`, `DetailView`, `CreateView`, `UpdateView`).
2. Add behavior mixins (`LoginRequiredMixin`, `PermissionRequiredMixin`) strictly to the *left* of the generic view class (MRO order).
3. Override hook methods (`get_queryset()`, `get_context_data()`, `form_valid()`) for customization.
**Trade-offs**:
- *Pros*: Reduces 50 lines of procedural view logic to 5 lines of declarative class attributes; standardized behavior.
- *Cons*: Complex inheritance chains can be harder to debug for developers unfamiliar with Django's internal class hierarchy.

## In-Memory Binary File Streaming (`io.BytesIO`)
**When to use**: When generating dynamic binary payloads (PDF invoices, Excel reports, ZIP archives, charts) for user download.
**How**:
1. Allocate an in-memory byte buffer: `buffer = io.BytesIO()`.
2. Pass `buffer` to the file-writing library (`xlsxwriter.Workbook(buffer)` or `weasyprint.HTML(...).write_pdf()`).
3. Finalize and close the writer.
4. Construct an `HttpResponse(buffer.getvalue(), content_type=...)` with a `Content-Disposition: attachment; filename="..."` header.
**Trade-offs**:
- *Pros*: Zero filesystem disk I/O; no temporary file leaks, permission conflicts, or disk-filling attacks.
- *Cons*: Entire binary file must fit in server RAM during generation; for massive multi-gigabyte exports, use `StreamingHttpResponse` with generators.

## ViewSet & Router Architecture (DRF)
**When to use**: When exposing a complete RESTful CRUD API for an application's database models to mobile clients or frontend SPAs.
**How**:
1. Define a `ModelSerializer` specifying model and fields.
2. Define a `ModelViewSet` declaring `queryset = Model.objects.all()` and `serializer_class = MySerializer`.
3. Register the ViewSet with a `DefaultRouter` in `urls.py`: `router.register("items", ItemViewSet)`.
**Trade-offs**:
- *Pros*: Automatically provides standard REST routes, pagination, sorting, search, and browsable HTML API testing interface.
- *Cons*: Can be overly opinionated if the API does not follow standard REST resource conventions.

## Transactional Test Sandboxing with `setUpTestData`
**When to use**: In automated test suites to ensure fast, isolated unit and integration testing without database pollution.
**How**:
1. Subclass `django.test.TestCase`.
2. Create shared, immutable database records inside `@classmethod def setUpTestData(cls):`.
3. Allow each test method to run inside an automatic database transaction rollback sandbox.
**Trade-offs**:
- *Pros*: Extremely fast database tests; records created in `setUpTestData` are constructed once per test class rather than per method.
- *Cons*: Mutating test data inside test methods can leak state across tests if not carefully isolated or restored.

## Two-Tier Production Server Architecture
**When to use**: For deploying Django applications reliably under concurrent production traffic.
**How**:
1. Deploy an application server (Gunicorn) running a pre-fork worker pool executing `project.wsgi:application`.
2. Place a reverse proxy (Nginx) in front of Gunicorn to handle SSL termination, request buffering, and direct static/media file serving.
3. Alternatively, install WhiteNoise middleware to allow Gunicorn to serve compressed, hash-cached static assets directly in containerized setups.
**Trade-offs**:
- *Pros*: Resilient multi-process worker model; Nginx and WhiteNoise protect Python processes from slow static asset requests.
- *Cons*: More complex operational setup than running the local development server.
