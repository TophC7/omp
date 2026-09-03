# Math for Web Design Cheatsheet

## Fast decision tree

1. **Does the value depend on events, time, live measurements, API data, loops, or complex conditions?**
   - Yes → JavaScript.
   - No → CSS.
2. **Is layout one-dimensional or two-dimensional?**
   - One main axis → Flexbox.
   - Rows **and** columns / line placement → Grid.
3. **What is the reference frame?**
   - Parent → `%`
   - Root font → `rem`
   - Current font → `em`
   - Viewport → `vw`, `vh`, `vmin`, `vmax`; mobile → `sv*`, `lv*`, `dv*`
4. **Continuous change or rule switch?**
   - Continuous → `calc()`, `min()`, `max()`, `clamp()`
   - Threshold/layout change → media query
5. **Color task?**
   - Channels/hex → RGB
   - Hue harmony → HSL
   - Perceptual scale/theme → OKLCH
   - Accessibility → relative luminance + contrast ratio

## CSS vs JavaScript math (Ch 1–3, 6)

| If you need… | Choose | Exact pattern |
|---|---|---|
| Mixed compatible units | CSS | `calc(100% - 2rem)` |
| Upper / lower / both bounds | CSS | `min()` / `max()` / `clamp(MIN, VAL, MAX)` |
| Render-time layout/type | CSS | Declarative browser resolution |
| Interaction/animation/runtime data | JS | events, `requestAnimationFrame()` |
| Cyclic index with negatives | JS | `((a % b) + b) % b` |
| Decimal comparison | JS | `Math.abs(a - b) < Number.EPSILON` |

JS safety: convert with `Number(value)`; prefer `===`; reject with `Number.isNaN()` / `Number.isFinite()`. Safe integers: `±9007199254740991`; use `BigInt` only for exact larger integers—never mix `number` and `bigint`. Default flex state: `flex: 0 1 auto;`.

## Units, functions, and box math (Ch 3)

| Tell | Calculation / choice |
|---|---|
| `rem` | root `font-size`; avoids nested compounding |
| `em` | current computed `font-size`; nested size = `base_size × ∏mᵢ` |
| `1vw`, `1vh` | `viewport_width / 100`, `viewport_height / 100` |
| `%` width/margin/padding | containing-block width—even top/bottom spacing |
| `%` height | requires explicit parent height |
| Fluid but bounded | `clamp(MIN, VAL, MAX)` = `max(MIN, min(VAL, MAX))` |
| `content-box` | rendered width = width + horizontal padding + borders |
| `border-box` | content width = width − horizontal padding − borders |

CSS smells: arithmetic outside `calc()`; missing spaces in `calc(100vh - 3rem)`; incompatible units; deep `em` chains; unbounded `vw`; assuming vertical percentage spacing uses height.

## Grid vs Flexbox (Ch 4–5)

| Need/state | Grid | Flexbox |
|---|---|---|
| Geometry | 2D numbered lines, starting at `1` | 1D main-axis budget |
| Dynamic full span | `grid-column: 1 / -1` | N/A |
| Responsive cards | `repeat(auto-fit, minmax(180px, 1fr))` | wrapping items |
| Preserve empty tracks | `auto-fill` | N/A |
| Base size | track definition | non-`auto` `flex-basis`; else width/content |
| Free space | `fr` after fixed costs | `flex-grow` |
| Overflow | intrinsic/min constraints | weighted `flex-shrink` |

Grid budget:

`R = C - F - G - B - P`

`W = (n / T) * R`

Remember: `fr` divides **remaining**, not total, space; `minmax()` cannot use `fr` as its minimum.

Flex grow:

`unused = container_width - sum_of_initial_sizes`

`final = initial + (grow / sum_grow) * unused`

Flex shrink:

`overflow = sum_of_initial_sizes - container_width`

`weight = item_width * flex_shrink`

`final = initial - (weight / sum_weights) * overflow`

Clamp at `min-width`/`max-width`, then redistribute.

## Responsive rules (Ch 6)

- Fixed → liquid: `element percentage = (element fixed width / parent fixed width) × 100`.
- Images: `.hero img { display: block; width: 100%; height: auto; }`
- Prefer Grid/Flex → `%`/viewport units → CSS math → media queries → JS.
- `min-width: 768px` means `>=`; `max-width: 768px` means `<=`.
- Closed range: `@media (600px <= width <= 1024px)`.
- Mobile height: `svh` = safe minimum; `lvh` = maximum; `dvh` = current, but may reflow.
- Smells: fixed primary widths, overlapping breakpoints, blind `100vh`, dividing weighted items before subtracting gaps.

## Color calculations (Ch 7)

| Decision | Rule |
|---|---|
| Harmony | hue wraps modulo `360`; complement: `C = (H + 180) % 360` |
| Grayscale | `gray = 0.299R + 0.587G + 0.114B` |
| Linearize normalized `c` | `c / 12.92` if `c <= 0.04045`; else `((c + 0.055) / 1.055) ** 2.4` |
| Luminance | `L = 0.2126Rₗ + 0.7152Gₗ + 0.0722Bₗ` |
| Contrast | `CR = (L₁ + 0.05) / (L₂ + 0.05)`, lighter first |
| WCAG | normal: AA `4.5:1`, AAA `7:1`; large: `3:1`, `4.5:1` |

Dark-mode smell: raw RGB inversion. Instead invert perceptual lightness, reduce saturation/chroma, optionally shift hue, then recalculate contrast.
