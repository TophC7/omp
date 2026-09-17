# Chapter 8: Media Serving and File Uploads

## Core Idea
Media files represent dynamic user-uploaded content (images, PDFs, documents) stored at runtime; Django handles them through distinct filesystem storage locations (`MEDIA_ROOT`), multipart form streaming (`request.FILES`), and database integration via `FileField` and `ImageField`.

## Frameworks Introduced
- **Media Settings & Development Serving**:
  - *Storage Configuration*:
    - `MEDIA_ROOT`: Absolute filesystem directory where uploaded files are permanently saved (e.g., `BASE_DIR / "media"`).
    - `MEDIA_URL`: Public URL prefix used to serve uploaded files (e.g., `"/media/"`).
    - *Security Invariant*: `MEDIA_ROOT` and `STATIC_ROOT` must **never** point to the same directory, and `MEDIA_URL` must not equal `STATIC_URL`. Sharing directories allows users to upload malicious `.js` or `.css` files that overwrite application code.
  - *Development Routing*: Django does not serve media automatically. In development only, append the helper route:
    `if settings.DEBUG: urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)`

- **Multipart Form Uploads & `request.FILES`**:
  - Standard HTML forms cannot transmit binary file streams under default encoding (`application/x-www-form-urlencoded`).
  - Forms uploading files must declare `enctype="multipart/form-data"`.
  - In views, file payloads bypass `request.POST` entirely and are parsed into `request.FILES`.
  - When binding forms with files: `form = BookForm(request.POST, request.FILES)`.

- **`FileField` & `ImageField` ORM Primitives**:
  - `models.FileField`: Stores the file in the designated storage backend and records the relative path string in the database column.
  - `models.ImageField`: Subclass of `FileField` that validates that the uploaded file is a valid image using the `Pillow` library, storing dimensions (`height_field`, `width_field`).
  - `upload_to`: Attribute defining subdirectory path. Accepts either:
    - A formatted string: `upload_to="book_covers/%Y/%m/"` (subdivides files by year/month).
    - A callable: `def book_directory_path(instance, filename): return f"books/{instance.isbn}/{filename}"`.

- **The `FieldFile` API**:
  - Accessing a model's file field returns a `FieldFile` proxy instance providing rich file inspection methods:
    - `.url`: Public URL for HTML tags (`<img src="{{ book.cover.url }}">`).
    - `.path`: Absolute filesystem path on disk (`/var/www/media/covers/pic.jpg`).
    - `.name`: Storage-relative path (`"covers/pic.jpg"`).
    - `.size`: File size in bytes.
    - `.delete(save=True)`: Removes the file from physical storage.

## Key Concepts
- **Media Files**: User-uploaded or dynamically generated binary assets created after application deployment.
- **`multipart/form-data`**: MIME encoding standard required to transmit binary byte streams over HTTP POST.
- **`request.FILES`**: A multi-value dictionary containing `UploadedFile` objects (`InMemoryUploadedFile` for small files, `TemporaryUploadedFile` for files >2.5MB).
- **Pillow**: Required Python imaging library (`pip install Pillow`) powering Django's `ImageField` validation.
- **`upload_to` Callable**: Function taking `(instance, filename)` to dynamically construct unique, collision-resistant storage paths.

## Mental Models
- **The Warehouse vs. The Showroom**: Static files are the showroom furnishings (built into the architecture by the architect); Media files are goods delivered to the loading dock by customers every day (stored in the warehouse, tracked by inventory tags).
- **The Two-Stream Intake**: When a multipart form arrives, text data flows into the `request.POST` stream; file byte streams flow into the `request.FILES` stream. If you don't connect `request.FILES` to your form, the files evaporate.
- **Database Pointer, Disk Payload**: The database table never stores binary file blobs; it stores a lightweight string path pointing to a file sitting on disk or an S3 bucket.

## Anti-patterns
- **Omitting `enctype="multipart/form-data"` on Forms**: Creating an upload form with `<form method="post">` without the enctype attribute. The browser only sends the filename as text, silently dropping the actual file contents.
- **Forgetting `request.FILES` in Views**: Writing `form = DocumentForm(request.POST)` instead of `form = DocumentForm(request.POST, request.FILES)`. The form fails validation with "This field is required".
- **Serving Media through Django in Production**: Leaving `urlpatterns += static(...)` active in production. Web workers will block serving large image and video downloads instead of handling dynamic Python requests.
- **Unsanitized File Uploads in Public Directories**: Permitting users to upload arbitrary executable scripts (`.php`, `.py`, `.html`) directly into web-executable web server directories.

## Code Examples

### Configuring Media Settings and Dynamic `upload_to`

```python
# bookr/settings.py
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

MEDIA_ROOT = BASE_DIR / "media"
MEDIA_URL = "/media/"
```

Model with `upload_to` callable and `ImageField`:
```python
# reviews/models.py
from django.db import models

def book_cover_path(instance: "Book", filename: str) -> str:
    # Save files to media/book_covers/<isbn>/<filename>
    return f"book_covers/{instance.isbn}/{filename}"

class Book(models.Model):
    title = models.CharField(max_length=100)
    isbn = models.CharField(max_length=20)
    cover = models.ImageField(upload_to=book_cover_path, blank=True, null=True)
    sample_pdf = models.FileField(upload_to="book_samples/", blank=True, null=True)

    def __str__(self) -> str:
        return self.title
```
- **What it demonstrates**: Dynamic partition path construction and optional image/file storage.

### ModelForm and View Handling File Uploads

Form definition:
```python
# reviews/forms.py
from django import forms
from .models import Book

class BookMediaForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ("cover", "sample_pdf")
```

View implementation handling `request.FILES`:
```python
# reviews/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpRequest, HttpResponse
from .models import Book
from .forms import BookMediaForm

def book_media_upload(request: HttpRequest, pk: int) -> HttpResponse:
    book = get_object_or_404(Book, pk=pk)

    if request.method == "POST":
        # Pass BOTH request.POST and request.FILES
        form = BookMediaForm(request.POST, request.FILES, instance=book)
        if form.is_valid():
            form.save()
            return redirect("reviews:book_detail", pk=book.pk)
    else:
        form = BookMediaForm(instance=book)

    return render(request, "reviews/media_form.html", {"form": form, "book": book})
```
- **What it demonstrates**: Binding `request.FILES` to the ModelForm and updating existing instances.

### Template Rendering Media Files

```html
<!-- reviews/templates/reviews/book_detail.html -->
{% extends "reviews/base.html" %}

{% block content %}
    <h1>{{ book.title }}</h1>

    {% if book.cover %}
        <div class="book-cover">
            <img src="{{ book.cover.url }}" alt="{{ book.title }} cover" width="200">
        </div>
    {% else %}
        <p><em>No cover image available.</em></p>
    {% endif %}

    {% if book.sample_pdf %}
        <p>
            <a href="{{ book.sample_pdf.url }}" target="_blank" download>
                Download Sample Chapter ({{ book.sample_pdf.size|filesizeformat }})
            </a>
        </p>
    {% endif %}
{% endblock %}
```
- **What it demonstrates**: Checking for file existence before accessing `.url` and using the `filesizeformat` filter.

## Reference Tables

### Static Files vs. Media Files

| Feature | Static Files (`STATIC_*`) | Media Files (`MEDIA_*`) |
|---|---|---|
| **Origin** | Authored by developers in source control | Uploaded by users / generated at runtime |
| **Lifecycle** | Deployed with code releases | Persisted dynamically across releases |
| **Settings** | `STATIC_ROOT`, `STATIC_URL`, `STATICFILES_DIRS`| `MEDIA_ROOT`, `MEDIA_URL` |
| **Storage Separation** | Kept in app `static/` directories | Kept in durable object storage / media disk |
| **Security Risk** | Low (code reviewed) | High (arbitrary user binary uploads) |
| **Dev Serving** | Automatic via `staticfiles` | Manual route via `static(settings.MEDIA_URL, ...)` |

### Key `FieldFile` Properties & Methods

| Attribute / Method | Type | Description |
|---|---|---|
| `file.url` | `str` | Public web URL for frontend HTML rendering |
| `file.path` | `str` | Absolute local filesystem path on the host server |
| `file.name` | `str` | Storage-relative path string stored in the database |
| `file.size` | `int` | Total file size in bytes |
| `file.delete(save=True)`| `None` | Deletes file from disk and clears model attribute |

## Worked Example

### End-to-End Book Cover Upload

1. Ensure `Pillow` is installed in virtual environment:
   `pip install Pillow`
2. Add media settings to `bookr/settings.py`:
   `MEDIA_ROOT = BASE_DIR / "media"`
   `MEDIA_URL = "/media/"`
3. Add development URL route in `bookr/urls.py`:
   ```python
   from django.conf import settings
   from django.conf.urls.static import static

   urlpatterns = [...]
   if settings.DEBUG:
       urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
   ```
4. Render form in `media_form.html`:
   ```html
   <form method="post" enctype="multipart/form-data">
       {% csrf_token %}
       {{ form.as_div }}
       <button type="submit">Upload Media</button>
   </form>
   ```
5. Execution trace:
   - User selects `cover.png` and submits form.
   - Django uploads stream into `request.FILES["cover"]`.
   - `Pillow` validates image headers.
   - Django saves file to `media/book_covers/9781836202073/cover.png`.
   - Django writes `"book_covers/9781836202073/cover.png"` into the `reviews_book.cover` column.
   - Detail view renders `<img src="/media/book_covers/9781836202073/cover.png">`.

## Key Takeaways
1. Never mix `MEDIA_ROOT` and `STATIC_ROOT`; keeping them isolated prevents security exploits.
2. Any form uploading files must include `enctype="multipart/form-data"`.
3. View functions must pass `request.FILES` alongside `request.POST` when binding forms.
4. Use dynamic `upload_to` functions on `FileField`/`ImageField` to organize uploads into structured, collision-resistant subdirectories.
5. Always check `{% if model.file %}` before rendering `model.file.url` in templates to prevent `ValueError` exceptions when fields are blank.

## Connects To
- **Ch 02**: Models and Migrations — introducing `models.Model` where `FileField` and `ImageField` are defined.
- **Ch 05**: Serving Static Files — contrasting developer assets with dynamic user uploads.
- **Ch 07**: Advanced Form Validation and Model Forms — processing and validating uploaded file metadata in ModelForms.
