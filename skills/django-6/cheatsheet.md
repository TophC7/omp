# Web Development with Django 6 — Cheatsheet & Decision Guide

## 1. Core Decision Rules

- **When modeling relationships**:
  - Use `ForeignKey(..., on_delete=models.CASCADE)` for child data that has no meaning without the parent (e.g., `Review` belonging to `Book`).
  - Use `ForeignKey(..., on_delete=models.PROTECT)` for critical master records that must never be accidentally wiped out by parent deletion (e.g., `Publisher`).
  - Use `ManyToManyField(..., through="JunctionModel")` whenever relationship metadata (role, date, order) must be recorded on the link itself.
- **When querying related objects**:
  - Always use `.select_related()` for `ForeignKey` and `OneToOne` relationships to execute an SQL `JOIN` in a single query.
  - Always use `.prefetch_related()` for `ManyToManyField` and reverse foreign key lookups to execute a batched `IN` query.
- **When designing view endpoints**:
  - Use **Function-Based Views (FBVs)** for highly custom, procedural, or unique algorithmic logic.
  - Use **Generic Class-Based Views (CBVs)** (`ListView`, `DetailView`, `CreateView`) for standard CRUD operations to eliminate repetitive boilerplate.
  - Mixins must always precede generic views in inheritance declarations (left-to-right MRO order: `class MyView(LoginRequiredMixin, ListView)`).
- **When handling forms**:
  - Always implement the **Post/Redirect/Get (PRG)** pattern for POST requests to prevent double form submission on page refresh.
  - In `clean_<fieldname>()`, always **return the cleaned value** at the end of the method; forgetting to return will overwrite data with `None`.
  - When saving forms with uncommitted instances (`form.save(commit=False)`), always call `form.save_m2m()` after saving the instance to preserve many-to-many links.
- **When handling file uploads**:
  - Forms must declare `enctype="multipart/form-data"` or the browser will silently drop the binary file stream.
  - Views must pass `request.FILES` to the form: `form = MyForm(request.POST, request.FILES)`.
  - Never share the same directory for `MEDIA_ROOT` and `STATIC_ROOT`.
- **When preparing for production deployment**:
  - Always run `python manage.py check --deploy` and set `DEBUG = False`.
  - Externalize all secrets (`SECRET_KEY`, `DATABASE_URL`) into environment variables using `python-decouple`.
  - Set `ALLOWED_HOSTS` strictly to production domain names; never use wildcard `['*']`.

---

## 2. Decision Tree: Choosing the Right View Component

```text
What type of endpoint are you building?
│
├── REST API Endpoint returning JSON?
│   ├── Standard CRUD over a Model? ──────────────► ModelViewSet + DefaultRouter (DRF)
│   ├── Read-only or single custom query? ────────► ListAPIView / APIView (DRF)
│   └── Quick lightweight endpoint? ──────────────► @api_view(['GET', 'POST'])
│
├── HTML Web Page returning Templates?
│   ├── Static informational page? ───────────────► TemplateView
│   ├── Listing a paginated collection? ──────────► ListView (override get_queryset)
│   ├── Viewing a single instance by PK/Slug? ────► DetailView
│   ├── Creating a new model record via form? ────► CreateView
│   ├── Updating an existing model record? ───────► UpdateView
│   └── Highly customized / multi-step logic? ────► Function-Based View (FBV)
│
└── Binary File Download?
    ├── Direct CSV export? ───────────────────────► HttpResponse(content_type="text/csv")
    ├── Large dataset (>10,000 rows)? ────────────► StreamingHttpResponse + iterator()
    └── Excel (.xlsx) / PDF / ZIP? ───────────────► io.BytesIO() buffer + HttpResponse
```

---

## 3. Trade-off Matrices

### Function-Based Views (FBV) vs. Class-Based Views (CBV)

| Dimension | Function-Based Views (FBVs) | Class-Based Views (CBVs) |
|---|---|---|
| **Readability** | High; explicit top-to-bottom procedural flow | Moderate; implicit behavior hidden in base classes |
| **Code Reuse** | Low; logic copied across similar views | High; reusable via inheritance and mixins |
| **HTTP Verb Handling** | `if request.method == "POST":` branches | Separate `get()`, `post()` class methods |
| **Best Used For** | Complex custom workflows, multi-step actions | Standard CRUD, list/detail views, generic forms |

### Session Storage Engine Comparison

| Engine (`SESSION_ENGINE`) | Speed | Scalability | Persistence | Best Used For |
|---|---|---|---|---|
| `backends.db` | Moderate | Moderate (DB load) | High (durable) | Standard sites with low-to-medium traffic |
| `backends.cache` | Instant | High (Redis) | Low (volatile) | Ephemeral sessions with independent Redis store |
| `backends.cached_db` | High | High | High (write-through) | High-traffic production deployments |
| `backends.signed_cookies`| Instant | Infinite (zero server RAM)| Client-bound | Stateless server setups; strictly <4KB data |

---

## 4. Thresholds & Operational Defaults

- **Gunicorn Worker Formula**: `workers = (2 * CPU_CORES) + 1` (e.g. 2 cores → 5 workers).
- **Session Cookie Lifetime**: Default is 2 weeks (1,209,600 seconds). Set `SESSION_COOKIE_AGE` or use `request.session.set_expiry(0)` for browser-close expiration.
- **HSTS Header Duration**: Set `SECURE_HSTS_SECONDS = 31536000` (1 year) in production after verifying HTTPS.
- **File Upload Chunk Size**: Files under 2.5MB (`FILE_UPLOAD_MAX_MEMORY_SIZE`) are held in memory (`InMemoryUploadedFile`); larger files stream to disk (`TemporaryUploadedFile`).
- **Database Query Pagination**: Never render unpaginated model collections; always declare `paginate_by = 10` or `25` on `ListView` and DRF pagination classes.

---

## 5. Tells & Smells (Diagnostic Heuristics)

| Codebase Smell | Diagnostic Tell | Prescribed Remedy |
|---|---|---|
| **Django Debug Toolbar shows 100+ SQL queries** | N+1 query problem inside a template loop | Add `.select_related()` (FK) or `.prefetch_related()` (M2M) to the view's queryset. |
| **HTTP 403 Forbidden on form submit** | Missing CSRF token in POST request | Add `{% csrf_token %}` inside `<form method="post">`. |
| **Form validates, but file is not uploaded** | Form missing binary multipart encoding | Add `enctype="multipart/form-data"` to the HTML `<form>` element. |
| **View crashes with `AttributeError` on `cleaned_data`** | Attempting to access data before validation | Always call `if form.is_valid():` before accessing `form.cleaned_data`. |
| **Template loads wrong app's layout** | Template naming collision across apps | Always namespace templates in `<app>/templates/<app>/layout.html`. |
| **Unit test database setup takes 30 seconds** | Database fixtures re-inserted for every test | Move model setup from `setUp()` to `@classmethod def setUpTestData(cls):`. |
| **`collectstatic` errors with directory overlap** | `STATIC_ROOT` placed inside `STATICFILES_DIRS` | Ensure `STATIC_ROOT` points to an isolated target directory outside source folders. |
| **`check --deploy` reports W006, W008, W012** | Insecure production cookie/SSL settings | Set `SESSION_COOKIE_SECURE = True`, `CSRF_COOKIE_SECURE = True`, and `SECURE_SSL_REDIRECT = True`. |
