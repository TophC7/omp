# Chapter 12: Building a REST API

## Core Idea
Django REST Framework (DRF) transforms Django applications into decoupled, stateless web services by translating relational model data to and from JSON using Serializers, consolidating CRUD operations into ViewSets, and generating standard RESTful URLs via automated Routers.

## Frameworks Introduced
- **The Serialization Framework (`serializers.ModelSerializer`)**:
  - Two-way data translation gateway:
    - *Serialization (Read)*: Converts complex model instances and QuerySets into native Python datatypes that can be easily rendered into JSON.
    - *Deserialization (Write)*: Parses incoming JSON request payloads, validates types and constraints, and converts data into Python objects or saves model instances directly.
  - Subclassing `serializers.ModelSerializer` automatically mirrors model fields, validators, and relational constraints defined in `models.py`.
  - Custom validation: Implement `validate_<fieldname>(self, value)` or multi-field `validate(self, data)`.

- **API Views & Generic Views Hierarchy**:
  - `api_view(['GET', 'POST'])`: Decorator converting simple function-based views into DRF-enabled handlers that parse incoming requests and return `rest_framework.response.Response`.
  - `APIView`: Base class-based API view supporting granular `get()`, `post()`, `put()`, `patch()`, and `delete()` handlers.
  - `generics.ListCreateAPIView` & `generics.RetrieveUpdateDestroyAPIView`: Pre-built class-based generic views combining querysets and serializers into functional endpoints with minimal code.

- **The ViewSet & Router Architecture**:
  - `viewsets.ModelViewSet`: Replaces separate list, detail, create, update, and delete views with a single unified class defining:
    - `list()`, `create()`, `retrieve()`, `update()`, `partial_update()`, `destroy()`.
  - `routers.DefaultRouter`: Automatically maps standard RESTful URL endpoints and generates a navigable root API directory:
    - `GET /api/books/` → `list`
    - `POST /api/books/` → `create`
    - `GET /api/books/<pk>/` → `retrieve`
    - `PUT /api/books/<pk>/` → `update`
    - `DELETE /api/books/<pk>/` → `destroy`

- **Token Authentication & Permissions**:
  - Stateless authentication protocol: Clients exchange username and password once for a static 40-character hexadecimal token.
  - Requests authenticate by supplying an HTTP header:
    `Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b`
  - Permissions policies: Declared per view or globally via `permission_classes`:
    - `IsAuthenticated`: Requires a valid token or session.
    - `IsAuthenticatedOrReadOnly`: Allows anonymous GET/HEAD requests, restricting POST/PUT/DELETE to authenticated clients.

## Key Concepts
- **REST (Representational State Transfer)**: Architectural style for stateless network communication where resources are identified by URIs and manipulated via standard HTTP verbs.
- **`Response(data, status=200)`**: DRF response object that automatically negotiates content type (JSON, Browsable API HTML) based on client `Accept` headers.
- **Nested Serializer**: Serializing related model instances as embedded JSON objects rather than raw integer foreign keys.
- **`serializer.is_valid(raise_exception=True)`**: Validates incoming payload; automatically raises `serializers.ValidationError`, which DRF translates into an HTTP 400 Bad Request response with structured error messages.
- **Browsable API**: Built-in interactive HTML interface allowing developers to inspect endpoints, submit forms, and test APIs directly in a web browser.

## Mental Models
- **The Two-Way Currency Converter (Serializer)**: Python model instances travel through the converter to emerge as universal JSON currency; incoming JSON bills are inspected for counterfeits (validation) and exchanged back into solid model gold.
- **The Master Router**: Instead of hand-soldering 10 separate URL routes for every model, register the ViewSet with a `DefaultRouter` switchboard that automatically wires up all 5 REST verbs and endpoints.
- **Stateless Tokens**: The server never remembers clients; every request must present its diplomatic passport (`Authorization: Token <key>`) at the border.

## Anti-patterns
- **Manual JSON Parsing with `json.loads`**: Manually extracting and validating JSON strings inside standard Django views instead of using DRF's `request.data` and Serializers.
- **Returning HTTP 200 on Validation Failure**: Returning `{"error": "Invalid data"}` with status code 200 OK. Always return standard REST error codes (`400 Bad Request`, `404 Not Found`).
- **N+1 Queries in API Serializers**: Serializing nested relationships without `select_related` or `prefetch_related` on the view's queryset, causing dozens of redundant database queries per API call.
- **Exposing Sensitive Fields in Serializers**: Including `password`, `is_superuser`, or internal audit columns in `Meta.fields = '__all__'`. Explicitly whitelist published fields.

## Code Examples

### ModelSerializer with Nested Relationships

```python
# reviews/serializers.py
from rest_framework import serializers
from .models import Book, Publisher, Review

class PublisherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Publisher
        fields = ("id", "name", "website", "email")

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ("id", "content", "rating", "date_created", "book")

    def validate_rating(self, value: int) -> int:
        if not 1 <= value <= 5:
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return value

class BookSerializer(serializers.ModelSerializer):
    # Nested representation for read operations
    publisher = PublisherSerializer(read_only=True)
    publisher_id = serializers.PrimaryKeyRelatedField(
        queryset=Publisher.objects.all(), source="publisher", write_only=True
    )

    class Meta:
        model = Book
        fields = ("id", "title", "publication_date", "isbn", "publisher", "publisher_id")
```
- **What it demonstrates**: Nested read representations with writable primary key input fields, plus custom field validation.

### ModelViewSet with Permission Controls

```python
# reviews/api_views.py
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .models import Book, Review
from .serializers import BookSerializer, ReviewSerializer

class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.select_related("publisher").all()
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.select_related("book").all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
```
- **What it demonstrates**: Full CRUD API for books and reviews in 12 lines of code, optimized with `select_related` and protected by permissions.

### Wiring Routers and Token Authentication

Configuring settings:
```python
# bookr/settings.py
INSTALLED_APPS = [
    ...
    "rest_framework",
    "rest_framework.authtoken",
]

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.TokenAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticatedOrReadOnly",
    ],
}
```

Routing in `bookr/urls.py`:
```python
# bookr/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken import views as authtoken_views
from reviews.api_views import BookViewSet, ReviewViewSet

router = DefaultRouter()
router.register("books", BookViewSet, basename="book")
router.register("reviews", ReviewViewSet, basename="review")

urlpatterns = [
    path("api/", include(router.urls)),
    # Endpoint to exchange username & password for a token
    path("api-token-auth/", authtoken_views.obtain_auth_token, name="api_token_auth"),
]
```
- **What it demonstrates**: Automated REST URL generation and built-in token acquisition endpoint.

## Reference Tables

### HTTP Verbs to DRF Action Mappings

| HTTP Method | URL Path Pattern | ModelViewSet Action | Description | Default Status Code |
|---|---|---|---|---|
| `GET` | `/api/books/` | `list` | Retrieve list of resources | `200 OK` |
| `POST` | `/api/books/` | `create` | Create a new resource | `201 Created` |
| `GET` | `/api/books/<pk>/` | `retrieve` | Retrieve single resource details | `200 OK` |
| `PUT` | `/api/books/<pk>/` | `update` | Replace entire resource | `200 OK` |
| `PATCH` | `/api/books/<pk>/` | `partial_update` | Update specific fields | `200 OK` |
| `DELETE` | `/api/books/<pk>/` | `destroy` | Remove resource permanently | `204 No Content` |

### DRF Permission Classes

| Permission Class | Allowed for Anonymous Users | Allowed for Authenticated Users |
|---|---|---|
| `AllowAny` | Unrestricted (GET, POST, PUT, DELETE) | Unrestricted |
| `IsAuthenticated` | None (HTTP 401 Unauthorized) | Unrestricted |
| `IsAuthenticatedOrReadOnly`| Read-Only (GET, HEAD, OPTIONS) | Full CRUD access |
| `IsAdminUser` | None | Staff users only (`is_staff=True`) |

## Worked Example

### Complete REST API Lifecycle: Token Creation, Listing, and Posting

1. Generate migration and migrate `rest_framework.authtoken`:
   `python manage.py migrate`
2. Obtain authentication token via terminal/HTTP client:
   ```bash
   curl -X POST http://127.0.0.1:8000/api-token-auth/ \
        -d "username=admin&password=secretpassword"
   # Response: {"token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b"}
   ```
3. Anonymous GET request (Allowed by `IsAuthenticatedOrReadOnly`):
   ```bash
   curl http://127.0.0.1:8000/api/books/
   # Response: HTTP 200 OK [{"id": 1, "title": "Web Development with Django 6", ...}]
   ```
4. Unauthenticated POST request (Rejected):
   ```bash
   curl -X POST http://127.0.0.1:8000/api/books/ -d "title=New Book"
   # Response: HTTP 401 Unauthorized {"detail": "Authentication credentials were not provided."}
   ```
5. Authenticated POST with Token header (Accepted):
   ```bash
   curl -X POST http://127.0.0.1:8000/api/books/ \
        -H "Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b" \
        -H "Content-Type: application/json" \
        -d '{"title": "Architecture Patterns with Python", "isbn": "9781492052203", "publication_date": "2020-03-05", "publisher_id": 1}'
   # Response: HTTP 201 Created {"id": 2, "title": "Architecture Patterns with Python", ...}
   ```

## Key Takeaways
1. Django REST Framework provides a mature, standard-compliant toolkit for building RESTful APIs.
2. `ModelSerializer` provides two-way translation between Python models and JSON dictionaries with automatic validation.
3. Use `ModelViewSet` and `DefaultRouter` to eliminate repetitive CRUD controller and URL routing code.
4. Always optimize ViewSet querysets with `select_related()` and `prefetch_related()` to prevent N+1 queries.
5. Secure APIs using `TokenAuthentication` and `IsAuthenticatedOrReadOnly` permissions.

## Connects To
- **Ch 02**: Models and Migrations — provides the underlying data models serialized by DRF.
- **Ch 09**: Sessions and Authentication — contrasting stateful session cookies with stateless API tokens.
- **Ch 11**: Advanced Templating and Class-Based Views — comparing HTML CBVs with API ViewSets.
