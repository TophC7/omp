# Chapter 5: Serving Static Files

## Core Idea
Django's `staticfiles` application manages frontend assets (CSS, JavaScript, images) across modular app directories during development and consolidates them into a single production-ready directory via `collectstatic` for high-performance web server or CDN delivery.

## Frameworks Introduced
- **The Static Files App & Lifecycle (`django.contrib.staticfiles`)**:
  - *Development Mode (`DEBUG = True`)*: The development server automatically intercepts requests matching `STATIC_URL` and serves assets dynamically from app and project directories.
  - *Production Mode (`DEBUG = False`)*: Django refuses to serve static files directly to prevent blocking Python worker threads; assets must be compiled to `STATIC_ROOT` and served by a reverse proxy (Nginx), CDN (S3/Cloudflare), or middleware (WhiteNoise).
  - When to use: Across every web application delivering stylesheets, frontend scripts, fonts, and theme icons.
  - How: Define `STATIC_URL`, `STATICFILES_DIRS`, and `STATIC_ROOT` in `settings.py`, and link assets in templates using `{% load static %}` and `{% static %}`.
  - Why it works: Allows developers to organize static assets alongside their corresponding modular apps without manually copying files during development.
  - Failure mode: Relying on Django's built-in development view to serve static files in production.

- **Static File Finders Pipeline (`STATICFILES_FINDERS`)**:
  - Plugin architecture responsible for locating assets on disk given a relative URL path:
    1. `AppDirectoriesFinder`: Searches for files in `<app>/static/<app>/` across all registered `INSTALLED_APPS`.
    2. `FileSystemFinder`: Searches project-level directories listed in `STATICFILES_DIRS`.
  - Finder resolution is executed during request handling (dev), running `findstatic`, and executing `collectstatic`.

- **Cache Busting & Storage Engines (`ManifestStaticFilesStorage`)**:
  - Automatically appends MD5 hashes of file contents to filenames (e.g. `css/style.a1b2c3d4.css`).
  - Allows web servers and CDNs to serve assets with infinite `Cache-Control: max-age=31536000, immutable` headers.
  - When a stylesheet is edited, its hash changes, automatically forcing client browsers to download the fresh asset.

## Key Concepts
- **Static Assets**: Fixed files (CSS, JS, fonts, brand logos) authored by developers and deployed as part of the codebase.
- **Media Files**: User-uploaded files (profile photos, document attachments) created at runtime (covered in Chapter 8).
- **`STATIC_URL`**: The public URL prefix prepended to all static asset links (e.g., `"/static/"`).
- **`STATICFILES_DIRS`**: List of filesystem paths where project-wide assets live outside modular app folders (e.g., `[BASE_DIR / "static"]`).
- **`STATIC_ROOT`**: The absolute destination directory where `python manage.py collectstatic` dumps all collected assets for production deployment.
- **`collectstatic`**: Management command that queries finders, copies files into `STATIC_ROOT`, and calculates manifest hashes.
- **`findstatic`**: Diagnostic CLI tool pinpointing the exact filesystem path from which an asset is being resolved.

## Mental Models
- **The Postal Collection and Distribution**: During development, each app writes letters into its local static mailbox; running `collectstatic` is the postal truck gathering every letter from every mailbox into a central sorting warehouse (`STATIC_ROOT`) for distribution.
- **The Hash Stamp for Caching**: Hashing asset contents turns filenames into immutable fingerprints; browsers never have to ask "has this file changed?" because any change produces a completely new filename.
- **Namespacing Static Assets**: Always nest static assets inside `<app>/static/<app>/` (e.g., `reviews/static/reviews/logo.png`) to prevent app asset collision, exactly like template namespacing.

## Anti-patterns
- **Setting `STATIC_ROOT` to a Directory Inside `STATICFILES_DIRS`**: Setting `STATIC_ROOT = BASE_DIR / 'static'` while `STATICFILES_DIRS = [BASE_DIR / 'static']` causes `collectstatic` to attempt copying a directory into itself, raising `CommandError`.
- **Hardcoding `/static/` Paths in HTML**: Writing `<link href="/static/style.css">` instead of `{% static 'reviews/style.css' %}`. This breaks if `STATIC_URL` changes or when switching to CDN storage.
- **Attempting to Serve Media via `STATICFILES_DIRS`**: Mixing user-uploaded uploads with developer-authored static files; media files must use `MEDIA_ROOT` and `MEDIA_URL`.
- **Neglecting Cache Invalidation**: Deploying CSS updates with plain filenames under long cache headers, causing return visitors to render broken layouts with stale stylesheets.

## Code Examples

### Complete Static Settings Configuration

```python
# bookr/settings.py
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# 1. Base URL prefix for static links
STATIC_URL = "/static/"

# 2. Project-level static directory (for global theme/CSS)
STATICFILES_DIRS = [
    BASE_DIR / "static",
    # Prefixed mode (optional namespace)
    ("vendor", BASE_DIR / "vendor_assets"),
]

# 3. Target directory for production compilation (collectstatic)
STATIC_ROOT = BASE_DIR / "staticfiles"

# 4. Storage engine with automatic cache-busting
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.ManifestStaticFilesStorage",
    },
}
```
- **What it demonstrates**: Configuring URL prefixes, source directories, collection targets, and manifest hashing.

### Template Integration

```html
<!-- reviews/templates/reviews/base.html -->
{% load static %}
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{% block title %}Bookr{% endblock %}</title>
    <!-- Resolves to /static/reviews/css/main.a1b2c3.css in production -->
    <link rel="stylesheet" href="{% static 'reviews/css/main.css' %}">
</head>
<body>
    <header>
        <img src="{% static 'reviews/images/logo.png' %}" alt="Bookr Logo" width="120">
    </header>
    <main>
        {% block content %}{% endblock %}
    </main>
    <script src="{% static 'reviews/js/app.js' %}" defer></script>
</body>
</html>
```
- **What it demonstrates**: Using `{% load static %}` and `{% static %}` to output hash-aware URLs.

### Debugging with findstatic & collectstatic

```bash
# Locate which disk path supplies an asset
python manage.py findstatic reviews/css/main.css
# Output: Found 'reviews/css/main.css' here:
#   /home/user/bookr/reviews/static/reviews/css/main.css

# Compile assets for production deployment
python manage.py collectstatic --no-input
# Output: 142 static files copied to '/home/user/bookr/staticfiles', 142 post-processed.
```
- **What it demonstrates**: Diagnosing asset resolution and preparing deployment bundles.

## Reference Tables

### Static Settings Comparison Matrix

| Setting | Type | Purpose | Production Role |
|---|---|---|---|
| `STATIC_URL` | `str` | Public URL prefix (`"/static/"` or CDN URL) | Base URL injected by `{% static %}` |
| `STATICFILES_DIRS` | `list[Path]` | Extra directories containing authored assets | Read by finders and `collectstatic` |
| `STATIC_ROOT` | `Path` | Directory where all assets are gathered | Pointed to by Nginx or WhiteNoise |
| `STATICFILES_FINDERS`| `list[str]` | Classes used to discover assets on disk | Locates files across apps & project dirs |

### Built-in Static Finders

| Finder Class | Search Path Target | Use Case |
|---|---|---|
| `AppDirectoriesFinder` | `<app>/static/` | Modular assets tied to specific Django apps |
| `FileSystemFinder` | `STATICFILES_DIRS` paths | Global branding, vendor JS, site-wide themes |

## Worked Example

### Styling the Bookr Application

1. Create modular stylesheet inside app directory:
   `reviews/static/reviews/css/main.css`
   ```css
   body { font-family: sans-serif; margin: 2rem; background: #f9f9f9; }
   nav { background: #333; padding: 1rem; color: #fff; }
   nav a { color: #fff; text-decoration: none; margin-right: 1rem; }
   .review-card { background: #fff; border: 1px solid #ddd; padding: 1rem; margin-bottom: 1rem; border-radius: 4px; }
   ```
2. Place logo in project-level static directory:
   `static/images/logo.png`
3. Configure `STATICFILES_DIRS = [BASE_DIR / "static"]` in `settings.py`.
4. In `reviews/templates/reviews/base.html`:
   ```html
   {% load static %}
   <link rel="stylesheet" href="{% static 'reviews/css/main.css' %}">
   <img src="{% static 'images/logo.png' %}" alt="Logo">
   ```
5. Test in development: navigate to `http://127.0.0.1:8000/books/`. Page renders with CSS styling and logo.
6. Verify resolution:
   `python manage.py findstatic reviews/css/main.css` confirms path.

## Key Takeaways
1. Never serve static files through standard Django views in production; rely on Nginx, CDNs, or WhiteNoise.
2. Store app-specific assets in `<app>/static/<app>/` and site-wide assets in `STATICFILES_DIRS`.
3. Reference all static assets in templates via `{% load static %}` and the `{% static %}` tag.
4. `STATIC_ROOT` is strictly the destination directory populated by `python manage.py collectstatic`.
5. Use `ManifestStaticFilesStorage` in production to append content hashes to filenames, enabling aggressive and safe browser caching.

## Connects To
- **Ch 01**: Introduction to Django — where basic template rendering begins.
- **Ch 08**: Media Serving and File Uploads — contrasting developer-authored static assets with dynamic user uploads.
- **Ch 15**: Deploying a Django Project — configuring Nginx, WhiteNoise, and production static pipelines.
