---
name: math-for-web-design
description: "Knowledge base from "Math for Web Design" by Paul McFedries. Use when applying mathematical models to CSS, JavaScript, Grid, Flexbox, responsive design, and color; studying the book; or referencing its concepts."
---

<!-- argument-hint: [topic, framework name, or chapter number] -->
# Math for Web Design

**Author**: Paul McFedries | **Pages**: ~298 | **Chapters**: 7 | **Generated**: 2026-08-13**

## How to Use This Skill

- **Without arguments:** Start with Core Frameworks; classify the problem as CSS, JavaScript, layout, responsiveness, or color.
- **With a topic:** Route through the Topic Index, then read the linked chapter.
- **With a framework name:** Find it in Core Frameworks and consult its source chapter for constraints and edge cases.
- **With a chapter number:** Open the corresponding Chapter Index entry; connect chapters only where the source supports it.
- **Browse:** Use the Chapter Index for study, Topic Index for routing, and Supporting Files for definitions, patterns, and syntax.

Read the relevant chapter before answering outside **Core Frameworks & Mental Models**. Prefer formulas and browser-resolved relationships over visual guesswork.

## Core Frameworks & Mental Models

### 1. Choose CSS or JavaScript by who owns the input

Model calculations as **Input → Relationship → Output**: contextual or runtime inputs pass through arithmetic, ratios, equations, inequalities, geometry, or trigonometry to produce sizes, positions, angles, progress, or decisions.

Use CSS for rendering-context relationships; prefer `calc()`, `min()`, `max()`, and `clamp()` so browsers reevaluate contextual units. Use JavaScript for events, runtime data, time, loops, conditions, or changing DOM state; custom animation can use `requestAnimationFrame()`. Combine them when CSS owns design and JavaScript owns behavior; do not implement declarative layout procedurally or procedural behavior as CSS math.

Normalized scroll:

`totalHeight = document.body.scrollHeight - window.innerHeight`

`progress = scrollY / totalHeight`

### 2. Use the smallest mathematical model that fits

Use arithmetic for remaining quantities; ratios for scaling, progress, and shares; `y = mx + b` for constant-rate change; inequalities for bounds; powers/roots for nonlinear effects and distance; coordinates/geometry for bounds and paths; trigonometry for circles, waves, and direction.

`position = initial + speed * time`

`distance = Math.sqrt(dx * dx + dy * dy)`

`x = centerX + radius * Math.cos(angle)`

`y = centerY + radius * Math.sin(angle)`

Keep coordinate systems consistent: `clientX`, `clientY`, and `getBoundingClientRect()` are viewport-relative; origin is top-left, x increases rightward, y downward.

### 3. Make JavaScript expressions type-, range-, and precision-safe

**Expression safety:** convert strings with `Number(value)`, unary `+value`, `parseInt(value)`, or `parseFloat(value)`; parenthesize grouping; validate with `Number.isSafeInteger()`, `Number.isNaN()`, or `Number.isFinite()`; choose comparisons and rounding deliberately.

Prefer `===`/`!==`; `"5" == 5` conceals a mismatch. Use `value ?? fallback` when `0`, `false`, and `""` are valid; use `value || fallback` only when all falsy values trigger fallback.

JavaScript `number` is 64-bit IEEE 754. Exact integers span `-(2 ** 53 - 1)` through `2 ** 53 - 1`; `Number.MAX_SAFE_INTEGER` is `9007199254740991`. Use `BigInt` for larger exact integers, but never mix `number` and `bigint` arithmetic.

Approximate decimal equality:

`Math.abs(a - b) < Number.EPSILON`

`Number.EPSILON = 2 ** -52`, approximately `2.220446049250313e-16`.

`%` is remainder, not mathematical modulo. For bidirectional wrapping:

`((dividend % divisor) + divisor) % divisor`

Choose `Math.round()`, `Math.floor()`, `Math.ceil()`, or `Math.trunc()` by intent. `.toFixed(digits)` and `.toPrecision(digits)` return strings. Bankers’ rounding (round half to even) reduces repeated halfway bias.

`Math.random()` returns pseudo-random values in `[0, 1)` and is insecure. Repeatable LCG:

`seed = (seed * 16807) % 2147483647`

`(seed - 1) / 2147483646`

### 4. Resolve CSS references before calculating

Use **Resolve → Calculate → Constrain → Render**: identify each relative reference, evaluate compatible arithmetic, apply bounds, then account for inheritance and the box model.

- `1rem`: root `font-size`; `1em`: current computed `font-size`.
- `1vw = viewport_width / 100`; `1vh = viewport_height / 100`.
- Width, margin, and padding percentages generally reference containing-block width.
- Percentage heights require a defined parent height.
- Percentage `line-height` references the element’s own `font-size`.
- Percentage `border-radius` references element width horizontally and height vertically.

Nested relatives multiply:

`computed_size = base_size × ∏mᵢ`

Use `rem` to avoid compounded typography and unitless `line-height` to preserve descendant proportions.

CSS arithmetic must be inside a math function: `calc(100% - 2rem)`, not `100% - 2rem`; preserve spaces around `+`/`-`. Combine compatible dimensions; multiplication/division requires a scalar operand.

- `min()`: upper limit.
- `max()`: lower limit.
- `clamp(MIN, VAL, MAX)`: both.

`clamp(MIN, VAL, MAX) = max(MIN, min(VAL, MAX))`

Under `content-box`:

`rendered width = width + padding-left + padding-right + border-left-width + border-right-width`

Under `border-box`:

`content width = width - padding-left - padding-right - border-left-width - border-right-width`

Prefer `box-sizing: border-box` when declared dimensions should equal the rendered border box. Margins remain external; adjacent vertical margins may collapse to:

`max(previous margin-bottom, next margin-top)`

### 5. Treat Grid as coordinates plus a space budget

Grid lines are one-based; tracks lie between lines. `grid-column: 3 / 4` selects column three, `2 / span 3` occupies three tracks, and `1 / -1` spans all explicit columns. Negative indexes reference explicit-grid boundaries only.

Track sizing resolves intrinsic sizes and constraints before distributing remainder. Let container `C`, fixed tracks `F`, gaps `G`, relevant borders `B`, padding `P`, and total flex factors `T`:

`R = C - F - G - B - P`

For an `nfr` track:

`W = (n / T) * R`

`fr` shares remainder, not total width. Intrinsic content may impose:

`actual_track_width = max(calculated_flex_value, min_content_width)`

Use `minmax(250px, 1fr)` for a floor plus flexible growth; `fr` is invalid as the minimum. Use `fit-content(limit)` for a grid-defined cap. `auto-fit` collapses empty tracks and redistributes space; `auto-fill` preserves them.

### 6. Diagnose Flexbox from the base size outward

Determine each **flex base size**, then classify the main-axis budget: underflow uses `flex-grow`; overflow uses weighted `flex-shrink`; constraints clamp items and require redistribution. On a horizontal axis, explicit `flex-basis` precedes `width`.

`flex: flex-grow flex-shrink flex-basis;`

Default: `flex: 0 1 auto;`.

Growth:

`available_unused_space = container_width - sum_of_initial_sizes`

`item_unused_space = (item_flex_grow_factor / sum_of_flex_grow_factors) * available_unused_space`

If fractional grow factors total less than `1`:

`item_unused_space = item_flex_grow_factor * available_unused_space`

Shrinkage:

`overflow = sum_of_initial_sizes - container_width`

`item_weighted_shrink_factor = item_width * item_flex_shrink_factor`

`item_overflow_space = (item_weighted_shrink_factor / sum_of_weighted_shrink_factors) * overflow`

Equal shrink factors do not imply equal pixel reductions. Treat `min-width`/`max-width` as hard stops: freeze constrained items, then redistribute the remainder.

### 7. Build responsiveness as continuous relationships first

Use the **Responsive implementation ladder**: Grid or Flexbox → percentages → viewport units → CSS math → media queries → JavaScript.

Use `%` for parent-relative and viewport units for viewport-relative sizing. Use `svh` for a stable mobile-safe minimum, `lvh` for the maximum viewport with browser UI hidden, and `dvh` only when a crucial panel must track the currently visible viewport.

`element percentage = (element fixed width / parent fixed width) × 100`

Use media queries when the rule changes, not merely its value. `min-width: 768px` means `>= 768px`; `max-width: 768px` means `<= 768px`. Closed range:

`@media (600px <= width <= 1024px)`

Runtime weighted allocation must subtract gaps first:

`totalGapWidth = gap × (widgetCount - 1)`

`usableWidth = containerWidth - totalGapWidth`

`widget width = (widget weight / total weight) × usableWidth`

### 8. Choose a color model that matches the operation

Use RGB for channels, pixels, and hex; HSL for hue rotation; LAB/OKLCH for perceptual adjustment. Hue is circular:

`shiftedHue = (hue + shift) mod 360`

Use positive JavaScript modulo for negative shifts.

For contrast, normalize RGB by 255 and gamma-correct each normalized sRGB channel `c`:

- If `c <= 0.04045`: `c / 12.92`.
- Otherwise: `((c + 0.055) / 1.055) ** 2.4`.

Then:

`L = 0.2126Rₗ + 0.7152Gₗ + 0.0722Bₗ`

`CR = (L₁ + 0.05) / (L₂ + 0.05)`

Use lighter luminance as `L₁`. WCAG thresholds: normal text AA `4.5:1`, AAA `7:1`; large text AA `3:1`, AAA `4.5:1`.

Grayscale:

`gray = 0.299R + 0.587G + 0.114B`

For dark mode, invert perceptual lightness and reduce saturation/chroma, not raw RGB. Recalculate contrast after every palette transformation.

## Chapter Index

| # | Title | Key Frameworks |
|---:|---|---|
| 1 | [Web dev math fundamentals](chapters/ch01-web-dev-math-fundamentals.md) | CSS-versus-JavaScript rule; Input → Relationship → Output; linear motion; coordinates; geometry |
| 2 | [Math basics for JavaScript](chapters/ch02-math-basics-for-javascript.md) | Expression safety; numeric-type decisions; true modulo; precision; rounding; randomness |
| 3 | [Math basics for CSS](chapters/ch03-math-basics-for-css.md) | Resolve → Calculate → Constrain → Render; reference values; multiplicative chains; box equations |
| 4 | [CSS Grid math](chapters/ch04-css-grid-math.md) | Grid coordinates; track sizing algorithm; `fr` budget; intrinsic sizing; repetition |
| 5 | [Flexbox math](chapters/ch05-flexbox-math.md) | Flex base size; grow and weighted shrink; fractional growth; constraint redistribution |
| 6 | [The mathematics of responsive design](chapters/ch06-responsive-design-math.md) | Implementation ladder; liquid conversion; bounded fluid sizing; viewport families; runtime allocation |
| 7 | [The mathematics of color](chapters/ch07-color-math.md) | Color models; conversion pipeline; hue harmony; luminance and contrast; compositing |

## Topic Index

- **A:** absolute value—ch01, ch02; alpha compositing—ch07; analogous colors—ch07; aspect ratio—ch01, ch06; `auto-fill`—ch04, ch06; `auto-fit`—ch04, ch06
- **B:** bankers’ rounding—ch02; `BigInt`—ch02; blend modes—ch07; `border-box`—ch03, ch04; bounded fluid sizing—ch03, ch06; box model—ch03
- **C:** `calc()`—ch01, ch03, ch06, ch07; CIELAB—ch07; `clamp()`—ch01, ch03, ch06; color contrast—ch07; color harmony—ch07; comparison expressions—ch01, ch02, ch06; coordinate systems—ch01, ch04; CSS math functions—ch03
- **D:** dark mode—ch07; decimal precision—ch02; distance—ch01; `dvh`—ch03, ch06
- **E:** `em`—ch01, ch03; EPSILON comparison—ch02; explicit Grid tracks—ch04; expressions—ch01, ch02, ch03
- **F:** `fit-content()`—ch04, ch05; flex base size—ch05; `flex-basis`—ch05, ch06; `flex-grow`—ch05; `flex-shrink`—ch05; floating point—ch02; `fr`—ch01, ch04, ch06
- **G:** gamma correction—ch07; gaps—ch04, ch06; geometric progressions—ch03; grayscale—ch07; Grid lines—ch04; grid track sizing algorithm—ch04
- **H:** hex colors—ch07; HSL—ch07; hue modulo—ch02, ch07
- **I:** IEEE 754—ch02; implicit Grid tracks—ch04; inheritance—ch03; intrinsic sizing—ch04, ch05
- **J:** JavaScript `Math` object—ch01, ch02; JavaScript-versus-CSS decision—ch01, ch06
- **L:** LAB—ch07; LCG—ch02; linear equations—ch01, ch06; liquid layouts—ch06; logical viewport units—ch06; luminance—ch07
- **M:** margin collapsing—ch03; media queries—ch06; `min()`—ch01, ch03, ch06; `min-content`—ch04, ch05; `minmax()`—ch04; modulo—ch02, ch03, ch07; multiplicative chains—ch03
- **N:** `NaN`—ch02; negative Grid lines—ch04; nested percentages—ch03, ch06; nullish coalescing—ch02; numeric conversion—ch02
- **O:** OKLCH—ch07; opacity—ch01, ch07; operator precedence—ch02; overflow—ch03, ch05
- **P:** percentages—ch01, ch03, ch06; Pythagorean theorem—ch01; precision—ch02; pseudo-random numbers—ch02
- **R:** ratios—ch01, ch04, ch05, ch06; relative units—ch03, ch06; relative luminance—ch07; remainder—ch02, ch03; `rem` unit—ch03; responsive implementation ladder—ch06; RGB—ch07; rounding—ch02, ch03
- **S:** safe integers—ch02; saturation—ch07; source-over compositing—ch07; `span`—ch04; strict equality—ch02; `svh`—ch06
- **T:** trigonometry—ch01; true modulo—ch02, ch07; truthy and falsy values—ch02
- **U:** underflow—ch05; unit conversion—ch03; unitless `line-height`—ch03
- **V:** viewport coordinates—ch01; viewport units—ch01, ch03, ch06; visual adaptation—ch06
- **W:** WCAG contrast thresholds—ch07; weighted allocation—ch05, ch06; weighted grayscale—ch07; weighted shrink factor—ch05
- **Z:** zero-based Grid assumptions—ch04

## Supporting Files

- [Glossary](glossary.md) — Mathematical, CSS, JavaScript, layout, responsive-design, and color definitions.
- [Patterns](patterns.md) — Reusable decisions and formulas from all seven chapters.
- [Cheatsheet](cheatsheet.md) — Syntax, equations, APIs, units, and lookup tables.

## Scope & Limits

This skill covers only the supplied seven-chapter MEAP source for *Math for Web Design*. It does not replace project design systems, build or testing tools, browser tooling, accessibility audits, or code review.

Use project-specific frameworks and verify evolving browser support, specifications, JavaScript boundaries, color rendering, and accessibility guidance against current platform and standards documentation.
