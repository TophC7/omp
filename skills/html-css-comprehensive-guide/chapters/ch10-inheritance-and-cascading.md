# Chapter 10: Inheritance and Cascading

## Core Idea
Cascading and inheritance govern how styles propagate through the DOM tree and how conflicting declarations resolve. Typography and text properties inherit down the tree by default, while box-model geometry does not. When multiple rules target the same element, the cascade resolves collisions strictly through a deterministic hierarchy: stylesheet origin, importance (`!important`), selector specificity `(A, B, C, D)`, and source order.

## Frameworks Introduced
- **The Cascade Resolution Algorithm**:
  - When to use: Diagnosing why a style rule fails to apply or resolving styling conflicts across multiple stylesheets.
  - How: The browser evaluates conflicting declarations through a 4-step sorting pipeline:
    1. **Origin and Importance**: User Agent default < User normal < Author normal < Author `!important` < User `!important`.
    2. **Specificity**: Higher `(A, B, C, D)` tuple wins.
    3. **Scope / Proximity**: More proximate shadow DOM or scoped rule wins.
    4. **Source Order**: If origin, importance, and specificity are identical, the rule declared latest in the stylesheet wins.
- **The 4-Column Specificity Calculation Framework `(A, B, C, D)`**:
  - When to use: Scoring selector weight to prevent specificity escalation wars.
  - How:
    - **A (Inline)**: 1 if declared in `style="..."`, else 0.
    - **B (IDs)**: Count of `#id` selectors.
    - **C (Classes / Attributes / Pseudo-classes)**: Count of `.class`, `[attr]`, and `:pseudo-class`.
    - **D (Elements / Pseudo-elements)**: Count of `tag` and `::pseudo-element`.
    - *Comparison Rule*: Compare left to right. Column A beats any value in B; Column B beats any value in C. Ten classes never equal one ID.
- **Inheritance Management Protocol (`inherit`, `initial`, `unset`)**:
  - When to use: Resetting styles, enforcing parent values on non-inherited properties, or establishing theme cascades.
  - How:
    - `inherit`: Forces the property to take the computed value of its immediate parent (useful for making `<a>` inherit `color`).
    - `initial`: Resets the property to its official CSS specification default value (e.g., `color: canvastext`, `display: inline`).
    - `unset`: Acts as `inherit` for naturally inherited properties; acts as `initial` for non-inherited properties.
    - `all: unset`: Wipes all declared properties on an element back to browser baseline.

## Key Concepts
- **Inheritance**: The mechanism by which certain CSS properties applied to an ancestor element automatically pass down to all descendant elements (e.g., `color`, `font-family`, `font-size`, `line-height`, `text-align`).
- **Non-Inherited Properties**: Box-model, layout, and visual framing properties that stop at the target element and do not pass down to children (e.g., `margin`, `padding`, `border`, `background`, `width`, `height`, `position`).
- **Cascade**: The deterministic algorithm resolving multiple competing declarations for a single DOM node.
- **User Stylesheet**: Client-side CSS applied by end users (often through browser extensions for high-contrast accessibility).
- **`!important`**: Modifier elevating a declaration above normal author rules; inverts cascade order so User `!important` overrides Author `!important` to guarantee accessibility accommodations.
- **Relative Units (`em` vs. `rem`)**:
  - `em`: Relative to the `font-size` of the immediate parent element (or the element's own `font-size` when used for padding/margins); compounds multiplicatively when nested.
  - `rem` (Root EM): Relative exclusively to the `font-size` of the root `<html>` element (default 16px); non-compounding and predictable for typography and spacing grids.
- **Viewport Units (`vw`, `vh`, `vmin`, `vmax`)**: Percentages relative to the viewport's width and height (`1vw = 1%` of viewport width).

## Mental Models
- **Think of Specificity as Coin Currency (Gold, Silver, Copper, Iron)**:
  - Inline style = Gold Bar (1,0,0,0)
  - ID selector = Silver Dollar (0,1,0,0)
  - Class / Attribute / Pseudo-class = Copper Dime (0,0,1,0)
  - Element tag = Iron Penny (0,0,0,1)
  - One thousand copper dimes cannot purchase an item priced at one silver dollar.
- **Think of Inheritance as Genetic Traits vs. Owned Property**: Eye color and blood type (`font-family`, `color`) are passed down biologically to children automatically. Houses and cars (`border`, `background`, `margin`) are owned by the parent; children do not automatically wear their parents' shoes.

## Anti-patterns
- **Using `!important` to Fix Specificity Bugs**: Slapping `!important` onto a rule because a class won't apply. Creates an arms race where future overrides require more `!important` declarations, eventually locking down the codebase. Fix the selector specificity instead.
- **Nesting `em` Font Sizes Deeply**: Defining `font-size: 1.2em` on lists. In a 3-level nested list, the text compounds: `1.2 × 1.2 × 1.2 = 1.728x` the intended size. Use `rem` for typography to avoid compounding.
- **Assuming `background` is Inherited**: Seeing an `<h1>` display against a gray body and assuming it inherited the background. In reality, `background-color` defaults to `transparent`; the gray body simply shows through.
- **Writing Redundant CSS for Inherited Properties**: Explicitly declaring `font-family` on every `p`, `h1`, `h2`, `span`, and `li`. Declare `font-family` once on `body` and let inheritance do the work.

## Code Examples
```css
/* 1. Global typography and root variables */
:root {
  font-size: 16px; /* Base 1rem = 16px */
}

body {
  margin: 0;
  font-family: system-ui, -apple-system, sans-serif;
  color: #1e293b; /* Inherited by all text descendants */
  line-height: 1.5; /* Inherited proportionally */
}

/* 2. Forcing inheritance on anchor tags */
/* Anchor tags do not inherit color by default in most user-agent stylesheets */
a.nav-link {
  color: inherit; /* Adopts the color of its parent container */
  text-decoration: none;
}

/* 3. Non-compounding typography using rem */
h1 { font-size: 2.25rem; } /* 36px */
h2 { font-size: 1.5rem; }  /* 24px */
p  { font-size: 1rem; }    /* 16px */

/* 4. Specificity Showcase: Which rule wins? */
/* Specificity: (0, 0, 0, 1) - Element */
p {
  color: #64748b;
}

/* Specificity: (0, 0, 1, 0) - Class (Wins over element) */
.alert-text {
  color: #d97706;
}

/* Specificity: (0, 0, 2, 0) - Two Classes */
.card .alert-text {
  color: #ea580c;
}

/* Specificity: (0, 1, 0, 0) - Single ID (Wins over any number of classes) */
#special-notice {
  color: #b91c1c;
}

/* 5. Modern color models with alpha transparency */
.banner {
  background-color: rgba(14, 165, 233, 0.15); /* RGBA with 15% opacity */
  border-left: 4px solid hsl(199, 89%, 48%);     /* HSL color representation */
}
```
- **What it demonstrates**: Inheritance delegation on `body`, `inherit` keyword on anchors, predictable `rem` typography, specificity scoring collisions, and color model representations.

## Reference Tables

### Inherited vs. Non-Inherited Properties
| Property Category | Inherited Automatically? | Common Properties |
|---|---|---|
| **Typography & Fonts** | **Yes** | `font-family`, `font-size`, `font-weight`, `font-style`, `line-height` |
| **Text Formatting** | **Yes** | `color`, `text-align`, `text-indent`, `letter-spacing`, `word-spacing` |
| **List Styling** | **Yes** | `list-style`, `list-style-type`, `list-style-position` |
| **Box Model & Spacing** | **No** (defaults to initial/zero) | `margin`, `padding`, `border`, `width`, `height`, `max-width` |
| **Backgrounds** | **No** (defaults to `transparent`) | `background-color`, `background-image`, `background-repeat` |
| **Layout & Positioning** | **No** | `display`, `position`, `top`, `left`, `float`, `z-index`, `overflow` |

### The Cascade Origin & Importance Sorting Ladder
| Priority Rank | Origin | Importance Modifier | Typical Authority |
|---|---|---|---|
| **1 (Highest)** | User Stylesheet | `!important` | End-user accessibility overrides (high contrast, zoom) |
| **2** | Author Stylesheet | `!important` | Developer imperative overrides |
| **3** | Author Stylesheet | Normal | Web project production stylesheets |
| **4** | User Stylesheet | Normal | User custom browser defaults |
| **5 (Lowest)** | User-Agent | Normal | Default browser rendering stylesheet |

### CSS Unit Reference
| Unit Type | Unit | Reference Base | Ideal Usage |
|---|---|---|---|
| **Absolute** | `px` | Hardware-independent reference pixel | Borders, precise box shadows |
| **Relative (Root)** | `rem` | Font-size of `<html>` (typically 16px) | Font sizes, layout margins, padding grids |
| **Relative (Local)** | `em` | Font-size of immediate parent / element | Component-relative padding, iconography sizing |
| **Percentage** | `%` | Dimension of containing parent block | Responsive widths, image containers |
| **Viewport Width** | `vw` | 1% of browser viewport width | Fluid responsive typography, full-bleed sections |
| **Viewport Height** | `vh` | 1% of browser viewport height | Hero sections (`height: 100vh`), modal dialogs |

## Worked Example
A junior developer cannot figure out why a critical alert remains blue instead of red:
```html
<div id="sidebar">
  <p class="alert-box">Database connection failed.</p>
</div>
```
```css
#sidebar p {
  color: blue;
}

.alert-box {
  color: red;
}
```
**Diagnosis & Resolution**:
1. Calculate specificity for Rule 1: `#sidebar p` has 1 ID and 1 Element = `(0, 1, 0, 1)`.
2. Calculate specificity for Rule 2: `.alert-box` has 1 Class = `(0, 0, 1, 0)`.
3. Column B (1) beats Column B (0). The ID selector dominates regardless of stylesheet order.
4. **Resolution without `!important`**: Match or exceed specificity using class-based scoping:
```css
#sidebar .alert-box {
  color: red; /* Specificity (0, 1, 1, 0) wins cleanly over (0, 1, 0, 1) */
}
```

## Key Takeaways
1. Typography and text colors inherit down the DOM tree; box dimensions, padding, margins, and borders do not.
2. Specificity is calculated as a 4-part tuple `(A, B, C, D)`; classes never override IDs regardless of quantity.
3. When specificity and importance are equal, the rule written lowest (latest) in source order wins.
4. Use `rem` for typography and spacing to avoid the multiplicative compounding problems of `em`.
5. Never use `!important` as a band-aid for selector specificity issues.
6. User `!important` styles override author styles by design to protect accessibility accommodations.

## Connects To
- **Ch 09**: Supplies the selectors scored inside this chapter's specificity matrix.
- **Ch 11**: Explores the non-inherited box model properties (`margin`, `padding`, `border`).
- **Ch 15**: Demonstrates browser DevTools techniques for inspecting the computed cascade.
