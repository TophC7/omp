---
name: html-css-comprehensive-guide
description: "Knowledge base from \"HTML and CSS: The Comprehensive Guide\" by Jürgen Wolf. Use when applying modern HTML5 semantics, responsive CSS architecture, Flexbox, CSS Grid, preprocessors (Sass/SCSS), or client-side DOM/Ajax integration."
---

<!-- argument-hint: [topic, framework name, or chapter number] -->

# HTML and CSS: The Comprehensive Guide
**Author**: Jürgen Wolf | **Pages**: ~1,681 | **Chapters**: 20 | **Generated**: 2026-09-05

## How to Use This Skill

- **Without arguments** — Load core web architecture frameworks and mental models below.
- **With a topic** — Ask about `flexbox`, `grid`, `specificity`, `forms`, `selectors`, `picture`, or any indexed term; I will load and reference the matching chapter summary.
- **With chapter** — Request a specific chapter (e.g., `ch09`, `ch13`) to dive into its full reference tables, mental models, code examples, and worked exercises.
- **Browse** — Ask "what chapters do you have?" to inspect the complete table of contents.

When you ask about topics not fully covered in the Core Frameworks below, I will read the corresponding chapter file in `chapters/` before answering.

---

## Core Frameworks & Mental Models

### 1. The Three-Layer Separation of Concerns
- **Rule**: Keep content structure (HTML), presentation (CSS), and behavior (JavaScript) strictly isolated.
- **Application**:
  - HTML defines document nodes, landmark roles, and text semantics. Never use HTML tags (`<b>`, `<i>`, `<font>`) or inline styles (`style="..."`) for visual layout.
  - CSS dictates visual design, fluid layouts, color palettes, and responsive reflows. Bind styles via external `<link rel="stylesheet">` tags.
  - JavaScript provides client-side DOM manipulation, event handling, and background network requests (Ajax). Bind logic via external `<script defer>` tags without inline `onclick` attributes.

### 2. The Landmark Structural Blueprint
- **Rule**: Eliminate generic `<div>` soup in favor of explicit HTML5 structural landmarks.
- **Application**:
  - `<header>`: Site branding, top navigation, or article heading introductions.
  - `<nav>`: Major navigation link collections (main menu, breadcrumbs, table of contents).
  - `<main>`: The unique, non-repeating core payload of the document (exactly one visible per document).
  - `<article>`: Self-contained, independently syndicatable content units (blog posts, news stories, product cards).
  - `<section>`: Thematic groupings of content, typically introduced by an `<h2>`-`<h6>` heading.
  - `<aside>`: Tangentially related side content (sidebars, pull quotes, related links).
  - `<footer>`: Terminal metadata (copyright, legal links, author credits).

### 3. The Universal Border-Box Reset
- **Rule**: Always reset the box model globally to prevent padding and borders from breaking layout math.
- **Application**:
  ```css
  *, *::before, *::after {
    box-sizing: border-box;
  }
  ```
  - In the classic W3C model (`content-box`), declared `width` applies only to the content area; adding padding or border expands the element outward, causing multi-column layouts to wrap unexpectedly.
  - In the alternate model (`border-box`), declared `width` encompasses padding and borders inward, ensuring percentages and grid columns behave predictably.

### 4. The Cascade & Specificity Resolution Algorithm
- **Rule**: Specificity is evaluated as a 4-part tuple `(A, B, C, D)`. Compare columns left-to-right; a higher number in a higher column wins unconditionally:
  - **A (Inline)**: Declared in HTML `style="..."` attribute `(1, 0, 0, 0)`.
  - **B (ID Selectors)**: Number of `#id` tokens `(0, 1, 0, 0)`.
  - **C (Classes / Attributes / Pseudo-classes)**: Number of `.class`, `[attr]`, and `:pseudo-class` tokens `(0, 0, 1, 0)`.
  - **D (Elements / Pseudo-elements)**: Number of `tag` and `::pseudo-element` tokens `(0, 0, 0, 1)`.
- **Tie-Breaker**: When specificity scores are identical, the rule declared lowest (latest) in source order wins.
- **Importance Ladder**: User `!important` > Author `!important` > Author normal > User normal > User-Agent default.

### 5. Layout Engine Selection: Grid vs. Flexbox
- **Rule**: Use CSS Grid for two-dimensional layouts (rows AND columns simultaneously); use Flexbox for one-dimensional layouts (rows OR columns).
- **Application**:
  - **CSS Grid (`display: grid`)**: High-level page scaffolding, magazine layouts, and auto-fitting responsive card collections (`repeat(auto-fit, minmax(280px, 1fr))`).
  - **Flexbox (`display: flex`)**: Navigation bars, button groups, centering an item along both axes (`justify-content: center; align-items: center`), and form input rows.

### 6. Mobile-First Progressive Enhancement
- **Rule**: Author baseline CSS for small, single-column mobile viewports outside media queries; progressively enhance larger screens using `min-width` queries declared in `em` units.
- **Application**:
  - Eliminates desktop override bloat on mobile hardware.
  - Media queries measured in `em` (`@media (min-width: 48em)`) scale proportionally when visually impaired users zoom their default browser font size, unlike rigid pixel queries (`768px`).

### 7. Hardware-Accelerated Animation Pipeline
- **Rule**: Animate strictly compositor-level CSS properties (`transform` and `opacity`); never animate geometry (`top`, `left`, `width`, `height`, `margin`).
- **Application**: `transform: translate()` and `opacity` are processed directly on the GPU without triggering expensive layout recalculations or browser repaints, guaranteeing 60fps animations.

### 8. Event Delegation on Parent Containers
- **Rule**: Instead of attaching individual listeners to hundreds of child elements, attach a single listener to their shared parent container and inspect `event.target.closest()`.
- **Application**: Drastically reduces browser memory footprint, eliminates memory leaks, and automatically handles dynamically inserted child nodes without rebinding.

---

## Chapter Index

| Chapter | Title | Key Concepts & Frameworks |
|---|---|---|
| [ch01](chapters/ch01-html-universe.md) | Introduction to the HTML Universe | 3-Pillar architecture, static vs dynamic selection matrix, browser engines (Blink, WebKit, Gecko), W3C validation |
| [ch02](chapters/ch02-basic-html-structure.md) | Basic Structure of HTML Documents | DOM tree hierarchy, tags vs elements, void elements, LIFO nesting rules, `<!doctype html>`, `<html>`, `<head>`, `<body>` |
| [ch03](chapters/ch03-head-data-and-metadata.md) | Head Data of an HTML Document | Modern baseline `<head>`, `<title>` SERP rules, viewport configuration, `<meta>` robots, script loading (`async` / `defer`) |
| [ch04](chapters/ch04-visible-html-and-semantics.md) | The Visible Part of an HTML Document | Landmark structural architecture (`header`, `nav`, `main`, `article`, `section`), text markup (`strong`, `em`, `time`), entities |
| [ch05](chapters/ch05-tables-and-hyperlinks.md) | Tables and Hyperlinks | Two-dimensional table semantics (`thead`, `tbody`, `th scope`), cell spans, secure external links (`rel="noopener"`), anchors |
| [ch06](chapters/ch06-graphics-and-multimedia.md) | Graphics and Multimedia | Responsive art direction (`<picture>`, `srcset`), CLS prevention (explicit dimensions), SVG vectors, native `<video>` & `<audio>` |
| [ch07](chapters/ch07-forms-and-interactive-elements.md) | HTML Forms and Interactive Elements | Accessible form control binding (`<label for>`), `<fieldset>`, GET vs POST security, HTML5 input constraints, `<details>`, `<dialog>` |
| [ch08](chapters/ch08-introduction-to-css.md) | Introduction to Cascading Style Sheets | Modular CSS, ruleset anatomy, external vs embedded vs inline styles, `@import` pitfalls, media-specific stylesheets (`print`) |
| [ch09](chapters/ch09-css-selectors.md) | The Selectors of CSS | Comprehensive selector taxonomy, attribute pattern matching, structural `:nth-child(An+B)`, generated content (`::before`), combinators |
| [ch10](chapters/ch10-inheritance-and-cascading.md) | Inheritance and Cascading | Inherited vs non-inherited properties, cascade resolution algorithm, `(A,B,C,D)` specificity scoring, `!important` origin ladder, units |
| [ch11](chapters/ch11-css-box-model.md) | The Box Model of CSS | Classic vs alternate box model, universal `border-box` reset, margin collapsing prevention, box styling, shadows, border radius |
| [ch12](chapters/ch12-css-positioning-and-flexbox.md) | CSS Positioning and Flexbox | Positioning schemes (`static`, `relative`, `absolute`, `fixed`, `sticky`), stacking contexts (`z-index`), Flexbox axis distribution |
| [ch13](chapters/ch13-responsive-layouts-and-grid.md) | Creating Responsive Layouts with CSS | Ethan Marcotte's 3 pillars, mobile-first progressive enhancement, `em` breakpoints, CSS Grid scaffolding (`fr`, `minmax`, areas) |
| [ch14](chapters/ch14-styling-with-css.md) | Styling with CSS | Web font optimization (`@font-face`, `font-display: swap`), multi-column text, 2D/3D transforms, 60fps transitions, form restyling |
| [ch15](chapters/ch15-testing-and-organizing.md) | Testing and Organizing | W3C validation, feature queries (`@supports`), CSS Reset vs Normalization (Normalize.css), modular bundle architecture |
| [ch16](chapters/ch16-sass-and-scss.md) | The CSS Preprocessor Sass and SCSS | SCSS compilation, variables, parent selector `&`, mixins vs placeholder `@extend`, color functions, control directives, partials |
| [ch17](chapters/ch17-javascript-introduction.md) | A Brief Introduction to JavaScript | V8/SpiderMonkey runtimes, `"use strict"`, `const`/`let` block scope, primitive types, truthy/falsy, strict equality (`===`), loops |
| [ch18](chapters/ch18-javascript-arrays-functions-objects.md) | Arrays, Functions, and Objects in JS | First-class functions, arrow functions vs lexical `this`, array pipelines (`filter`, `map`, `reduce`), ES6 classes, collections |
| [ch19](chapters/ch19-dom-manipulation-and-events.md) | Changing Web Pages Dynamically | DOM selection (`querySelector`), safe element creation (`textContent`), event propagation (capturing/bubbling), event delegation |
| [ch20](chapters/ch20-ajax-and-json.md) | An Introduction to Ajax | Asynchronous HTTP lifecycle, `XMLHttpRequest` state machine, Promise-based `fetch()`, JSON serialization, Same-Origin Policy |

---

## Topic Index

- **Accessibility & Screen Readers** → [ch01](chapters/ch01-html-universe.md), [ch02](chapters/ch02-basic-html-structure.md), [ch04](chapters/ch04-visible-html-and-semantics.md), [ch05](chapters/ch05-tables-and-hyperlinks.md), [ch07](chapters/ch07-forms-and-interactive-elements.md)
- **Ajax & Asynchronous Communication** → [ch20](chapters/ch20-ajax-and-json.md)
- **Animations & Transitions** → [ch14](chapters/ch14-styling-with-css.md)
- **Arrays & Functional Pipelines** → [ch18](chapters/ch18-javascript-arrays-functions-objects.md)
- **Attribute Selectors** → [ch09](chapters/ch09-css-selectors.md)
- **Box Model (`box-sizing`)** → [ch11](chapters/ch11-css-box-model.md)
- **Browser Engines (Blink, WebKit, Gecko)** → [ch01](chapters/ch01-html-universe.md), [ch15](chapters/ch15-testing-and-organizing.md)
- **Cascade & Specificity** → [ch10](chapters/ch10-inheritance-and-cascading.md)
- **Character Encoding (UTF-8) & Entities** → [ch01](chapters/ch01-html-universe.md), [ch03](chapters/ch03-head-data-and-metadata.md), [ch04](chapters/ch04-visible-html-and-semantics.md)
- **Combinators (Child, Sibling, Descendant)** → [ch09](chapters/ch09-css-selectors.md)
- **CSS Grid Layout** → [ch13](chapters/ch13-responsive-layouts-and-grid.md)
- **Cumulative Layout Shift (CLS)** → [ch06](chapters/ch06-graphics-and-multimedia.md)
- **Document Object Model (DOM)** → [ch02](chapters/ch02-basic-html-structure.md), [ch17](chapters/ch17-javascript-introduction.md), [ch19](chapters/ch19-dom-manipulation-and-events.md)
- **Event Handling & Delegation** → [ch19](chapters/ch19-dom-manipulation-and-events.md)
- **Feature Queries (`@supports`)** → [ch15](chapters/ch15-testing-and-organizing.md)
- **Fetch API** → [ch20](chapters/ch20-ajax-and-json.md)
- **Flexbox Layout** → [ch12](chapters/ch12-css-positioning-and-flexbox.md)
- **Forms & Native Validation** → [ch07](chapters/ch07-forms-and-interactive-elements.md)
- **Head Metadata (`<title>`, Viewport, Robots)** → [ch03](chapters/ch03-head-data-and-metadata.md)
- **Hyperlinks & Security (`rel="noopener"`)** → [ch05](chapters/ch05-tables-and-hyperlinks.md)
- **Images & Art Direction (`<picture>`, `srcset`)** → [ch06](chapters/ch06-graphics-and-multimedia.md)
- **Inheritance (`inherit`, `initial`, `unset`)** → [ch10](chapters/ch10-inheritance-and-cascading.md)
- **Interactive Elements (`<details>`, `<dialog>`)** → [ch07](chapters/ch07-forms-and-interactive-elements.md)
- **JSON Serialization** → [ch20](chapters/ch20-ajax-and-json.md)
- **Margin Collapsing** → [ch11](chapters/ch11-css-box-model.md)
- **Media Queries & Breakpoints** → [ch13](chapters/ch13-responsive-layouts-and-grid.md)
- **Mobile-First Design** → [ch13](chapters/ch13-responsive-layouts-and-grid.md)
- **Multi-Column Text Layout** → [ch14](chapters/ch14-styling-with-css.md)
- **Object-Oriented JavaScript (Classes)** → [ch18](chapters/ch18-javascript-arrays-functions-objects.md)
- **Positioning (`absolute`, `fixed`, `sticky`, `relative`)** → [ch12](chapters/ch12-css-positioning-and-flexbox.md)
- **Pseudo-Classes & Pseudo-Elements** → [ch09](chapters/ch09-css-selectors.md)
- **Reset vs. Normalize** → [ch15](chapters/ch15-testing-and-organizing.md)
- **Sass / SCSS Preprocessors** → [ch16](chapters/ch16-sass-and-scss.md)
- **Script Loading (`async`, `defer`)** → [ch03](chapters/ch03-head-data-and-metadata.md), [ch17](chapters/ch17-javascript-introduction.md)
- **Semantic Landmarks (`header`, `main`, `article`, `nav`)** → [ch04](chapters/ch04-visible-html-and-semantics.md)
- **Stacking Context & `z-index`** → [ch12](chapters/ch12-css-positioning-and-flexbox.md)
- **SVG Vector Graphics** → [ch06](chapters/ch06-graphics-and-multimedia.md)
- **Tables (`table`, `th scope`, `colspan`)** → [ch05](chapters/ch05-tables-and-hyperlinks.md), [ch14](chapters/ch14-styling-with-css.md)
- **Transforms (2D/3D)** → [ch14](chapters/ch14-styling-with-css.md)
- **Typography & Web Fonts (`@font-face`)** → [ch14](chapters/ch14-styling-with-css.md)
- **Units (`rem`, `em`, `px`, `vw`, `vh`, `fr`)** → [ch10](chapters/ch10-inheritance-and-cascading.md), [ch13](chapters/ch13-responsive-layouts-and-grid.md)
- **Validation (W3C)** → [ch01](chapters/ch01-html-universe.md), [ch15](chapters/ch15-testing-and-organizing.md)
- **Video & Audio (`<video>`, `<audio>`, `<track>`)** → [ch06](chapters/ch06-graphics-and-multimedia.md)

---

## Supporting Files

- [glossary.md](glossary.md) — Comprehensive alphabetical definitions for all key HTML, CSS, and JS terms.
- [patterns.md](patterns.md) — Reusable implementation templates and architecture patterns.
- [cheatsheet.md](cheatsheet.md) — High-density decision rules, layout trees, thresholds, and diagnostic smells.

---

## Scope & Limits

This skill encapsulates client-side web development fundamentals (HTML5, CSS, preprocessors, DOM, Ajax) as taught by Jürgen Wolf. For backend server programming (Node.js, PHP, Python, databases) or advanced reactive frontend component frameworks (React, Svelte, Vue), combine this skill with project-specific tooling or dedicated framework skills.
