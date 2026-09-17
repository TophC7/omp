# Chapter 15: Deploying a Django Project

## Core Idea
Deploying Django to production requires splitting the monolithic development server into a high-concurrency two-tier architecture (reverse proxy and WSGI application server), externalizing secrets into environment variables, hardening security headers (`check --deploy`), and automating asset compilation.

## Frameworks Introduced
- **The Two-Tier Production Server Architecture**:
  - *Frontend Reverse Proxy (Nginx, Caddy, Cloudflare)*:
    - Receives public client traffic on ports 80/443.
    - Handles SSL/TLS termination, request buffering, rate limiting, and DDoS mitigation.
    - Serves static assets (`/static/`) and media files (`/media/`) directly from disk or CDN storage with zero Python overhead.
    - Forwards application requests to the WSGI server via Unix domain sockets or HTTP loopback (`127.0.0.1:8000`).
  - *WSGI Application Server (Gunicorn, uWSGI)*:
    - Pre-fork worker model: Spawns multiple worker processes based on available CPU cores (`workers = (2 * CPU) + 1`).
    - Executes the Django WSGI application callable (`bookr.wsgi:application`).
  - *ASGI Alternative (Uvicorn, Daphne)*: Used for asynchronous workloads, WebSockets, and real-time streaming connections.

- **The Django Security Checklist (`python manage.py check --deploy`)**:
  - Built-in audit tool inspecting active settings against security benchmarks:
    - `DEBUG = False`: Mandatory; prevents stack traces, source code snippets, and environment variables from leaking on error pages.
    - `SECRET_KEY`: Must be unique, secret, and loaded from external environment variables; never committed to version control.
    - `ALLOWED_HOSTS`: Explicit whitelist of valid domain names and IP addresses (`["bookr.com", "www.bookr.com"]`); prevents HTTP Host header poisoning attacks.
    - `SECURE_SSL_REDIRECT = True`: Enforces automatic HTTP to HTTPS redirection.
    - `SESSION_COOKIE_SECURE = True` & `CSRF_COOKIE_SECURE = True`: Instructs browsers to transmit cookies strictly over HTTPS connections.
    - `SECURE_HSTS_SECONDS = 31536000`: Enables HTTP Strict Transport Security (HSTS) forcing browsers to connect only via HTTPS.

- **Environment Externalization (`python-decouple` / `django-environ`)**:
  - Separates code from deployment configuration (Twelve-Factor App methodology).
  - Reads secrets and toggleable settings from `.env` files or container environment variables:
    `SECRET_KEY = config("SECRET_KEY")`
    `DEBUG = config("DEBUG", default=False, cast=bool)`

- **Standalone Static Serving with WhiteNoise**:
  - For containerized or PaaS environments without an Nginx reverse proxy, WhiteNoise middleware integrates into Gunicorn to serve static assets with gzip and Brotli compression, cache headers, and manifest support.

## Key Concepts
- **WSGI (Web Server Gateway Interface)**: Python standard (PEP 3333) defining communication between web servers and Python web applications.
- **Pre-fork Model**: Architecture where a master process starts and manages worker subprocesses to handle incoming concurrent HTTP requests.
- **Host Header Attack**: Exploit where an attacker tampers with the HTTP `Host` header to poison password reset emails or cache entries; mitigated by `ALLOWED_HOSTS`.
- **HSTS (HTTP Strict Transport Security)**: Security header instructing browsers to refuse unencrypted HTTP communication with the domain for a designated timeframe.
- **Multi-Stage Docker Build**: Containerization pattern separating build tools from minimal runtime containers to optimize image size and security.

## Mental Models
- **The Security Air Gap**: Development mode leaves doors unlocked and walls open so developers can inspect inner pipes (`DEBUG=True`); Production mode seals all doors, installs bulletproof glass (`DEBUG=False`), and posts guards (`ALLOWED_HOSTS`, `CSRF_COOKIE_SECURE`).
- **The Factory Foreman (Gunicorn)**: Gunicorn master is the foreman standing on the catwalk; when requests flood in, the foreman hands requests to workers on the factory floor; if a worker crashes, the foreman spawns a replacement worker immediately.
- **Twelve-Factor Configuration**: Code is a static blueprint identical across all environments (Dev, Staging, Prod); environment variables are the fuel poured in at runtime that dictates how it runs.

## Anti-patterns
- **Running `DEBUG = True` in Production**: The most catastrophic deployment error; reveals private settings, API keys, database credentials, and full source code to any user encountering an unhandled exception.
- **Committing `SECRET_KEY` to Version Control**: Pushing plain `SECRET_KEY = "django-insecure-..."` to GitHub. Attackers can forge session cookies and sign arbitrary administrative payloads.
- **Wildcard `ALLOWED_HOSTS = ['*']` in Production**: Disabling host header validation, exposing the application to DNS rebinding and poisoned password reset links.
- **Using `manage.py runserver` for Production Traffic**: Attempting to run the single-threaded development server in production; it cannot handle concurrent users, lacks worker supervision, and leaks memory.

## Code Examples

### Production Settings with Environment Decoupling

```python
# bookr/settings.py
from pathlib import Path
from decouple import config, Csv
import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

# Load configuration from environment variables
SECRET_KEY = config("SECRET_KEY")
DEBUG = config("DEBUG", default=False, cast=bool)
ALLOWED_HOSTS = config("ALLOWED_HOSTS", default="127.0.0.1,localhost", cast=Csv())

# Database configuration from DATABASE_URL string
DATABASES = {
    "default": config(
        "DATABASE_URL",
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
        cast=dj_database_url.parse,
    )
}

# Production HTTPS / Security Headers
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = "DENY"
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

# Static files configuration with WhiteNoise
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",  # Placed directly after SecurityMiddleware
    ...
]
STATIC_ROOT = BASE_DIR / "staticfiles"
STATIC_URL = "/static/"
STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}
```
- **What it demonstrates**: Twelve-Factor configuration loading, database URL parsing, WhiteNoise setup, and automated HTTPS hardening.

### Production Dockerfile

```dockerfile
# Dockerfile - Multi-stage Production Container
FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq-dev && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# Copy application source
COPY . .

# Collect static assets into STATIC_ROOT
RUN python manage.py collectstatic --noinput

# Run as non-privileged system user for security
RUN adduser --disabled-password --no-create-home appuser && \
    chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

CMD ["gunicorn", "bookr.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3", "--access-logfile", "-"]
```
- **What it demonstrates**: Multi-worker Gunicorn execution, static asset pre-compilation, and unprivileged user security.

## Reference Tables

### Key Production Security Settings

| Setting | Production Recommendation | Security Threat Mitigated |
|---|---|---|
| `DEBUG` | `False` | Prevents credential leaks and traceback exposure |
| `SECRET_KEY` | Read from environment | Prevents cryptographic forgery and session hijacking |
| `ALLOWED_HOSTS` | Whitelist domains (`["bookr.com"]`) | Prevents HTTP Host header poisoning |
| `SECURE_SSL_REDIRECT` | `True` | Prevents man-in-the-middle sniffing of HTTP traffic |
| `SESSION_COOKIE_SECURE`| `True` | Ensures session cookies transmit only over HTTPS |
| `CSRF_COOKIE_SECURE` | `True` | Ensures CSRF tokens transmit only over HTTPS |
| `SECURE_HSTS_SECONDS` | `31536000` (1 Year) | Forces browsers to refuse insecure HTTP connections |

### WSGI vs. ASGI Application Servers

| Feature | WSGI (Gunicorn / uWSGI) | ASGI (Uvicorn / Daphne) |
|---|---|---|
| **Paradigm** | Synchronous, multi-process pre-fork | Asynchronous, event-loop driven |
| **Concurrency Model** | 1 process/thread per request | Concurrent co-routines (`asyncio`) |
| **Protocol Support** | HTTP/1.1 | HTTP/1.1, HTTP/2, WebSockets |
| **Best Used For** | Standard Django views, ORM, and REST APIs | Real-time chats, live notifications, WebSockets |

## Worked Example

### Preparing and Verifying Production Readiness

1. Create production environment file `.env`:
   ```bash
   SECRET_KEY=super-long-cryptographic-random-string-12345
   DEBUG=False
   ALLOWED_HOSTS=bookr.example.com,www.bookr.example.com
   DATABASE_URL=postgres://bookr_user:pass@db:5432/bookr_prod
   ```
2. Run Django's deployment verification check:
   ```bash
   python manage.py check --deploy
   # System check identified no issues (0 silenced).
   ```
3. Compile static assets:
   ```bash
   python manage.py collectstatic --noinput
   ```
4. Run Gunicorn server with 3 worker processes:
   ```bash
   gunicorn bookr.wsgi:application --bind 127.0.0.1:8000 --workers 3
   # [INFO] Starting gunicorn 22.0.0
   # [INFO] Listening at: http://127.0.0.1:8000 (1234)
   # [INFO] Using worker: sync
   # [INFO] Booting worker with pid: 1235
   # [INFO] Booting worker with pid: 1236
   # [INFO] Booting worker with pid: 1237
   ```

## Key Takeaways
1. Always set `DEBUG = False` and load `SECRET_KEY` and `ALLOWED_HOSTS` from environment variables in production.
2. Run `python manage.py check --deploy` to audit project security before public release.
3. Deploy Django using a pre-fork WSGI application server (Gunicorn) behind a reverse proxy (Nginx) or paired with WhiteNoise.
4. Set secure cookie flags (`SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE`, `SECURE_SSL_REDIRECT`, `HSTS`) to enforce HTTPS.
5. Containerize applications using unprivileged users and multi-worker execution specs for horizontal scalability.

## Connects To
- **Ch 01**: Introduction to Django — where development `runserver` started.
- **Ch 05**: Serving Static Files — compiling assets into `STATIC_ROOT` via `collectstatic`.
- **Ch 08**: Media Serving and File Uploads — handling persistent user uploads in production.
- **Ch 09**: Sessions and Authentication — securing production session cookies.
