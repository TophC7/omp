# Chapter 10: Building Modern REST APIs with Django Ninja

## Core Idea
Django Ninja provides a type-hinted, high-performance framework for building REST APIs in Django, leveraging Python type annotations and Pydantic schemas to automate request validation, serialization, and interactive OpenAPI documentation—serving as the programmatic JSON counterpart to HTMX's HTML-over-the-wire hypermedia.

## Frameworks Introduced
- **The Modern Django Full-Stack Split (HTMX + Django Ninja)**:
  - *HTML-over-the-Wire (HTMX)*: Serves first-party interactive browser UI using server-rendered template partials, sessions, and CSRF protection.
  - *JSON-over-the-Wire (Django Ninja)*: Serves programmatic API consumers—mobile applications, third-party webhook integrations, external partners, and CLI tools—using type-checked Pydantic schemas and API keys.
  - *Unified Core*: Both layers share the exact same Django ORM models, business rules, and database transactions.

- **The `NinjaAPI` & `Router` Architecture**:
  - `NinjaAPI(version="1.0", title="...")`: Central API container instantiated once in project settings and mounted onto `urls.py` via `path("api/v1/", api.urls)`.
  - `Router()`: Modular route collector instantiated in individual Django apps (e.g. `bands/api.py`, `venues/api.py`) and registered to the parent instance via `api.add_router("/bands/", bands_router)`.
  - *Trailing Slash Invariant*: Always declare endpoints with trailing slashes (e.g. `@router.get("/venues/")`) to prevent Django's `APPEND_SLASH` 301 redirects from dropping HTTP request bodies on POST/PUT actions.

- **Pydantic Schemas & `ModelSchema`**:
  - `ninja.Schema`: Base Pydantic class defining request and response JSON shapes using standard Python type annotations (`id: int`, `name: str`, `created_at: datetime`).
  - `ninja.ModelSchema`: Automatically derives schema fields directly from Django ORM models via an inner `class Meta: model = Venue; fields = [...]`.
  - *Nested Schemas & Relationship Aliasing*: Reverse foreign keys and many-to-many relationships are traversed seamlessly using field aliases:
    ```python
    class VenueOutSchema(ModelSchema):
        rooms: list[RoomSchema] = Field(..., alias="room_set")
        class Meta:
            model = Venue
            fields = ["id", "name"]
    ```

- **Query Filtering with `FilterSchema`**:
  - Replaces repetitive manual `request.GET.get()` lookups with declarative Pydantic filter classes:
    ```python
    class VenueFilter(FilterSchema):
        name: Optional[str] = Field(None, q=["name__istartswith"])
    ```
  - Injected into views via `def list_venues(request, filters: VenueFilter = Query(...)): venues = filters.filter(Venue.objects.all())`.

- **API Security via `APIKeyHeader`**:
  - Subclass `ninja.security.APIKeyHeader` to inspect incoming HTTP headers (`X-API-KEY`).
  - Implement `authenticate(self, request, key)` to validate tokens against database records or environment variables.
  - Protect endpoints by attaching `auth=token_auth` to router decorators (`@router.post("/venues/", auth=token_auth)`).

## Key Concepts
- **Django Ninja**: Fast, type-annotated REST framework for Django built on Pydantic and ASGI/WSGI standards.
- **`ModelSchema`**: Bridge class generating Pydantic validation and serialization directly from Django ORM model metadata.
- **OpenAPI & Swagger UI**: Standard API documentation generated automatically at `/api/v1/docs` with interactive request testing out of the box.
- **Automatic 404 Serialization**: When `get_object_or_404()` raises an `Http404` inside a Ninja endpoint, Ninja automatically converts it to a clean JSON response: `{"detail": "Not Found"}` with an HTTP 404 status.
- **`Query(...)` & `Path(...)`**: Parameter markers designating whether function arguments originate from query strings or URL path segments.
- **Content Negotiation**: Distinguishing between hypermedia requests (returning HTML partials) and programmatic API requests (returning JSON).

## Mental Models
- **The Two Front Doors to the Same House**: The Django ORM and domain models represent the house. The front door with the welcome mat is HTMX (welcoming human browser visitors with warm, rendered HTML rooms). The side door with the electronic keycard reader is Django Ninja (granting programmatic access to robots, mobile apps, and automated scripts with structured JSON payloads).
- **The Schema Gatekeeper**: Every incoming and outgoing JSON payload must present credentials matching a Pydantic schema. Malformed types (e.g. string sent where integer required) are rejected immediately at the perimeter with detailed 422 error passports before reaching the database.

## Anti-patterns
- **Omitting Trailing Slashes on API Endpoints**: Defining `@router.post("/venues")` without the trailing slash. When a client POSTs without a slash, Django returns a 301 redirect to `/venues/`, stripping the POST body and converting the request to a GET.
- **Returning Unserialized Model Instances**: Returning raw Django QuerySets without specifying `response=list[MySchema]`, triggering JSON serialization `TypeError` exceptions.
- **Duplicating Domain Rules Between HTMX & Ninja**: Writing separate business validation logic for API endpoints that diverges from Django Model/ModelForm validation. Keep business logic centralized on the model or service layer.
- **Hardcoding API Keys in Source Code**: Comparing incoming keys against hardcoded string literals instead of environment variables (`os.environ`) or hashed database tokens.

## Code Examples

### 1. Ninja API Configuration & Router Mounting
```python
# RiffMates/urls.py
from django.contrib import admin
from django.urls import path
from ninja import NinjaAPI
from bands.api import router as bands_router

# Instantiate central API with versioning and title
api = NinjaAPI(
    version="1.0",
    title="RiffMates API",
    description="Programmatic REST API for bands, venues, and musicians."
)

# Mount modular app routers
api.add_router("/bands/", bands_router)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/", api.urls),  # Swagger docs available at /api/v1/docs
]
```

### 2. Schemas & Nested Relationships (`bands/schemas.py`)
```python
from ninja import ModelSchema, Schema, Field
from typing import Optional
from bands.models import Venue, Room

class RoomSchema(ModelSchema):
    class Meta:
        model = Room
        fields = ["id", "name"]

class VenueInSchema(Schema):
    name: str

class VenueOutSchema(ModelSchema):
    # Reverse foreign key traversed via alias='room_set'
    rooms: list[RoomSchema] = Field(..., alias="room_set")
    
    class Meta:
        model = Venue
        fields = ["id", "name"]
```

### 3. API Key Authentication (`bands/security.py`)
```python
import os
from django.http import HttpRequest
from ninja.security import APIKeyHeader

class ApiKey(APIKeyHeader):
    param_name = "X-API-KEY"

    def authenticate(self, request: HttpRequest, key: Optional[str]) -> Optional[str]:
        # Validate against environment variable or API key database table
        valid_key = os.environ.get("RIFFMATES_API_KEY", "secret-api-token")
        if key == valid_key:
            return key
        return None

token_auth = ApiKey()
```

### 4. Full CRUD Endpoints with Filtering (`bands/api.py`)
```python
from typing import Optional
from django.shortcuts import get_object_or_404
from ninja import Router, FilterSchema, Field, Query
from bands.models import Venue
from bands.schemas import VenueInSchema, VenueOutSchema
from bands.security import token_auth

router = Router()

class VenueFilter(FilterSchema):
    name: Optional[str] = Field(None, q=["name__istartswith"])

@router.get("/venues/", response=list[VenueOutSchema])
def list_venues(request, filters: VenueFilter = Query(...)):
    """List all venues with optional name prefix filtering."""
    venues = Venue.objects.all().prefetch_related("room_set")
    return filters.filter(venues)

@router.get("/venues/{venue_id}/", response=VenueOutSchema)
def get_venue(request, venue_id: int):
    """Retrieve a single venue by ID (auto-serializes 404 if missing)."""
    return get_object_or_404(Venue, id=venue_id)

@router.post("/venues/", response={201: VenueOutSchema}, auth=token_auth)
def create_venue(request, payload: VenueInSchema):
    """Create a new venue (protected by API key)."""
    venue = Venue.objects.create(name=payload.name)
    return 201, venue

@router.put("/venues/{venue_id}/", response=VenueOutSchema, auth=token_auth)
def update_venue(request, venue_id: int, payload: VenueInSchema):
    """Update an existing venue."""
    venue = get_object_or_404(Venue, id=venue_id)
    venue.name = payload.name
    venue.save()
    return venue

@router.delete("/venues/{venue_id}/", response={204: None}, auth=token_auth)
def delete_venue(request, venue_id: int):
    """Delete a venue."""
    venue = get_object_or_404(Venue, id=venue_id)
    venue.delete()
    return 204, None
```

## Reference Tables

### Django Ninja vs Django REST Framework (DRF)
| Architectural Feature | Django Ninja | Django REST Framework (DRF) |
|:---|:---|:---|
| **Type Checking** | Native Python type hints + Pydantic | Custom serializer classes |
| **Documentation** | Automatic OpenAPI / Swagger UI at `/docs` | Requires external packages (drf-spectacular) |
| **Execution Performance** | High (lightweight, async-native) | Moderate (heavy serializer machinery) |
| **Learning Curve** | Gentle (FastAPI-like ergonomics) | Steep (complex class-based views/mixins) |
| **`INSTALLED_APPS`** | Not required | Required |
| **Async Support** | Native `async def` view handlers | Supported in newer versions |

### Parameter Sources in Django Ninja Endpoints
| Syntax in View Function | Parameter Location | Example |
|:---|:---|:---|
| `venue_id: int` matching `{venue_id}` in URL | URL Path Segment | `@router.get("/venues/{venue_id}/")` |
| `name: Optional[str] = None` | URL Query String | `/venues/?name=Madison` |
| `payload: MySchema` | HTTP Request Body (JSON) | `POST /venues/` with `{"name": "..."}` |
| `filters: MyFilter = Query(...)` | Query String Filter Collection | `/venues/?name__istartswith=The` |
| `auth=api_key` | HTTP Header (`X-API-KEY`) | Validated via `APIKeyHeader` subclass |

## Worked Example

### Complete Venue & Room API with Nested Serialization
Demonstrating how a client queries an endpoint and receives full nested child relations automatically:

**1. Data Models in Database:**
- `Venue(id=1, name="The Fillmore")`
- `Room(id=101, name="Main Auditorium", venue_id=1)`
- `Room(id=102, name="VIP Lounge", venue_id=1)`

**2. Client Request (HTTP GET):**
```http
GET /api/v1/bands/venues/1/ HTTP/1.1
Host: localhost:8000
Accept: application/json
```

**3. Django Ninja Processing:**
- `get_venue(request, venue_id=1)` executes `get_object_or_404(Venue, id=1)`.
- Returns model instance.
- Django Ninja serializes instance matching `VenueOutSchema`.
- `rooms` field resolves alias `"room_set"`, executing ORM child lookup.
- Child rooms serialize through `RoomSchema`.

**4. JSON Response (HTTP 200 OK):**
```json
{
  "id": 1,
  "name": "The Fillmore",
  "rooms": [
    {
      "id": 101,
      "name": "Main Auditorium"
    },
    {
      "id": 102,
      "name": "VIP Lounge"
    }
  ]
}
```

## Key Takeaways
1. Django Ninja provides a type-hinted, high-speed REST API layer that complements HTMX's HTML-over-the-wire hypermedia.
2. `ModelSchema` automatically derives validation and serialization directly from Django ORM models.
3. Interactive Swagger UI documentation is generated automatically out of the box at `/api/v1/docs`.
4. Trailing slashes must be explicitly declared on router endpoints to prevent 301 redirects from corrupting HTTP POST/PUT payloads.
5. `APIKeyHeader` and `FilterSchema` streamline security and complex database querying with clean, declarative syntax.

## Connects To
- **Ch 01**: HTMX Foundations & Attributes — comparing hypermedia architecture against JSON REST APIs.
- **Ch 08**: Django HTMX Foundations & Architecture — sharing models, authentication, and database logic across web and API layers.
- **Ch 09**: Django HTMX Interactive Patterns — using the same Django ORM models for hypermedia widgets and REST endpoints.
