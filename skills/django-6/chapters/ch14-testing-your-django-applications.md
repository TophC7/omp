# Chapter 14: Testing Your Django Applications

## Core Idea
Django provides an automated testing framework built atop Python's `unittest` library, offering transactional database sandboxing, class-level fixture caching (`setUpTestData`), a simulated HTTP Test Client, and specialized assertions for validating models, views, and templates.

## Frameworks Introduced
- **The Django TestCase Hierarchy (`django.test`)**:
  - Specialized base classes providing varying levels of database and server isolation:
    - `SimpleTestCase`: Disallows database queries entirely; raises an error if an SQL query is attempted. Best for testing pure algorithms, utilities, and standalone forms.
    - `TestCase` (Standard): Wraps each test method inside an atomic database transaction that is rolled back upon test completion. Provides instant database isolation without truncating tables.
    - `TransactionTestCase`: Does not wrap tests in rollbacks; truncates database tables after each test run. Required only when explicitly verifying transaction commit hooks, rollbacks, or multi-threaded background workers.
    - `LiveServerTestCase`: Spawns a real HTTP server on an ephemeral background port, allowing full-browser integration testing with Selenium or Playwright.

- **Lifecycle Setup Optimization (`setUpTestData`)**:
  - Class-level hook `@classmethod def setUpTestData(cls):` executes once per `TestCase` class rather than before each test method.
  - Populates shared read-only database fixtures in memory.
  - Combined with per-test atomic transaction rollbacks, this reduces database setup overhead by an order of magnitude compared to `setUp()`.

- **The Django Test Client Framework (`self.client`)**:
  - Simulates a web browser making HTTP requests (`client.get()`, `client.post()`) passing through the full Django middleware pipeline and URL dispatcher without network socket overhead.
  - Authentication helpers:
    - `client.login(username=..., password=...)`: Simulates full authentication flow.
    - `client.force_login(user)`: Directly binds an authenticated user, bypassing password hashing to accelerate test suites.
  - Specialized Assertions:
    - `assertContains(response, text, status_code=200)`: Asserts status code and verifies substring presence in rendered HTML.
    - `assertTemplateUsed(response, "reviews/book_list.html")`: Verifies which templates were evaluated during rendering.
    - `assertRedirects(response, expected_url)`: Follows HTTP 302 redirects and validates final landing pages.

- **The RequestFactory Pattern (`RequestFactory`)**:
  - Construct direct, standalone `HttpRequest` instances without routing through the URL dispatcher or middleware stack.
  - Allows invoking view functions directly in complete isolation: `response = my_view(request)`.

## Key Concepts
- **Transactional Rollback Isolation**: Running each test method within `SAVEPOINT` / `ROLLBACK` transactions to restore clean database state without slow `FLUSH` operations.
- **`setUpTestData`**: Class method creating immutable baseline data once for all test methods in the class.
- **`assertContains`**: High-level assertion checking status code, content presence, and handling decoded byte responses automatically.
- **`force_login()`**: Optimization skipping expensive PBKDF2 password verification during test authentication setup.
- **`--parallel` Flag**: CLI option (`python manage.py test --parallel`) distributing test runs across available CPU cores.

## Mental Models
- **The Transactional Sandbox**: Each test enters a temporary database sandbox; it builds sandcastles, modifies rows, and deletes tables; when the test finishes, Django resets the sand with a single transaction rollback, leaving the beach pristine for the next test.
- **Virtual Browser (Client) vs. Wire Tap (RequestFactory)**: `self.client` is a virtual browser sitting on the outside typing URLs and passing through security guards (middleware); `RequestFactory` taps directly into the view's internal telephone wire, passing synthesized signals straight to the function.
- **The Factory Assembly Line (`setUpTestData`)**: Build the expensive test fixtures once at the beginning of the shift, not before every single minute of work.

## Anti-patterns
- **Using `setUp()` for Heavy Database Fixtures**: Creating 10 model instances inside `def setUp(self):`. This re-inserts the data before *every single test method*, grinding large test suites to a halt. Use `setUpTestData` instead.
- **Defaulting to `TransactionTestCase`**: Using `TransactionTestCase` for routine database tests. Truncating and re-creating database tables after each test is 10x–50x slower than `TestCase` rollbacks.
- **Testing Formats via Raw String Regexes**: Writing fragile regex assertions against raw HTML strings (`re.search('<input...', response.content)`) instead of using `assertContains()` or form validation unit tests.
- **Testing Production Databases**: Running test commands against live databases. Django creates a dedicated ephemeral test database (prefixed with `test_`), but developers must ensure settings point to local or test database credentials.

## Code Examples

### Model and Form Unit Testing

```python
# reviews/tests/test_models.py
from django.test import TestCase
from django.core.exceptions import ValidationError
from datetime import date
from reviews.models import Publisher, Book

class ModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.publisher = Publisher.objects.create(
            name="Packt Publishing",
            website="https://packt.com",
            email="contact@packt.com",
        )

    def test_book_str_returns_title(self):
        book = Book.objects.create(
            title="Django 6 Deep Dive",
            publication_date=date.today(),
            isbn="978-1-83620-207-3",
            publisher=self.publisher,
        )
        self.assertEqual(str(book), "Django 6 Deep Dive")

    def test_duplicate_isbn_is_prevented(self):
        Book.objects.create(
            title="Book 1", publication_date=date.today(),
            isbn="1234567890", publisher=self.publisher
        )
        with self.assertRaises(Exception):
            Book.objects.create(
                title="Book 2", publication_date=date.today(),
                isbn="1234567890", publisher=self.publisher
            )
```
- **What it demonstrates**: Using `setUpTestData` for shared publisher fixtures and asserting string representations and database uniqueness.

### View Testing with the Test Client

```python
# reviews/tests/test_views.py
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from datetime import date
from reviews.models import Publisher, Book

User = get_user_model()

class ViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username="testuser", password="secretpassword")
        cls.publisher = Publisher.objects.create(name="Packt", website="https://packt.com", email="info@packt.com")
        cls.book = Book.objects.create(
            title="Web Development with Django 6",
            publication_date=date(2026, 3, 1),
            isbn="9781836202073",
            publisher=cls.publisher,
        )

    def test_book_list_view_renders_correctly(self):
        url = reverse("reviews:book_list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "reviews/book_list.html")
        self.assertContains(response, "Web Development with Django 6")
        self.assertIn(self.book, response.context["books"])

    def test_review_create_requires_login(self):
        url = reverse("reviews:book_review", kwargs={"pk": self.book.pk})
        response = self.client.get(url)
        
        # Verify redirect to login page
        expected_redirect = f"/accounts/login/?next={url}"
        self.assertRedirects(response, expected_redirect)

    def test_review_create_authenticated_post(self):
        url = reverse("reviews:book_review", kwargs={"pk": self.book.pk})
        self.client.force_login(self.user)  # High-speed auth bypass

        response = self.client.post(url, {
            "rating": 5,
            "content": "Outstanding guide to modern Django architectures!",
        })

        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.book.review_set.count(), 1)
```
- **What it demonstrates**: Testing HTTP status codes, templates used, context injection, login redirection, and form submission with `force_login()`.

### Isolated View Testing with `RequestFactory`

```python
# reviews/tests/test_isolated_views.py
from django.test import SimpleTestCase, RequestFactory
from django.contrib.auth.models import AnonymousUser
from reviews.views import index

class IsolatedViewTests(SimpleTestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_index_view_direct_call(self):
        request = self.factory.get("/")
        request.user = AnonymousUser()

        response = index(request)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Bookr", response.content)
```
- **What it demonstrates**: Using `RequestFactory` to test a view function directly without routing or middleware overhead.

## Reference Tables

### Django TestCase Class Hierarchy

| Class | Database Access | Isolation Mechanism | Relative Speed | Typical Use Case |
|---|---|---|---|---|
| `SimpleTestCase` | **Disabled** (Raises Error) | None | Blindingly fast | Pure Python logic, utilities, regexes |
| `TestCase` | **Enabled** | Transactional `SAVEPOINT` rollback | Fast (~10–50ms) | 90% of all unit and integration tests |
| `TransactionTestCase`| **Enabled** | Database `TRUNCATE / FLUSH` | Slow (~200–1000ms) | Transaction commit hooks, concurrency |
| `LiveServerTestCase` | **Enabled** | Background TCP Server | Very slow | Selenium, Playwright, E2E browser tests |

### Key Django Test Assertions

| Assertion Method | Parameters | Behavior Checked |
|---|---|---|
| `assertContains(resp, text)` | `response, text, status_code=200` | Checks HTTP status and verifies substring in content |
| `assertNotContains(resp, text)`| `response, text` | Ensures text does not appear in rendered output |
| `assertTemplateUsed(resp, name)`| `response, template_name` | Confirms template was loaded by DTL engine |
| `assertRedirects(resp, target)` | `response, target_url` | Validates 302 redirect status and destination path |
| `assertFormError(form, fld, err)`| `form, field_name, error_msg` | Asserts validation errors attached to form inputs |
| `assertQuerySetEqual(qs, list)` | `queryset, expected_list` | Validates QuerySet contents and ordering |

## Worked Example

### End-to-End Test Suite Execution

1. Organize tests into a modular package:
   `reviews/tests/`
   ├── `__init__.py`
   ├── `test_models.py`
   ├── `test_views.py`
   └── `test_forms.py`
2. Run full test suite:
   ```bash
   python manage.py test
   # Creating test database for alias 'default'...
   # System check identified no issues (0 silenced).
   # ......
   # ----------------------------------------------------------------------
   # Ran 6 tests in 0.245s
   # OK
   # Destroying test database for alias 'default'...
   ```
3. Run specific test case with parallel acceleration:
   `python manage.py test reviews.tests.test_views --parallel`

## Key Takeaways
1. Subclass `TestCase` for standard database tests to leverage fast transactional rollbacks.
2. Optimize shared database fixtures with `setUpTestData` to avoid re-inserting records before every test method.
3. Use `self.client` to test full request-response workflows, and `force_login()` to bypass password hashing overhead.
4. Verify both HTTP status codes and rendered content using `assertContains()` and `assertTemplateUsed()`.
5. Use `SimpleTestCase` for tests that do not touch the database to maximize test execution speed.

## Connects To
- **Ch 02**: Models and Migrations — models exercised by database test cases.
- **Ch 03**: Django Views, URL Configuration, and Templates — views and templates verified by the Test Client.
- **Ch 09**: Sessions and Authentication — testing access control with authenticated client sessions.
- **Ch 12**: Building a REST API — testing DRF API endpoints using `APIClient`.
