# Chapter 4: The Visible Part of an HTML Document

## Core Idea
The `<body>` represents the human- and machine-visible payload of an HTML document. Replacing generic, presentational `<div>` soup with HTML5 semantic landmarks (`<header>`, `<nav>`, `<main>`, `<article>`, `<section>`, `<aside>`, `<footer>`) enables screen readers to navigate via landmark regions, allows web crawlers to isolate primary content from boilerplate, and creates durable, maintainable CSS styling hooks.

## Frameworks Introduced
- **The Landmark Structural Framework**:
  - When to use: Architecting any page layout before writing CSS or content.
  - How: Wrap top-level introductory banners and site logos in `<header>`; enclose primary page links inside `<nav>`; wrap the central, page-unique content block in `<main>` (exactly one visible per document); encapsulate standalone, syndicatable content units in `<article>`; organize thematic sub-topics with `<section>` (each section should ideally contain its own heading `<h2>`-`<h6>`); place secondary sidebars, related links, or callouts in `<aside>`; and wrap copyright, legal, and author details in `<footer>`.
- **Semantic Text Markup Decision Framework**:
  - When to use: Formatting words, dates, quotations, and code within paragraphs.
  - How:
    - Use `<strong>` for content of strong importance, seriousness, or urgency; use `<b>` purely for drawing attention without altering semantic weight.
    - Use `<em>` for verbal stress/emphasis that shifts sentence meaning; use `<i>` for alternative voice, technical terms, or idiomatic phrasing.
    - Use `<time datetime="YYYY-MM-DD">` for machine-readable dates and timestamps.
    - Use `<code>` for inline snippets, `<kbd>` for user keyboard input, and `<samp>` for computer program output.
- **Div-to-Semantics Migration Pattern**:
  - When to use: Auditing legacy markup or refactoring CMS templates.
  - How: Replace `<div id="header">` with `<header>`, `<div id="nav">` with `<nav>`, `<div id="content">` with `<main>`, `<div class="post">` with `<article>`, and `<div id="footer">` with `<footer>`. Retain `<div>` strictly as a semantically neutral styling wrapper for CSS layout requirements (e.g., flex or grid centering containers).

## Key Concepts
- **`<main>`**: Landmark element representing the dominant, non-repeating content of the document body. Only one `<main>` may be visible per document.
- **`<article>`**: Self-contained composition independently distributable or reusable (e.g., blog post, news article, forum reply, product card).
- **`<section>`**: Thematic grouping of content, typically introduced by an explicit heading (`<h2>`-`<h6>`).
- **`<aside>`**: Content tangentially related to the surrounding context, such as sidebars, pull quotes, advertising, or related reading.
- **`<figure>` and `<figcaption>`**: Self-contained visual or programmatic unit (diagram, photo, code block) with an optional caption.
- **`<dl>`, `<dt>`, `<dd>`**: Description list establishing key-value, glossary, or metadata pairs (Description List, Description Term, Description Details).
- **`<time>`**: Semantic element wrapping dates or clock times; machine value declared in the `datetime` attribute.
- **HTML Character Entities**: Escape sequences (`&name;` or `&#number;`) representing reserved markup characters (`&lt;`, `&gt;`, `&amp;`, `&quot;`) or typographic glyphs (`&copy;`, `&shy;`, `&nbsp;`).

## Mental Models
- **Think of Semantic HTML as a Newspaper Blueprint**: A newspaper has a top masthead (`<header>`), an index of sections (`<nav>`), independent editorial stories (`<article>`), themed subsections (`<section>`), side commentary and advertisements (`<aside>`), and publishing imprints at the bottom (`<footer>`). A blind reader or automated scanning indexer navigates directly to specific editorial desks without reading every printing press line.
- **Use "Semantic Meaning Over Browser Default Appearance"**: Never choose `<blockquote>` simply because you want text indented; never choose `<b>` simply because you want bold weight. Choose tags based on what the content *is*, and use CSS to control how the content *looks*.

## Anti-patterns
- **"Div Soup" Architecture**: Constructing entire applications out of nested `<div>` tags (`<div class="header"><div class="nav-wrapper"><div class="content">...</div></div></div>`). Destroys document accessibility, renders screen reader landmark navigation useless, and degrades SEO indexing.
- **Heading Level Skipping**: Jumping from `<h1>` directly to `<h4>` to achieve smaller visual typography. Headings create an outline tree; skipping levels confuses assistive technology. Style heading sizes via CSS `font-size`.
- **Misusing `<br>` and `&nbsp;` for Layout Grid**: Writing `<br><br>` to create paragraph gaps or `&nbsp;&nbsp;&nbsp;&nbsp;` to indent list items. Use CSS `margin`, `padding`, or `text-indent`.
- **Using `<time>` without `datetime`**: Writing `<time>Yesterday</time>`. Without the standard ISO `datetime="2026-09-04"` attribute, machines and calendar crawlers cannot resolve the relative phrase into an absolute timestamp.

## Code Examples
```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>The Cooking Journal</title>
  </head>
  <body>
    <!-- Top-level site banner and primary navigation -->
    <header>
      <h1>The Cooking Journal</h1>
      <nav aria-label="Primary Navigation">
        <ul>
          <li><a href="/">Home</a></li>
          <li><a href="/recipes">Recipes</a></li>
          <li><a href="/about">About</a></li>
        </ul>
      </nav>
    </header>

    <!-- Document unique payload -->
    <main>
      <!-- Standalone article -->
      <article>
        <header>
          <h2>Homemade Madagascar Vanilla Sauce</h2>
          <p>Published on <time datetime="2026-09-05">September 5, 2026</time> by <address style="display:inline;"><a href="mailto:chef@example.com">Chef Julia</a></address></p>
        </header>

        <p>A classic custard sauce relies on gentle heat and patience. <em>Never</em> boil the milk once the egg yolks are incorporated, or the mixture will curdle.</p>

        <figure>
          <img src="custard.jpg" alt="Rich golden vanilla custard swirling in a glass bowl" width="600" height="400">
          <figcaption>Figure 1: Desired consistency coating the back of a wooden spoon.</figcaption>
        </figure>

        <section>
          <h3>Ingredients & Specifications</h3>
          <dl>
            <dt>Milk Base</dt>
            <dd>500 ml whole milk (minimum 3.5% fat content)</dd>
            <dt>Vanilla</dt>
            <dd>1 whole Madagascar vanilla bean, split lengthwise</dd>
          </dl>
        </section>
      </article>

      <!-- Tangential complementary content -->
      <aside>
        <h3>Related Guides</h3>
        <ul>
          <li><a href="/custard-tips">Fixing Broken Custards</a></li>
          <li><a href="/bean-sourcing">Grading Vanilla Beans</a></li>
        </ul>
      </aside>
    </main>

    <!-- Global document footer -->
    <footer>
      <p>&copy; 2026 The Cooking Journal. All rights reserved.</p>
    </footer>
  </body>
</html>
```
- **What it demonstrates**: Full semantic HTML5 document showcasing `<header>`, `<nav>`, `<main>`, `<article>`, `<section>`, `<aside>`, `<footer>`, `<figure>`, `<figcaption>`, `<dl>`, `<time>`, and proper character entities (`&copy;`).

## Reference Tables

### HTML5 Semantic Structural Landmarks
| Element | Description | Typical Use Case | Landmark Role |
|---|---|---|---|
| `<header>` | Introductory container for page or section | Logo, headings, author info, search box | `banner` (when top-level) |
| `<nav>` | Block containing major navigation links | Primary site menu, table of contents, pagination | `navigation` |
| `<main>` | Core, non-repeated content of document | Central article, search results, primary tool | `main` |
| `<article>` | Independent, self-contained unit | News item, blog post, forum card, product review | `article` |
| `<section>` | Thematic grouping of content | Chapter sub-parts, feature blocks, tab panels | `region` (with accessible name) |
| `<aside>` | Tangentially related secondary content | Sidebar, glossary callout, related links, ads | `complementary` |
| `<footer>` | Terminal container for page or section | Copyright, author links, privacy policy, sitemap | `contentinfo` (when top-level) |

### Semantic Text & Formatting Elements
| Element | Semantic Purpose | Visual Default (Browsers) | CSS Replacement if purely aesthetic |
|---|---|---|---|
| `<strong>` | High importance, seriousness, urgency | Bold | `font-weight: bold;` |
| `<b>` | Stylistic offset / keyword without added importance | Bold | `font-weight: bold;` |
| `<em>` | Stressed emphasis altering spoken inflection | Italic | `font-style: italic;` |
| `<i>` | Alternate voice, technical term, foreign phrase | Italic | `font-style: italic;` |
| `<mark>` | Reference highlighting / search match | Yellow background | `background-color: yellow;` |
| `<code>` | Inline fragment of computer programming code | Monospace font | `font-family: monospace;` |
| `<pre>` | Preformatted text preserving spaces and line breaks | Monospace + preserved whitespace | `white-space: pre;` |
| `<kbd>` | User keyboard or voice input instruction | Monospace | `font-family: monospace;` |
| `<time>` | Machine-readable date or clock time (`datetime`) | Normal text | None (semantic hook) |
| `<del>` / `<ins>` | Editorial deletions and insertions | Strikethrough / Underline | `text-decoration: line-through;` |

### Essential HTML Reserved Character Entities
| Character | Literal Meaning | Named Entity | Numeric Entity | Why Entity is Required |
|---|---|---|---|---|
| `<` | Less than | `&lt;` | `&#60;` | Prevents parser from interpreting character as tag opener |
| `>` | Greater than | `&gt;` | `&#62;` | Prevents parser confusion when closing tag constructs |
| `&` | Ampersand | `&amp;` | `&#38;` | Prevents parser from interpreting character as entity opener |
| `"` | Double quotation | `&quot;` | `&#34;` | Prevents string termination inside HTML attribute values |
| `'` | Single quotation | `&apos;` | `&#39;` | Prevents string termination in single-quoted attributes |
| ` ` | Non-breaking space | `&nbsp;` | `&#160;` | Enforces explicit space and prevents word-wrapping line breaks |

## Worked Example
A legacy recipe template uses old presentational markup:
```html
<div id="wrapper">
  <div class="headline">Grandma's Apple Pie</div>
  <div class="date">Posted: Oct 12, 2023</div>
  <div class="story">A wonderful heritage recipe...</div>
  <div class="ingredients-title">Ingredients</div>
  <div class="ing-item">- 6 Granny Smith Apples</div>
  <div class="ing-item">- 1 cup white sugar</div>
</div>
```
**Step-by-step refactoring to modern HTML5 semantics:**
1. **Container & Heading**: Replace `<div class="headline">` with an `<article>` container headed by an `<h1>`.
2. **Metadata & Timestamp**: Convert `<div class="date">` into a semantic `<time datetime="2023-10-12">`.
3. **Paragraph flow**: Convert `<div class="story">` into standard `<p>`.
4. **List Structure**: Replace the hyphenated ingredient divs with an unordered list (`<ul>` and `<li>`) nested inside an ingredients `<section>`.
5. **Resulting clean markup**:
```html
<article>
  <header>
    <h1>Grandma's Apple Pie</h1>
    <p>Posted: <time datetime="2023-10-12">October 12, 2023</time></p>
  </header>
  <p>A wonderful heritage recipe...</p>
  <section>
    <h2>Ingredients</h2>
    <ul>
      <li>6 Granny Smith Apples</li>
      <li>1 cup white sugar</li>
    </ul>
  </section>
</article>
```

## Key Takeaways
1. Use semantic landmarks (`<header>`, `<nav>`, `<main>`, `<article>`, `<section>`, `<aside>`, `<footer>`) to give layout regions explicit machine meaning.
2. Maintain a strict single `<main>` element per document for the page's primary payload.
3. Use `<article>` for self-contained, shareable content; use `<section>` for thematic sub-chapters with headings.
4. Distinguish between semantic importance (`<strong>`, `<em>`) and typographic styling (`<b>`, `<i>`, CSS).
5. Always escape reserved characters (`<`, `>`, `&`, `"`) with HTML entities when outputting raw text.

## Connects To
- **Ch 02**: Provides the concrete display elements that populate the `<body>` node.
- **Ch 05**: Expands tabular and relational text structuring with `<table>` and `<a>`.
- **Ch 08**: Demonstrates how CSS element selectors bind directly to these semantic tags.
- **Ch 09**: Shows how CSS combinators leverage this clean ancestor-descendant hierarchy.
