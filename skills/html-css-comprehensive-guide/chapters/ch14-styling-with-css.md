# Chapter 14: Styling with CSS

## Core Idea
CSS visual styling elevates plain document semantics into refined user interfaces through typographic hierarchies (`@font-face`, `line-height`, `letter-spacing`), multi-column text flows, table and list treatments, hardware-accelerated 2D/3D transformations (`transform`), and smooth state transitions (`transition`). 

## Frameworks Introduced
- **Web Font Optimization & Loading Framework (`@font-face` + `font-display: swap`)**:
  - When to use: Embedding custom brand typography across web applications.
  - How: Deliver modern WOFF2 formats first (with WOFF fallback); always declare `font-display: swap` to ensure text renders immediately using a system fallback while the web font downloads, eliminating Flash of Invisible Text (FOIT). Pair with a robust generic fallback stack (`font-family: 'BrandFont', system-ui, -apple-system, sans-serif;`).
- **Hardware-Accelerated Animation & Transition Pipeline**:
  - When to use: Creating hover effects, drawer slides, modal reveals, and button interactions.
  - How: Animate strictly via compositor properties: `transform` (`translate()`, `scale()`, `rotate()`) and `opacity`. Never animate geometry properties (`width`, `height`, `top`, `left`, `margin`, `padding`), which trigger expensive layout recalculations and browser repaints, degrading frame rates below 60fps on mobile devices. Declare transitions using `transition: transform 0.2s cubic-bezier(0.4, 0, 0.2, 1), opacity 0.2s ease`.
- **Accessible Custom Form Control Architecture**:
  - When to use: Restyling native checkboxes, radio buttons, and inputs to match design systems.
  - How: Hide the native `<input>` visually using `opacity: 0` or clipping while keeping it keyboard-focusable; render the custom visual box using an adjacent `<label>` or `::before` pseudo-element styled with `:checked + label::before`. Always preserve distinct visual outlines on `:focus-visible` for keyboard navigation.

## Key Concepts
- **`@font-face`**: CSS at-rule defining custom downloadable typefaces, formats (`woff2`, `woff`), and font weights.
- **`font-display: swap`**: Font loading strategy instructing the browser to render system fallback text immediately until the custom web font loads.
- **`line-height`**: Unitless ratio (e.g., `1.5`) controlling vertical distance between lines of text; essential for reading comfort.
- **`column-count` / `column-gap`**: Multi-column text flow module flowing paragraphs across newspaper-style columns without manual DOM slicing.
- **`border-collapse: collapse`**: Table property merging adjoining cell borders into single shared boundaries.
- **`transform`**: Visual displacement function modifying coordinate space without disturbing neighboring DOM flow (`scale()`, `rotate()`, `translate()`, `skew()`).
- **`transition`**: Property interpolating changes between CSS states over time: `property duration timing-function delay`.
- **`transform-origin`**: Anchor point around which rotations and scale transforms execute (defaults to `50% 50%` center).

## Mental Models
- **Think of Transforms as Moving Shadows or Glass Projections**: When an element scales up (`transform: scale(1.1)`) or slides (`transform: translateY(-5px)`), surrounding layout elements do not move. It is like lifting a glass tile into a projector beam above the table—the footprint underneath stays unchanged, avoiding layout thrashing.
- **Think of `line-height` as Breathing Room**: Text set with `line-height: 1.0` suffocates the reader, causing ascenders and descenders to collide. A unitless ratio of `1.5` to `1.6` provides natural rhythmic cadence matching printed editorial standards.

## Anti-patterns
- **Animating `top`, `left`, `width`, or `height`**: Writing `.drawer { transition: left 0.3s; }`. Forces the browser CPU through full layout recalculations on every single animation frame, causing visible stutter on mobile devices. Use `transform: translateX()` instead.
- **Stripping Focus Outlines (`outline: none`)**: Applying `*:focus { outline: none; }` without providing an accessible alternative. Renders the website completely unusable for keyboard and switch-access users who rely on visible focus rings to navigate.
- **Missing `font-display: swap`**: Relying on default web font loading behavior. If the network hiccups, users stare at blank white screens for up to 3 seconds while text remains invisible.
- **Using Fixed Line Heights with Unit Values**: Setting `line-height: 24px` on parent containers. If a child heading increases `font-size: 32px`, the text lines will overlap and collide into an unreadable mess; use unitless ratios like `line-height: 1.5`.

## Code Examples
```css
/* 1. High-Performance Web Font Declaration */
@font-face {
  font-family: 'OpenSans';
  src: url('../fonts/OpenSans-Regular.woff2') format('woff2'),
       url('../fonts/OpenSans-Regular.woff') format('woff');
  font-weight: 400;
  font-style: normal;
  font-display: swap; /* Prevents invisible text during download */
}

/* 2. Editorial Typography and Multi-Column Layout */
.article-prose {
  font-family: 'OpenSans', system-ui, sans-serif;
  font-size: 1.125rem;
  line-height: 1.7;
  color: #1e293b;
  column-count: 2;
  column-gap: 2.5rem;
  column-rule: 1px solid #e2e8f0;
}

.article-prose h2 {
  column-span: all; /* Heading spans across both columns */
  margin-bottom: 1rem;
}

/* 3. Table Styling: Collapsed borders and readable striping */
.data-table {
  width: 100%;
  border-collapse: collapse; /* Merges double borders */
  margin: 1.5rem 0;
}

.data-table th,
.data-table td {
  padding: 0.75rem 1rem;
  border-bottom: 1px solid #e2e8f0;
  text-align: left;
}

.data-table th {
  background-color: #f8fafc;
  font-weight: 600;
}

/* 4. Hardware-Accelerated Interactive Card with Smooth Transform */
.interactive-card {
  padding: 1.5rem;
  background: #ffffff;
  border-radius: 8px;
  border: 1px solid #cbd5e1;
  /* Animate exclusively composite properties */
  transition: transform 0.25s cubic-bezier(0.2, 0, 0, 1), box-shadow 0.25s ease;
  will-change: transform;
}

.interactive-card:hover {
  transform: translateY(-4px) scale(1.01);
  box-shadow: 0 12px 20px -5px rgba(0, 0, 0, 0.1);
  cursor: pointer;
}

/* 5. Custom Accessible Checkbox Component */
.checkbox-container {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
}

.checkbox-container input[type="checkbox"] {
  appearance: none; /* Strips browser default UI */
  width: 1.25rem;
  height: 1.25rem;
  border: 2px solid #94a3b8;
  border-radius: 4px;
  outline: none;
  transition: background-color 0.15s, border-color 0.15s;
}

.checkbox-container input[type="checkbox"]:checked {
  background-color: #0284c7;
  border-color: #0284c7;
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 16 16' fill='white' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M12.207 4.793a1 1 0 010 1.414l-5 5a1 1 0 01-1.414 0l-2-2a1 1 0 011.414-1.414L6.5 9.086l4.293-4.293a1 1 0 011.414 0z'/%3E%3C/svg%3E");
}

.checkbox-container input[type="checkbox"]:focus-visible {
  box-shadow: 0 0 0 3px rgba(2, 132, 199, 0.35);
}
```
- **What it demonstrates**: WOFF2 web font integration with `font-display: swap`, multi-column newspaper layout, table border collapse, 60fps compositor transitions (`translateY` / `scale`), and accessible custom checkbox restyling.

## Reference Tables

### CSS Transform Functions
| Transform Function | Syntax Example | Operation Performed | Layout Shift Impact |
|---|---|---|---|
| `translate()` | `transform: translate(20px, -10px);` | Moves element along X and Y axes | **Zero** (Compositor only) |
| `scale()` | `transform: scale(1.1);` | Enlarges or shrinks element proportionally | **Zero** (Compositor only) |
| `rotate()` | `transform: rotate(45deg);` | Rotates element around `transform-origin` | **Zero** (Compositor only) |
| `skew()` | `transform: skew(10deg, 5deg);` | Shears/skews element along horizontal/vertical | **Zero** (Compositor only) |

### Transition Timing Functions
| Timing Keyword | Curve Mechanics | Ideal Interaction |
|---|---|---|
| `ease` | Slow start, fast middle, slow finish | General micro-interactions, subtle color fades |
| `linear` | Constant speed throughout | Spinners, continuous progress animations |
| `ease-in` | Slow start, accelerating to exit | Elements exiting the screen off-canvas |
| `ease-out` | Rapid entrance, decelerating to rest | Elements entering the screen / modal reveals |
| `cubic-bezier()` | Custom 4-point Bézier curve | Physics-based spring and bounce effects |

## Worked Example
A shopping cart checkout button feels stiff and sudden when hovered, and its click state lacks visual feedback.
```css
.buy-btn {
  background: #2563eb;
  color: white;
  padding: 10px 20px;
}
.buy-btn:hover {
  background: #1d4ed8;
}
```
**Refactoring to a smooth, physical micro-interaction**:
1. Add smooth transition on background and transform.
2. Add subtle elevation on hover (`translateY(-2px)` with shadow).
3. Add physical compression on active click state (`translateY(0)` with scale contraction).
```css
.buy-btn {
  background: #2563eb;
  color: #ffffff;
  padding: 0.75rem 1.5rem;
  border-radius: 6px;
  border: none;
  font-weight: 600;
  cursor: pointer;
  /* Transition background, transform, and shadow simultaneously */
  transition: 
    background-color 0.15s ease,
    transform 0.15s cubic-bezier(0.2, 0, 0, 1),
    box-shadow 0.15s ease;
  box-shadow: 0 2px 4px rgba(37, 99, 235, 0.2);
}

.buy-btn:hover {
  background-color: #1d4ed8;
  transform: translateY(-2px);
  box-shadow: 0 6px 12px rgba(37, 99, 235, 0.3);
}

.buy-btn:active {
  transform: translateY(0) scale(0.98); /* Physical button press feel */
  box-shadow: 0 1px 2px rgba(37, 99, 235, 0.2);
}

.buy-btn:focus-visible {
  outline: 2px solid #2563eb;
  outline-offset: 2px;
}
```

## Key Takeaways
1. Always use `font-display: swap` in `@font-face` to eliminate invisible text during font loading.
2. Use unitless numbers (e.g., `1.5`) for `line-height` to allow scalable font inheritance.
3. Animate strictly via `transform` and `opacity` to maintain 60fps hardware-accelerated performance.
4. Never disable focus outlines without replacing them with accessible `:focus-visible` styles.
5. Use `border-collapse: collapse` to format clean, readable tables without double borders.
6. Multi-column text layouts (`column-count`) flow text across columns automatically.

## Connects To
- **Ch 05**: Applies table styling properties (`border-collapse`, `border-spacing`).
- **Ch 07**: Powers accessible custom form controls (`checkbox`, `radio`, `select`).
- **Ch 12**: Enhances Flexbox and positioned elements with transforms and transitions.
