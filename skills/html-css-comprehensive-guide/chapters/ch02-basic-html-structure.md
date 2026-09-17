# Chapter 2: Basic Structure of HTML and HTML Documents

## Core Idea
An HTML document is a serialized tree structure parsed by the browser runtime into the Document Object Model (DOM). Proper hierarchical nesting (LIFO closing order), standard doctype declaration, and explicit containment within `<html>`, `<head>`, and `<body>` are required for predictable rendering across all user agents.

## Frameworks Introduced
- **The DOM Tree Hierarchy (Parent-Child-Sibling Model)**:
  - When to use: When designing document architecture or writing selectors and scripts.
  - How: Treat `<html>` as the single document root. Directly below the root, place only two child nodes: `<head>` (metadata, links, scripts) and `<body>` (rendered content). Every nested element becomes a child node with a distinct ancestor-descendant chain.
- **Strict LIFO Nesting Rule (Last In, First Out)**:
  - When to use: Every time tags are opened inside an existing element.
  - How: The tag opened most recently must be closed first. Overlapping tags (e.g., `<p>Text <b>bold</p></b>`) trigger browser repair heuristics, creating diverging DOM trees across different rendering engines.
- **Void Element Protocol**:
  - When to use: When placing content-free or standalone elements (`<br>`, `<img>`, `<meta>`, `<link>`, `<hr>`, `<input>`).
  - How: Never provide a closing tag for void elements. In modern HTML5, trailing slashes (`<br />`) are optional syntactic noise inherited from XHTML; standard `<br>` is preferred and universally supported.

## Key Concepts
- **HTML Tag**: Markup delimiter surrounded by angle brackets (e.g., `<p>` or `</p>`). Tags mark the boundaries of elements.
- **HTML Element**: The complete conceptual node consisting of the opening tag, attributes, child content/text, and the closing tag (e.g., `<p class="lead">Hello</p>`).
- **Void (Standalone) Element**: An element that cannot contain child nodes or text and requires no closing tag (e.g., `<meta>`, `<link>`, `<img>`, `<br>`, `<hr>`, `<input>`).
- **HTML Attribute**: Name-value pair (`name="value"`) placed exclusively inside the opening tag of an element to provide configuration, metadata, or hooks.
- **Global Attributes**: Attributes permitted on virtually every HTML element (e.g., `id`, `class`, `lang`, `title`, `dir`, `hidden`, `style`).
- **Document Type Declaration (`<!doctype html>`)**: An instruction informing the browser engine to render the document in modern Standards Mode rather than Quirks Mode.
- **Document Object Model (DOM)**: An object-oriented in-memory tree representation of the HTML document exposed to scripting languages (JavaScript) where each element is an inspectable node.

## Mental Models
- **Think of HTML as Russian Matryoshka Nesting Dolls**: Every inner doll must be completely enclosed inside its outer doll before the outer doll's lid can close. Dolls cannot intersect or straddle boundaries.
- **Use "Rectangular Box Composition"**: Every visible element in `<body>` generates a rectangular bounding box. The web layout is not a freeform canvas; it is a nested set of boxes stacked vertically, arranged horizontally, or nested within containers.

## Anti-patterns
- **Tag Overlapping (Cross-Nesting)**: Writing `<p>This is <b>broken markup.</p></b>`. Forces the browser parser into error-recovery mode, producing unpredictable DOM tree structures.
- **Relying on Optional Tag Omission**: Leaving off `</html>`, `</body>`, or `</p>` because HTML5 allows it in certain contexts. Makes team code reviews error-prone, degrades diff readability, and risks syntax breaks when refactoring deeply nested structures.
- **Misusing `<br>` for Vertical Spacing**: Inserting multiple `<br><br><br>` tags to push content down the page. Spacing is the strict responsibility of CSS (`margin` / `padding`). `<br>` exists exclusively for semantic line breaks (e.g., poetry, mailing addresses).
- **Putting Secrets in HTML Comments**: Writing `<!-- TODO: remove database password admin123 -->`. HTML comments are delivered across the network in plaintext and are immediately readable via browser "View Source" or DevTools.

## Code Examples
```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8">
    <title>Semantic DOM Hierarchy Demonstration</title>
  </head>
  <body>
    <!-- Main content container -->
    <main>
      <h1>Document Object Model Overview</h1>
      <p>HTML documents parse into a tree of <strong>nodes</strong>.</p>
      
      <!-- Proper nesting of void and paired tags -->
      <p>
        Visit our reference library:<br>
        <a href="https://example.com" title="External Library">Documentation Portal</a>
      </p>
    </main>
  </body>
</html>
```
- **What it demonstrates**: Standard HTML5 skeleton showing strict LIFO nesting, global `lang` attribute, void element (`<br>`), attribute quoting, and structured comment usage.

## Reference Tables

### Document Skeleton Hierarchy
| Element | Category | Direct Parent | Permitted Direct Children | Purpose |
|---|---|---|---|---|
| `<!doctype html>` | Declaration | None (Prologue) | None | Forces standard standards-compliant rendering mode |
| `<html>` | Root Element | Document | `<head>`, followed by `<body>` | Top-level container for all document nodes |
| `<head>` | Metadata Container | `<html>` | `<title>`, `<meta>`, `<link>`, `<style>`, `<script>`, `<base>` | Machine-readable document metadata, styles, and assets |
| `<body>` | Renderable Container | `<html>` | Flow content (headings, sections, paragraphs, media, scripts) | Human-visible document content rendered in viewport |

### Void Elements vs. Normal Elements
| Element Type | Closing Tag Permitted? | Content / Children Allowed? | Examples |
|---|---|---|---|
| **Normal Element** | Required (or strictly recommended) | Yes (text, child elements, or empty) | `<html>`, `<head>`, `<body>`, `<h1>`-`<h6>`, `<p>`, `<div>`, `<span>`, `<a>` |
| **Void Element** | Forbidden (never use `</img>` or `</br>`) | No (never contains inner text or children) | `<img>`, `<br>`, `<hr>`, `<input>`, `<meta>`, `<link>`, `<source>`, `<area>` |

## Worked Example
A junior author writes an un-validated blog post snippet:
```html
<p>Welcome to our site! Check our <a href=blog.html>latest article<b>here</p></a></b>
```
**Step-by-step correction to valid structure:**
1. **Attribute quoting**: Add quotes around attribute value `href="blog.html"` for backward compatibility and parsing safety.
2. **Untangle cross-nesting**: Identify opening order: `<p>`, `<a>`, `<b>`.
3. **Apply LIFO closing order**:
   - `<b>` was opened last; close it first: `</b>`.
   - `<a>` was opened before `<b>`; close it next: `</a>`.
   - `<p>` was opened first; close it last: `</p>`.
4. **Resulting valid markup**:
```html
<p>Welcome to our site! Check our <a href="blog.html">latest article <b>here</b></a>.</p>
```

## Key Takeaways
1. `<!doctype html>` is not an HTML element; it is an instruction that prevents quirks mode rendering.
2. Always declare `lang` on `<html>` to ensure screen readers apply correct pronunciation rules and search engines index the language accurately.
3. Void elements must never have closing tags or inner content.
4. Always wrap attribute values in double quotation marks (`attribute="value"`).
5. HTML comments (`<!-- ... -->`) are client-visible; never commit sensitive technical notes or credentials inside them.

## Connects To
- **Ch 01**: Extends validation theory into practical DOM structure rules.
- **Ch 03**: Explores the `<head>` node and its critical metadata elements.
- **Ch 19**: JavaScript accesses and manipulates this exact node tree via the DOM API (`querySelector`, `appendChild`).
