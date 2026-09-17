# Chapter 9: Sessions and Authentication

## Core Idea
Django manages stateful user identity across stateless HTTP connections through a layered middleware pipeline that resolves cryptographic session cookies (`SessionMiddleware`), authenticates credentials, and attaches the active user identity (`AuthenticationMiddleware`) to every incoming request.

## Frameworks Introduced
- **The Middleware Pipeline Architecture**:
  - Middleware components wrap view execution in an onion-like pipeline:
    - *Request Phase*: Executes top-to-bottom in `MIDDLEWARE` list order before view invocation.
    - *Response Phase*: Executes bottom-to-top in reverse order after view invocation.
  - Key Modules:
    - `SecurityMiddleware`: Enforces SSL redirects and security headers (HSTS, XSS protection).
    - `SessionMiddleware`: Inspects `sessionid` cookie, loads storage backend, and attaches `request.session`.
    - `AuthenticationMiddleware`: Inspects session data, resolves user identity, and attaches `request.user` (instantiating `AnonymousUser` if unauthenticated).
    - `CsrfViewMiddleware`: Validates CSRF tokens on POST requests.
    - `MessageMiddleware`: Manages cookie-based flash notifications.

- **The Authentication API Lifecycle**:
  - `authenticate(request, username=..., password=...)`: Verifies credentials against configured authentication backends. If valid, returns the matching `User` instance; otherwise returns `None`.
  - `login(request, user)`: Attaches the user's primary key to the current session and rotates the session key to prevent Session Fixation attacks.
  - `logout(request)`: Flushes the session store and clears the `sessionid` cookie.
  - Password Hashing: Django uses PBKDF2 with SHA256 (or Argon2/bcrypt) with random per-user cryptographic salts. Passwords are never stored or logged in plaintext.

- **View Access Control Decorators**:
  - `@login_required(login_url="/accounts/login/")`: Intercepts unauthenticated users and redirects them to the login page, preserving the requested destination in a `?next=/target/` parameter.
  - `@permission_required("reviews.change_book", raise_exception=True)`: Restricts access to users possessing specific model-level permissions (granted directly or via Groups).
  - `@user_passes_test(lambda u: u.is_staff)`: Evaluates an arbitrary predicate function against `request.user`.

- **The Session Engine Framework**:
  - Provides a dictionary-like API on `request.session` backed by configurable persistence engines (`SESSION_ENGINE`):
    - `django.contrib.sessions.backends.db` (Default): Stores session blobs in the `django_session` table.
    - `django.contrib.sessions.backends.cache`: High-speed in-memory session storage (Redis/Memcached).
    - `django.contrib.sessions.backends.cached_db`: Write-through cache reading from memory and writing to database.
    - `django.contrib.sessions.backends.signed_cookies`: Client-side encrypted cookies with zero database storage overhead.
  - *The Mutation Flag*: When modifying mutable nested structures (lists/dicts) inside a session, Django's dirty-check cannot detect the inner mutation; developers must explicitly declare `request.session.modified = True`.

## Key Concepts
- **`request.user`**: The user model instance attached to every request (`is_authenticated=True` for logged-in accounts, `AnonymousUser` for guests).
- **Session ID (`sessionid`)**: A signed 32-character random string stored in an HTTP-only browser cookie pointing to server-side session state.
- **Session Fixation**: A security exploit where an attacker forces a known session ID on a victim; thwarted by Django rotating the session key upon `login()`.
- **`request.session.set_expiry()`**: Configures session lifetime (e.g., `0` for browser-close expiration, or seconds for sliding expiration).
- **Groups & Permissions**: Role-based access control where permissions (`<app>.<action>_<model>`) are attached to Groups, and Users inherit permissions via group membership.

## Mental Models
- **The Onion Middleware Wrapper**: Requests travel inward through outer security layers, peeling down to the view core; responses travel back outward through each layer to receive headers.
- **The Coat Check Token**: The browser holds only a small brass coat check token (`sessionid` cookie); all heavy winter coats and luggage (user profile, shopping cart, interaction history) remain securely stored in the server's coat room (`django_session`).
- **Session Fixation Immunity**: Every time a user changes privilege levels (logging in), Django throws away the old coat check ticket and issues a brand new random ticket.

## Anti-patterns
- **Plaintext Password Manipulation**: Assigning `user.password = "secret"`, which saves an unhashed string and prevents login. Always use `user.set_password("secret")` or `User.objects.create_user()`.
- **Unmarked Nested Session Mutations**: Modifying a nested list (`request.session['viewed_books'].append(12)`) without setting `request.session.modified = True`. Django will not persist the change to storage.
- **Storing Sensitive Secrets in Client Sessions**: Placing private keys, credit card numbers, or unencrypted tokens in `request.session` when using `signed_cookies`.
- **Ignoring the `?next=` Redirect Parameter**: Hardcoding redirect URLs after login instead of checking `request.GET.get("next")`, frustrating users who were redirected to login from a specific bookmark.

## Code Examples

### Custom Login and Logout Views

```python
# accounts/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpRequest, HttpResponse

def user_login(request: HttpRequest) -> HttpResponse:
    redirect_to = request.POST.get("next") or request.GET.get("next") or "reviews:index"

    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)  # Rotates session ID and binds user
                return redirect(redirect_to)
    else:
        form = AuthenticationForm()

    return render(request, "accounts/login.html", {"form": form, "next": redirect_to})

def user_logout(request: HttpRequest) -> HttpResponse:
    logout(request)  # Flushes session data
    return redirect("reviews:index")
```
- **What it demonstrates**: Handling credential authentication, session rotation via `login()`, and `next` query redirect preservation.

### View Access Control with Decorators

```python
# reviews/views.py
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render, get_object_or_404
from django.http import HttpRequest, HttpResponse
from .models import Book

@login_required(login_url="/accounts/login/")
def add_review(request: HttpRequest, pk: int) -> HttpResponse:
    book = get_object_or_404(Book, pk=pk)
    # Guaranteed request.user is authenticated
    return render(request, "reviews/review_form.html", {"book": book, "user": request.user})

@permission_required("reviews.delete_review", raise_exception=True)
def delete_review(request: HttpRequest, pk: int) -> HttpResponse:
    # Raises 403 Forbidden if user lacks permission
    ...
```
- **What it demonstrates**: Restricting views to authenticated users and checking granular permissions.

### Tracking Browsing History with Sessions

```python
# reviews/views.py
def book_detail(request: HttpRequest, pk: int) -> HttpResponse:
    book = get_object_or_404(Book, pk=pk)

    # Manage recently viewed books in session
    viewed_books = request.session.get("viewed_books", [])
    if book.pk not in viewed_books:
        viewed_books.append(book.pk)
        # Keep only the last 5 viewed books
        if len(viewed_books) > 5:
            viewed_books.pop(0)
        request.session["viewed_books"] = viewed_books
        request.session.modified = True  # Invariant: force session save for modified list

    return render(request, "reviews/book_detail.html", {"book": book})
```
- **What it demonstrates**: Storing user history in session and setting `modified = True`.

### Template Authentication State

```html
<!-- reviews/templates/reviews/base.html -->
<nav>
    <a href="{% url 'reviews:index' %}">Home</a>
    {% if user.is_authenticated %}
        <span>Welcome, <strong>{{ user.username }}</strong>!</span>
        {% if perms.reviews.change_book %}
            <a href="/admin/">Staff Admin</a>
        {% endif %}
        <a href="{% url 'accounts:logout' %}">Log Out</a>
    {% else %}
        <a href="{% url 'accounts:login' %}">Log In</a>
        <a href="{% url 'accounts:register' %}">Register</a>
    {% endif %}
</nav>
```
- **What it demonstrates**: Conditional navigation rendering using `user.is_authenticated` and `perms.<app>.<action>_<model>`.

## Reference Tables

### Session Storage Backends (`SESSION_ENGINE`)

| Engine Value | Storage Medium | Performance | Persistence Characteristics |
|---|---|---|---|
| `django.contrib.sessions.backends.db` | Relational Database (`django_session`) | Moderate | Survives server restarts; easy to query |
| `django.contrib.sessions.backends.cache` | In-Memory (Redis/Memcached) | Maximum | Volatile; lost if cache restarts without persistence |
| `django.contrib.sessions.backends.cached_db` | Redis Cache + Database write-through | Fast | High speed with durable relational fallback |
| `django.contrib.sessions.backends.signed_cookies`| Browser Cookie | High | Zero server storage; size capped at 4KB; client visible |

### Built-in Access Control Decorators

| Decorator | Argument | Behavior on Failure |
|---|---|---|
| `@login_required` | `login_url="/login/"` | Redirects to login with `?next=<path>` |
| `@permission_required` | `"app.codename"` | Redirects to login, or raises `PermissionDenied` (403) |
| `@user_passes_test` | `lambda user: bool` | Redirects to login or custom URL |

## Worked Example

### End-to-End Authentication and Session History Flow

1. User visits `/books/42/` as a guest:
   - `request.user` is `AnonymousUser`.
   - `book_detail` stores `pk=42` in `request.session["viewed_books"]`.
   - Server returns response with `Set-Cookie: sessionid=abc123xyz`.
2. User clicks "Write a Review" (`/books/42/review/`):
   - Protected by `@login_required`.
   - Browser redirects to `/accounts/login/?next=/books/42/review/`.
3. User submits valid credentials:
   - `authenticate()` verifies PBKDF2 hash against `auth_user`.
   - `login()` rotates session key from `abc123xyz` to `def456uvw` (anti-fixation).
   - View redirects back to `/books/42/review/`.
4. User accesses review page:
   - Request passes through `AuthenticationMiddleware`.
   - `request.user.is_authenticated` is `True`.
   - View renders review form populated with user context.

## Key Takeaways
1. Authentication is powered by middleware: `SessionMiddleware` reads the cookie; `AuthenticationMiddleware` populates `request.user`.
2. Always use `authenticate()` to verify passwords and `login()` to rotate session keys against session fixation attacks.
3. Passwords must never be saved directly; use `user.set_password()` to apply PBKDF2 salting.
4. Protect views using `@login_required` and `@permission_required` to enforce authorization rules.
5. When mutating nested data structures inside `request.session`, always set `request.session.modified = True`.

## Connects To
- **Ch 04**: An Introduction to Django Admin — utilizes the authentication framework for staff users.
- **Ch 07**: Advanced Form Validation and Model Forms — binding authenticated users via `commit=False`.
- **Ch 10**: Advanced Django Admin and Customizations — customizing user permissions and user models.
- **Ch 12**: Building a REST API — contrasting session cookies with token-based API authentication.
