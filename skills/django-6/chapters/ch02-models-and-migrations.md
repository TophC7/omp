# Chapter 2: Models and Migrations

## Core Idea
Django's Object-Relational Mapper (ORM) translates declarative Python classes into relational database tables, managing database schema evolution through automated migration files and providing a rich, lazily-evaluated QuerySet API for database operations.

## Frameworks Introduced
- **The Model Declaration Framework**:
  - Subclass `models.Model` to define database tables, columns, constraints, and relationships in pure Python.
  - Fields map directly to SQL column data types and constraints (`CharField`, `IntegerField`, `DateField`, `DecimalField`, `TextField`).
  - When to use: For every domain entity requiring persistence in a relational database.
  - How: Define field attributes, choices, default values, and metadata options within an inner `class Meta:`.
  - Why it works: Provides database-agnostic table generation, built-in validation rules, and automatic admin representation.
  - Failure mode: Modifying field attributes (e.g. `max_length`) in Python without creating and applying a database migration.

- **Relational Mapping & Deletion Rules**:
  - *ForeignKey (Many-to-One)*: Links multiple rows in the current table to a single parent row. Requires explicit `on_delete` policy:
    - `models.CASCADE`: Deletes related records when parent is deleted.
    - `models.PROTECT`: Prevents parent deletion by raising `ProtectedError` if children exist.
    - `models.SET_NULL`: Sets foreign key column to `NULL` (requires `null=True`).
  - *ManyToManyField (Many-to-Many)*: Links rows across tables using an intermediary junction table; can specify custom through-models (`through="BookContributor"`).
  - *OneToOneField (One-to-One)*: Enforces strict 1:1 relationship with a unique foreign key constraint.

- **The Migration Engine**:
  - Two-step schema evolution lifecycle:
    1. `python manage.py makemigrations [app]`: Inspects `models.py`, compares against historical migration state, and generates declarative Python migration files in `<app>/migrations/`.
    2. `python manage.py migrate`: Applies unapplied migration operations within database transactions and logs applied migrations in `django_migrations`.
  - Introspection commands:
    - `python manage.py showmigrations`: Displays applied/unapplied status.
    - `python manage.py sqlmigrate <app> <number>`: Inspects raw SQL generated for a specific migration without applying it.

- **QuerySet API & Lazy Evaluation**:
  - Django QuerySets are lazy: defining a QuerySet (`books = Book.objects.filter(title__icontains="python")`) executes zero database queries.
  - Database queries execute only upon evaluation: iteration (`for b in books:`), slicing with step, indexing, `list()`, `bool()`, or calling `len()`.
  - Complex lookups using field lookups (`__exact`, `__iexact`, `__contains`, `__icontains`, `__in`, `__gt`, `__gte`, `__lt`, `__lte`, `__range`).

- **Q Objects for Complex Logic**:
  - Encapsulate SQL conditions to construct complex `OR` (`|`), `AND` (`&`), and `NOT` (`~`) logic in `filter()` queries.

## Key Concepts
- **ORM (Object-Relational Mapping)**: Abstraction layer converting relational database rows into Python model instances and vice-versa.
- **QuerySet**: An iterable collection of database queries that can be chained, filtered, ordered, and sliced.
- **Lazy Evaluation**: Postponing SQL execution until the data is explicitly consumed in Python code.
- **Related Name (`related_name`)**: The reverse relationship attribute added to the target model (defaults to `<model>_set`).
- **`bulk_create()`**: Method executing a single multi-row `INSERT` statement for a list of model instances, bypassing individual `save()` calls.
- **`bulk_update()`**: Method executing an efficient SQL `UPDATE` statement for specified fields across multiple instances.
- **`select_related`**: Performance optimization for single-valued relationships (ForeignKey, OneToOne) performing an SQL `JOIN`.
- **`prefetch_related`**: Performance optimization for multi-valued relationships (ManyToManyField, reverse ForeignKey) performing batched lookup queries.

## Mental Models
- **The Blueprint and the Mason**: Your `models.py` is the architectural blueprint; `makemigrations` creates the construction work order; `migrate` is the mason building the physical brick-and-mortar database schema.
- **Water Pipes (Lazy QuerySets)**: Chaining `.filter()` and `.exclude()` is like fitting PVC pipes together; no water flows until you turn on the tap (evaluate the QuerySet by iterating or taking `list(qs)`).
- **Q Objects as Circuit Switches**: Standard kwargs in `.filter(a=1, b=2)` are in series (AND); `Q(a=1) | Q(b=2)` connects switches in parallel (OR).

## Anti-patterns
- **The N+1 Query Problem**: Iterating over records and accessing foreign keys in a template loop (e.g. `{% for book in books %}{{ book.publisher.name }}{% endfor %}`), executing 1 query for books and N queries for publishers. Fix with `.select_related('publisher')`.
- **Row-by-Row Loop Saves**: Running `for item in items: item.save()` in a loop of 1,000 items, generating 1,000 separate network round-trips. Fix with `bulk_create()` or `bulk_update()`.
- **Modifying Migration Files Post-Commit**: Editing an already-shared, deployed migration file rather than creating a new migration file with `makemigrations`.
- **Misusing `.get()` for Multiple Objects**: Calling `Model.objects.get()` when zero or multiple records match, raising unhandled `DoesNotExist` or `MultipleObjectsReturned` exceptions.

## Code Examples

### Defining Relational Models (The Bookr Domain)

```python
# reviews/models.py
from django.db import models

class Publisher(models.Model):
    name = models.CharField(max_length=50, help_text="The name of the Publisher.")
    website = models.URLField(help_text="The Publisher's website.")
    email = models.EmailField(help_text="The Publisher's email address.")

    def __str__(self) -> str:
        return self.name

class Contributor(models.Model):
    first_names = models.CharField(max_length=50)
    last_names = models.CharField(max_length=50)
    email = models.EmailField()

    def __str__(self) -> str:
        return f"{self.first_names} {self.last_names}"

class Book(models.Model):
    title = models.CharField(max_length=100, help_text="The title of the book.")
    publication_date = models.DateField(verbose_name="Date the book was published.")
    isbn = models.CharField(max_length=20, verbose_name="ISBN number of the book.")
    publisher = models.ForeignKey(Publisher, on_delete=models.CASCADE, related_name="books")
    contributors = models.ManyToManyField(Contributor, through="BookContributor")

    def __str__(self) -> str:
        return self.title

class BookContributor(models.Model):
    class ContributionRole(models.TextChoices):
        AUTHOR = "AUTHOR", "Author"
        CO_AUTHOR = "CO_AUTHOR", "Co-Author"
        EDITOR = "EDITOR", "Editor"

    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    contributor = models.ForeignKey(Contributor, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ContributionRole.choices)

class Review(models.Model):
    content = models.TextField(help_text="The Review text.")
    rating = models.IntegerField(help_text="The rating the reviewer has given.")
    date_created = models.DateTimeField(auto_now_add=True)
    date_edited = models.DateTimeField(auto_now=True)
    book = models.ForeignKey(Book, on_delete=models.CASCADE, help_text="The Book that this review is for.")
```
- **What it demonstrates**: Defining models with `ForeignKey`, `ManyToManyField` through intermediate model, and `TextChoices`.

### Querying with Lookups and Q Objects

```python
from django.db.models import Q
from reviews.models import Book, Review

# Basic field lookup (case-insensitive substring)
python_books = Book.objects.filter(title__icontains="python")

# Complex OR / NOT query using Q objects
# Find books published by Packt OR published in 2026, but NOT titled "Legacy"
recent_or_packt = Book.objects.filter(
    (Q(publisher__name="Packt Publishing") | Q(publication_date__year=2026)) &
    ~Q(title__icontains="legacy")
)

# Reverse relationship lookup: Publishers with 5-star reviews
top_publishers = Publisher.objects.filter(books__review__rating=5).distinct()
```
- **What it demonstrates**: Filtering across relationships and chaining `Q` objects for Boolean SQL logic.

### Bulk Operations

```python
from reviews.models import Publisher

# Bulk Create (single multi-value INSERT query)
publishers_to_create = [
    Publisher(name=f"Publisher {i}", website="https://example.com", email=f"pub{i}@example.com")
    for i in range(100)
]
Publisher.objects.bulk_create(publishers_to_create, batch_size=50)

# Bulk Update (single multi-value UPDATE query)
publishers = Publisher.objects.filter(name__startswith="Publisher")
for p in publishers:
    p.website = "https://updated-domain.com"
Publisher.objects.bulk_update(publishers, ["website"], batch_size=50)
```
- **What it demonstrates**: High-throughput database batching without firing per-instance post-save signals.

## Reference Tables

### Common Model Field Types

| Field Class | Python Type | PostgreSQL / SQLite Type | Key Options |
|---|---|---|---|
| `CharField` | `str` | `varchar(N)` | `max_length` (required) |
| `TextField` | `str` | `text` | Unbounded multi-line text |
| `IntegerField` | `int` | `integer` | `-2147483648` to `2147483647` |
| `DecimalField` | `Decimal` | `numeric(m, d)` | `max_digits`, `decimal_places` |
| `DateField` | `datetime.date`| `date` | `auto_now`, `auto_now_add` |
| `DateTimeField` | `datetime.datetime`| `timestamp with time zone`| Timezone-aware timestamp |
| `BooleanField` | `bool` | `boolean` | `default=False` |
| `EmailField` | `str` | `varchar(254)` | Built-in email validator |
| `URLField` | `str` | `varchar(200)` | Built-in URL validator |

### Common Field Lookups

| Lookup Expression | Generated SQL Equivalent | Meaning |
|---|---|---|
| `field__exact="val"` | `field = 'val'` | Exact case-sensitive match |
| `field__iexact="val"` | `LOWER(field) = LOWER('val')` | Case-insensitive match |
| `field__contains="val"` | `field LIKE '%val%'` | Substring match |
| `field__icontains="val"`| `field ILIKE '%val%'` | Case-insensitive substring |
| `field__in=[1, 2, 3]` | `field IN (1, 2, 3)` | Inclusion match |
| `field__gt=5` | `field > 5` | Greater than |
| `field__gte=5` | `field >= 5` | Greater than or equal |
| `field__range=(a, b)` | `field BETWEEN a AND b` | Inclusive range match |

## Worked Example

### Complete Model Workflow: Creation, Migration, and Querying

1. Define model in `reviews/models.py`.
2. Generate migration:
```bash
python manage.py makemigrations reviews
# Output: Migrations for 'reviews':
#   reviews/migrations/0001_initial.py
#     - Create model Publisher
#     - Create model Contributor
#     - Create model Book
#     - Create model BookContributor
#     - Create model Review
```
3. Apply migration to SQLite/Postgres:
```bash
python manage.py migrate
# Output: Applying reviews.0001_initial... OK
```
4. Query in Django shell (`python manage.py shell`):
```python
from reviews.models import Publisher, Book, Review
from datetime import date

# Create publisher and book
pub = Publisher.objects.create(name="Packt", website="https://packt.com", email="info@packt.com")
book = Book.objects.create(title="Django 6 Guide", publication_date=date.today(), isbn="978-1-83620-207-3", publisher=pub)

# Create review linked via foreign key
Review.objects.create(book=book, content="Excellent architecture overview!", rating=5)

# Query via reverse relation
packt_books_with_reviews = Book.objects.filter(publisher__name="Packt", review__rating__gte=4).distinct()
assert packt_books_with_reviews.count() == 1
```

## Key Takeaways
1. Models define both database schemas and Python domain behaviors in a single declarative class.
2. Migrations must be version-controlled: `makemigrations` captures schema changes; `migrate` applies them.
3. Foreign keys require explicit `on_delete` policies (`CASCADE`, `PROTECT`, `SET_NULL`) to preserve relational integrity.
4. QuerySets are lazily evaluated; chaining filters does not hit the database until evaluated by iteration or formatting.
5. Prevent N+1 performance bottlenecks with `select_related()` (single relations) and `prefetch_related()` (multi relations).
6. Use `bulk_create()` and `bulk_update()` for multi-row operations to reduce database round-trips.

## Connects To
- **Ch 01**: Introduction to Django — where the MVT Model component originates.
- **Ch 03**: Django Views, URL Configuration, and Templates — displaying QuerySet data in HTML templates.
- **Ch 04**: An Introduction to Django Admin — registering models to manage data visually.
- **Ch 07**: Advanced Form Validation and Model Forms — automatically generating form fields directly from model definitions.
