# HTML & CSS Decision Cheatsheet

A practitioner's reasoning aid capturing the core technical judgments, trade-offs, and defaults from *HTML and CSS: The Comprehensive Guide* by Jürgen Wolf.

---

## 1. Decision Rules ("When X, Do Y, Because Z")

- **When choosing layout technology**:
  - If aligning items along a single axis (row OR column), **do use Flexbox**, because its content-first sizing handles micro-distribution intuitively.
  - If laying out elements in two dimensions simultaneously (rows AND columns), **do use CSS Grid**, because grid tracks coordinate page scaffolding without nested wrappers.
  - If wrapping editorial body text around a picture, **do use `float`**, because text wrapping is its only valid modern use case.
- **When choosing unit types**:
  - For typography and document spacing, **do use `rem`**, because it scales predictably from the root without compounding multiplicatively like `em`.
  - For media query breakpoints, **do use `em`**, because `em` media queries respect user-configured browser font zoom levels where `px` fails.
  - For fine borders and box shadows, **do use `px`**, because sub-pixel geometric lines must remain sharp regardless of root scale.
- **When choosing image integration**:
  - If serving photos across multiple viewports, **do use `<picture>` with WebP/AVIF and JPEG fallbacks**, because it cuts mobile payload by 40–60% with zero compatibility loss.
  - If rendering logos, UI icons, or line diagrams, **do use SVG**, because vectors maintain infinite sharpness at tiny byte sizes.
- **When adding interactivity**:
  - If expanding/collapsing details, **do use native `<details>` and `<summary>`**, because it provides accessible keyboard toggles with zero JavaScript.
  - If animating UI elements, **do animate strictly `transform` and `opacity`**, because composited properties run on the GPU at 60fps without triggering layout recalculations.
  - If capturing list item clicks, **do use event delegation on the parent container**, because it eliminates hundreds of memory-heavy event closures.

---

## 2. Layout Decision Trees

### Layout Engine Selector
```
Do you need to lay out elements?
├── Wrapping body text around an image? ──────────────> Use float
├── Aligning items in a single row or column?
│   ├── Navigation bar, button bar, form row? ───────> Use Flexbox (`display: flex`)
│   └── Centering an item vertically and horizontally? > Use Flexbox (`justify-content: center; align-items: center`)
└── Coordinating a 2D layout (rows AND columns)?
    ├── Macro page template (header/main/sidebar)? ───> Use CSS Grid (`grid-template-areas`)
    └── Responsive card grid (unknown item count)? ───> Use CSS Grid (`repeat(auto-fit, minmax(280px, 1fr))`)
```

### Positioning Scheme Selector
```
Does the element need custom coordinate placement?
├── Normal document flow (standard stacking)? ────────> `position: static` (Default)
├── Minor nudge without affecting neighbors? ─────────> `position: relative`
├── Anchored inside a parent card/container? ─────────> `position: absolute` (Parent: `position: relative`)
├── Pinned permanently to the screen viewport? ───────> `position: fixed`
└── Scrolls normally, then pins at a top offset? ─────> `position: sticky; top: 0;`
```

---

## 3. Trade-off Matrices

### CSS Integration Comparison
| Approach | Network Caching | Rendering Latency | Maintenance Scope | Recommended Context |
|---|---|---|---|---|
| **External `<link>`** | **High** (cached across site) | Zero after first hit | Single-point global update | Default for all production styles |
| **Embedded `<style>`**| None (re-downloaded) | Fastest first paint | Scoped to single document | Critical above-the-fold CSS |
| **Inline `style="..."`**| None (bloats HTML payload)| Zero | Painful; overrides stylesheets | Dynamic JS coordinates only |

### CSS Baseline Reset Comparison
| Approach | Strips All Styles? | Form Defaults | Development Speed | Maintenance Cost |
|---|---|---|---|---|
| **Classic CSS Reset** | **Yes** (Destructive) | Un-styled; raw inputs | Slow (must rebuild headings/lists)| High |
| **Normalize.css** | **No** (Standardizes bugs) | Preserved & normalized | Fast (works out of the box) | Low |

---

## 4. Thresholds, Defaults & Rules of Thumb

- **Typography Line Height**: Default to unitless `line-height: 1.5` to `1.6` for body copy; use `1.1` to `1.2` for large headings. Never append pixel units (`line-height: 24px`).
- **Optimal Reading Measure**: Constrain text column width between `45` and `75` characters (`max-width: 65ch`) for human reading comfort.
- **Touch Target Sizing**: Minimum clickable/tappable area on mobile controls is `44 × 44px` (or `48 × 48px`).
- **SCSS Nesting Ceiling**: Never nest deeper than **3 levels**. If nesting reaches 4 levels, refactor using flat class selectors or BEM naming.
- **Image `alt` Length**: Keep informational image descriptions between **12 and 16 words** (75–125 characters). For purely decorative images, set `alt=""`.
- **Search Meta Description**: Constrain `<meta name="description">` to **150–160 characters** to avoid truncation in Google search result snippets.
- **Document Title Length**: Keep `<title>` under **60 characters** with primary keywords placed first.

---

## 5. Tells & Smells (Fast Diagnostic Heuristics)

| Symptom / Smell | Probable Root Cause | Immediate Diagnostic Action |
|---|---|---|
| **Horizontal scrollbar on mobile** | Element width + padding exceeds 100% in classic box model | Apply `*, *::before, *::after { box-sizing: border-box; }` |
| **Mobile viewport microscopic / tiny text** | Missing responsive viewport declaration | Add `<meta name="viewport" content="width=device-width, initial-scale=1.0">` to `<head>` |
| **`position: sticky` refuses to stick** | Missing offset threshold or ancestor has `overflow: hidden` | Ensure `top: 0;` is declared and inspect parent nodes for clipping overflows |
| **Image stretches or distorts aspect ratio** | Declared `max-width: 100%` without matching height rule | Add `height: auto;` alongside `max-width: 100%` |
| **`margin-top` has no effect on text** | Element is `display: inline` (e.g., `<a>`, `<span>`) | Switch to `display: inline-block` or `display: block` |
| **Vertical gap between elements smaller than expected** | Normal flow margin collapsing occurred | Expected behavior (margins combine). Add padding, border, or `display: flow-root` to separate |
| **`z-index: 9999` sits underneath lower-indexed element** | Trapped inside a lower parent stacking context | Inspect parent elements; ensure parent `z-index` exceeds the competing container |
| **`::before` pseudo-element invisible** | Missing the mandatory `content` property | Add `content: "";` to the ruleset |
