# Chapter 13: Generating CSV, PDF, and Other Binary Files

## Core Idea
Django views can dynamically generate and stream non-HTML binary payloads—including CSV spreadsheets, Excel workbooks, PDF documents, and ZIP archives—by configuring MIME content types, managing `Content-Disposition` headers, and utilizing in-memory byte buffers.

## Frameworks Introduced
- **The File-Like `HttpResponse` Stream Pattern**:
  - A Django `HttpResponse` implements the Python file-like write interface (`write()`, `writelines()`).
  - Text-based formats (like CSV) can write directly into the `HttpResponse` object without intermediary temporary files on disk.
  - Critical HTTP Header Invariants:
    - `Content-Type`: Declares the MIME type to client browsers (e.g. `text/csv`, `application/pdf`).
    - `Content-Disposition`: Instructs client browsers how to handle the payload:
      - `attachment; filename="report.csv"`: Triggers a file download prompt.
      - `inline; filename="report.pdf"`: Attempts to render the file within the browser tab.

- **In-Memory Binary Buffering (`io.BytesIO`)**:
  - Binary generators (Excel, ZIP archives, generated charts, PDFs) require seekable byte streams that cannot write directly into plain text responses.
  - Pattern:
    1. Instantiate an in-memory buffer: `buffer = io.BytesIO()`.
    2. Pass `buffer` to the binary library (e.g., `xlsxwriter.Workbook(buffer)` or `zipfile.ZipFile(buffer, 'w')`).
    3. Generate and close the document.
    4. Seek to the start (`buffer.seek(0)`) or extract value (`buffer.getvalue()`).
    5. Construct `HttpResponse(buffer.getvalue(), content_type=...)`.
  - Eliminates server disk I/O, file permission issues, and disk cleanup maintenance.

- **HTML-to-PDF Rendering (WeasyPrint / ReportLab)**:
  - Generates publication-quality PDF documents directly from standard Django HTML templates and CSS styles.
  - Render template to string (`render_to_string("report.html", context)`), compile via WeasyPrint, and stream raw PDF bytes into the response.

- **`StreamingHttpResponse` for Large Datasets**:
  - Prevents Out-Of-Memory (OOM) crashes when exporting massive datasets (e.g., 500,000 database rows).
  - Accepts a generator function yielding chunks of text or bytes.
  - Streams rows incrementally over HTTP without buffering the full dataset in server memory.

## Key Concepts
- **MIME Type**: Two-part identifier indicating the nature and format of a file transmitted over HTTP (e.g., `text/csv`, `application/pdf`).
- **`Content-Disposition`**: HTTP response header specifying whether content should be displayed inline or downloaded as an attachment.
- **`BytesIO` / `StringIO`**: In-memory byte and string stream buffers from Python's standard `io` library.
- **`StreamingHttpResponse`**: Django response class that streams content via a Python iterator or generator rather than a pre-computed string.
- **XlsxWriter**: High-performance Python package for formatting, writing, and charting Excel `.xlsx` spreadsheets.

## Mental Models
- **The Pipe to the Browser**: The `HttpResponse` object acts as an open plumbing pipe connected directly to the user's download manager; writing data to the response streams bytes straight through the pipe.
- **In-Memory RAM Canvas**: Constructing binary files in `io.BytesIO()` is like painting on an easel in RAM; once finished, you ship the canvas over the wire and dissolve the easel instantly, leaving zero clutter on disk.
- **Attachment vs. Inline**: `attachment` tells the browser "Save this box in your downloads folder"; `inline` tells the browser "Open this box and look at it right here".

## Anti-patterns
- **Writing Temporary Export Files to Server Disk**: Saving `report.csv` to local disk (`/tmp/export.csv`) before reading it back into `HttpResponse`. If traffic spikes, disk space fills up and simultaneous users may overwrite each other's files. Use `io.BytesIO` instead.
- **Buffering Millions of Rows in RAM**: Using `Book.objects.all()` and writing 500,000 rows into a standard `HttpResponse`. This exhausts server memory and crashes worker processes. Use `StreamingHttpResponse` with QuerySet `.iterator()`.
- **Forgetting File Extension in `Content-Disposition`**: Writing `filename="report"` without `.csv` or `.pdf`. Operating systems fail to associate the downloaded file with the correct desktop application.
- **Leaving Buffers Open**: Forgetting to close workbooks (`workbook.close()`) before reading buffer values, resulting in truncated or corrupted binary archives.

## Code Examples

### CSV Export View Using Standard Library

```python
# reviews/views.py
import csv
from django.http import HttpRequest, HttpResponse
from .models import Book

def export_books_csv(request: HttpRequest) -> HttpResponse:
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="books_catalog.csv"'

    writer = csv.writer(response)
    # 1. Write Header Row
    writer.writerow(["Title", "ISBN", "Publisher", "Publication Date"])

    # 2. Stream database records (optimized with select_related)
    books = Book.objects.select_related("publisher").all()
    for book in books:
        writer.writerow([
            book.title,
            book.isbn,
            book.publisher.name,
            book.publication_date.strftime("%Y-%m-%d"),
        ])

    return response
```
- **What it demonstrates**: Writing directly into `HttpResponse` with correct CSV headers and dates.

### Excel Workbook Export Using `io.BytesIO` & `xlsxwriter`

```python
# reviews/views.py
import io
import xlsxwriter
from django.http import HttpRequest, HttpResponse
from .models import Book

def export_books_excel(request: HttpRequest) -> HttpResponse:
    buffer = io.BytesIO()
    workbook = xlsxwriter.Workbook(buffer)
    worksheet = workbook.add_worksheet("Books")

    # Styling formats
    header_format = workbook.add_format({"bold": True, "bg_color": "#D3D3D3", "border": 1})
    date_format = workbook.add_format({"num_format": "yyyy-mm-dd"})

    # Write headers
    headers = ["Title", "ISBN", "Publisher", "Publication Date"]
    for col_num, header in enumerate(headers):
        worksheet.write(0, col_num, header, header_format)

    # Write data rows
    books = Book.objects.select_related("publisher").all()
    for row_num, book in enumerate(books, start=1):
        worksheet.write(row_num, 0, book.title)
        worksheet.write(row_num, 1, book.isbn)
        worksheet.write(row_num, 2, book.publisher.name)
        worksheet.write(row_num, 3, str(book.publication_date), date_format)

    worksheet.autofit()
    workbook.close()  # Finalize document before extracting bytes

    buffer.seek(0)
    response = HttpResponse(
        buffer.getvalue(),
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    response["Content-Disposition"] = 'attachment; filename="books_catalog.xlsx"'
    return response
```
- **What it demonstrates**: Using `io.BytesIO` buffer, applying cell styling, auto-fitting column widths, and setting the OpenXML MIME type.

### Memory-Efficient Streaming CSV Export

```python
# reviews/views.py
import csv
from typing import Generator
from django.http import HttpRequest, StreamingHttpResponse
from .models import Review

class Echo:
    """An object that implements just the write method of the file-like interface."""
    def write(self, value):
        return value

def generate_review_rows() -> Generator[str, None, None]:
    writer = csv.writer(Echo())
    yield writer.writerow(["Book Title", "Rating", "Review Content"])

    # iterator() streams rows from database without loading entire table into RAM
    for review in Review.objects.select_related("book").iterator(chunk_size=2000):
        yield writer.writerow([review.book.title, review.rating, review.content])

def export_reviews_streaming(request: HttpRequest) -> StreamingHttpResponse:
    response = StreamingHttpResponse(generate_review_rows(), content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="all_reviews.csv"'
    return response
```
- **What it demonstrates**: Combining `StreamingHttpResponse` with `QuerySet.iterator()` to export millions of rows with minimal, constant memory footprint.

## Reference Tables

### Common MIME Content-Types

| Format | Content-Type Header Value | Target Extension |
|---|---|---|
| **CSV** | `text/csv` | `.csv` |
| **PDF** | `application/pdf` | `.pdf` |
| **Excel (.xlsx)** | `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet` | `.xlsx` |
| **ZIP Archive** | `application/zip` | `.zip` |
| **JSON** | `application/json` | `.json` |
| **PNG Image** | `image/png` | `.png` |

### Content-Disposition Directives

| Directive Syntax | Client Behavior | Typical Use Case |
|---|---|---|
| `attachment; filename="data.csv"` | Prompts browser download dialog | CSV/Excel exports, ZIP archives, backup files |
| `inline; filename="doc.pdf"` | Renders document inside browser tab | PDF invoices, reports, embedded images |

## Worked Example

### End-to-End PDF Invoice / Catalog Generation with WeasyPrint

1. Install WeasyPrint: `pip install weasyprint`
2. Create invoice HTML template (`reviews/templates/reviews/catalog_pdf.html`):
```html
<!DOCTYPE html>
<html>
<head>
    <style>
        @page { size: A4; margin: 2cm; }
        body { font-family: sans-serif; }
        h1 { color: #2c3e50; border-bottom: 2px solid #2c3e50; }
        table { width: 100%; border-collapse: collapse; margin-top: 1rem; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
    </style>
</head>
<body>
    <h1>Bookr Catalog Summary</h1>
    <table>
        <tr><th>Title</th><th>Publisher</th><th>ISBN</th></tr>
        {% for book in books %}
            <tr><td>{{ book.title }}</td><td>{{ book.publisher.name }}</td><td>{{ book.isbn }}</td></tr>
        {% endfor %}
    </table>
</body>
</html>
```
3. View implementation:
```python
from django.template.loader import render_to_string
from weasyprint import HTML
from django.http import HttpResponse

def export_catalog_pdf(request):
    books = Book.objects.select_related("publisher").all()
    html_string = render_to_string("reviews/catalog_pdf.html", {"books": books})
    pdf_bytes = HTML(string=html_string).write_pdf()

    response = HttpResponse(pdf_bytes, content_type="application/pdf")
    response["Content-Disposition"] = 'inline; filename="catalog.pdf"'
    return response
```
4. User visits `/export/pdf/`: Browser immediately renders a styled, printable A4 PDF catalog inside the active tab.

## Key Takeaways
1. Set `Content-Type` and `Content-Disposition` headers to control MIME parsing and download behavior.
2. Direct text exports (CSV) directly into `HttpResponse`; buffer binary generators (Excel, ZIP) in `io.BytesIO()`.
3. Never write temporary export files to physical server disks when in-memory streaming is possible.
4. Use `StreamingHttpResponse` combined with `QuerySet.iterator()` for huge exports to prevent memory exhaustion.
5. Close binary workbooks and archives before reading buffer bytes to ensure file completeness.

## Connects To
- **Ch 03**: Django Views, URL Configuration, and Templates — views and templates reused for PDF compilation.
- **Ch 12**: Building a REST API — contrasting JSON serialization with binary file downloads.
- **Ch 14**: Testing Your Django Applications — verifying status codes and binary response headers in test suites.
