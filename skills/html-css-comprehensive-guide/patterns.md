# Practical Architecture & Design Patterns

Techniques, implementation patterns, and design algorithms extracted from *HTML and CSS: The Comprehensive Guide* by Jürgen Wolf.

---

## 1. Universal Border-Box Reset
**When to use**: The foundational first declaration of every web project.
**How**:
```css
*, *::before, *::after {
  box-sizing: border-box;
}
```
**Trade-offs**: Absorbs padding and border dimensions directly into declared element widths, preventing horizontal scrollbars and unexpected multi-column line breaks. Slightly modifies legacy behavior if integrating third-party widgets expecting classic `content-box` (remedied by isolating widgets with `box-sizing: content-box`).

---

## 2. Accessible Semantic Landmark Architecture
**When to use**: Scaffolding any top-level HTML document layout.
**How**:
Replace non-semantic `<div>` containers with native landmark elements:
```html
<header class="site-header">...</header>
<nav aria-label="Primary Navigation">...</nav>
<main id="main-content">
  <article>
    <header><h1>Title</h1></header>
    <section><h2>Sub-topic</h2></section>
  </article>
  <aside>...</aside>
</main>
<footer class="site-footer">...</footer>
```
**Trade-offs**: Enhances screen reader navigation, improves automated SEO indexing, and provides stable CSS hooks without extra classes. Requires developers to understand semantic nuances (e.g., `<article>` vs. `<section>`).

---

## 3. Cumulative Layout Shift (CLS) Prevention for Media
**When to use**: Embedding any raster photo, video, or iframe.
**How**:
Always supply explicit `width` and `height` attributes directly on the HTML tag, combined with responsive CSS rules:
```html
<img src="photo.jpg" alt="Description" width="800" height="600" loading="lazy">
```
```css
img, video, iframe {
  max-width: 100%;
  height: auto;
  display: block;
}
```
**Trade-offs**: Modern browser engines calculate the intrinsic aspect ratio (`800 / 600`) before the image payload downloads, reserving the exact layout box and eliminating sudden jumping as the user scrolls. Requires knowing original media dimensions during authoring.

---

## 4. Responsive Art Direction via `<picture>`
**When to use**: Serving tailored image crops, resolutions, and next-gen formats (WebP/AVIF) across diverse devices.
**How**:
```html
<picture>
  <!-- Desktop: Wide banner in WebP -->
  <source media="(min-width: 64em)" srcset="banner-wide.webp" type="image/webp">
  <source media="(min-width: 64em)" srcset="banner-wide.jpg">
  
  <!-- Mobile: Tight square crop in WebP -->
  <source srcset="banner-square.webp" type="image/webp">
  
  <!-- Universal Fallback -->
  <img src="banner-square.jpg" alt="Artisan bakery storefront" width="600" height="600">
</picture>
```
**Trade-offs**: Minimizes mobile data consumption and guarantees optimal visual focal points. Requires generating multiple image variants during asset preparation.

---

## 5. Relative Parent Anchor with Absolute Child
**When to use**: Positioning notification badges, tooltips, overlay close buttons, or drop-down panels.
**How**:
Apply `position: relative` to the container element without offsets; apply `position: absolute` to the child:
```css
.card {
  position: relative;
}
.badge {
  position: absolute;
  top: 0.5rem;
  right: 0.5rem;
}
```
**Trade-offs**: Guarantees the child positions relative to its immediate card boundary rather than flying to the viewport edges. The child is removed from normal flow, so parent containers will not expand height to fit the child.

---

## 6. Intrinsic Auto-Fitting Card Grid
**When to use**: Product listings, blog cards, or photo galleries adapting seamlessly from mobile to desktop without media queries.
**How**:
```css
.card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1.5rem;
}
```
**Trade-offs**: Eliminates dozens of hard-coded media query breakpoints; dynamically wraps and distributes free space proportionally. Requires cards to look visually balanced across any dynamic width between 280px and the full viewport.

---

## 7. Mobile-First Progressive Enhancement
**When to use**: Structuring all global page stylesheets and component rulesets.
**How**:
Write base styles for single-column mobile viewports outside any media query. Add progressive enhancements using `min-width` queries measured in `em`:
```css
/* Mobile baseline */
.layout {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

/* Tablet & Desktop */
@media (min-width: 48em) { /* 768px / 16px = 48em */
  .layout {
    display: grid;
    grid-template-columns: 1fr 300px;
    gap: 2rem;
  }
}
```
**Trade-offs**: Mobile devices parse minimal, clean CSS without downloading or overriding heavy desktop rules; `em` units ensure layout reflows if the user increases browser font size. Requires discipline to resist designing desktop-first.

---

## 8. Hardware-Accelerated 60fps Transitions
**When to use**: Micro-interactions, button hover effects, modal drawer slides, and card elevation.
**How**:
Animate strictly compositor properties (`transform` and `opacity`); avoid animating geometry (`width`, `height`, `top`, `left`, `margin`):
```css
.card {
  transition: transform 0.2s cubic-bezier(0.2, 0, 0, 1), box-shadow 0.2s ease;
  will-change: transform;
}
.card:hover {
  transform: translateY(-4px) scale(1.01);
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
}
```
**Trade-offs**: Ensures buttery smooth 60fps animations on mobile GPUs without triggering expensive CPU layout recalculations or paint cycles. The animated element preserves its static flow footprint.

---

## 9. Progressive Enhancement via `@supports`
**When to use**: Adopting cutting-edge CSS properties without breaking legacy browser clients.
**How**:
```css
/* Fallback for all browsers */
.overlay {
  background-color: rgba(15, 23, 42, 0.9);
}

/* Modern enhancement */
@supports (backdrop-filter: blur(10px)) {
  .overlay {
    background-color: rgba(15, 23, 42, 0.6);
    backdrop-filter: blur(10px);
  }
}
```
**Trade-offs**: Pure native CSS feature detection with zero runtime JavaScript overhead. Requires testing both branches to ensure fallback visual contrast is accessible.

---

## 10. DRY Component Architecture with SCSS
**When to use**: Generating design system variations and eliminating duplicated compiled CSS.
**How**:
Pair `%placeholder` for static shared geometries with parameterized `@mixin` for variable color tokens:
```scss
%btn-base {
  display: inline-flex;
  align-items: center;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  font-weight: 600;
}

@mixin btn-theme($color) {
  background-color: $color;
  border: 1px solid darken($color, 10%);
  &:hover { background-color: darken($color, 8%); }
}

.btn-primary {
  @extend %btn-base;
  @include btn-theme(#0284c7);
}
```
**Trade-offs**: `@extend` keeps compiled CSS payload tiny by grouping selectors, while `@mixin` handles mathematical color derivation. Must avoid extending complex nested class selectors.

---

## 11. Event Delegation on Parent Containers
**When to use**: Managing click or input events across large, dynamic, or frequently re-rendered item lists.
**How**:
Attach a single listener to the common parent element and inspect the event target using `.closest()`:
```javascript
taskList.addEventListener("click", (event) => {
  const deleteBtn = event.target.closest(".btn-delete");
  if (deleteBtn) {
    const item = deleteBtn.closest(".task-item");
    item.remove();
  }
});
```
**Trade-offs**: Reduces memory overhead from hundreds of closures to one single listener; dynamically inserted child nodes work immediately without manual rebinding. Events must bubble (non-bubbling events like `blur`/`focus` require capturing phase or `focusin`).

---

## 12. Safe XSS-Proof DOM Construction
**When to use**: Rendering dynamic text from user inputs, search fields, or external API payloads.
**How**:
Never assign untrusted strings to `innerHTML`. Use `document.createElement()` and `textContent`:
```javascript
function createNotification(userText) {
  const card = document.createElement("div");
  card.classList.add("notification-card");
  
  const p = document.createElement("p");
  p.textContent = userText; // Safe: escapes HTML characters automatically
  
  card.appendChild(p);
  document.body.appendChild(card);
}
```
**Trade-offs**: Completely neutralizes Cross-Site Scripting (XSS) injection vectors. Slightly more verbose than string template concatenation (mitigated by helper utilities or `<template>` cloning).

---

## 13. Asynchronous Data Fetch with Defensive Parsing
**When to use**: Fetching server data or posting form payloads without page reloads.
**How**:
```javascript
async function loadEndpoint(url) {
  try {
    const response = await fetch(url);
    if (!response.ok) {
      throw new Error(`HTTP Error ${response.status}`);
    }
    const data = await response.json();
    renderData(data);
  } catch (err) {
    console.error("Network or parse error:", err);
    renderErrorUI("Failed to load server data.");
  }
}
```
**Trade-offs**: Decouples UI presentation from backend page lifecycles; handles network dropouts and malformed JSON payloads gracefully without crashing the script thread. Requires handling loading indicators and error states in UI.
