# Patterns and Techniques

## Choose CSS or JavaScript Math
**When to use**: Use CSS for render-time layout, sizing, spacing, typography, and bounds; use JavaScript for interaction, animation, runtime measurements, loops, or complex conditions (Chs 1, 6).
**How**: 1. Identify inputs. 2. Define the relationship. 3. Produce the output. Prefer `calc()`, `min()`, `max()`, and `clamp()` when browser context supplies the inputs. Use event handlers and `requestAnimationFrame()` when values depend on users or elapsed time.
**Trade-offs**: CSS remains responsive and declarative. JavaScript supports arbitrary logic but adds state, event, and DOM-management costs.

## Resolve CSS Measurements
**When to use**: Debug relative units, inheritance, mixed-unit expressions, or unexpected dimensions (Ch 3).
**How**: 1. Resolve references: `%`, `em`, `rem`, `vw`, or `vh`. 2. Evaluate expressions such as `width: calc(100% - 2rem)`. 3. Apply constraints. 4. Include inheritance and the box model. Nested values multiply: `computed_size = base_size × ∏mᵢ`. Use `var(--gap, 1rem)` when a custom property may be absent.
**Trade-offs**: Relative units preserve relationships but depend on different reference frames. Deeply nested `em` values compound; use `rem` for nesting-independent typography.

## Calculate the Rendered Box
**When to use**: Diagnose overflow or make declared dimensions match rendered dimensions (Ch 3).
**How**: Under `content-box`: `rendered width = width + padding-left + padding-right + border-left-width + border-right-width`. Under `border-box`: `content width = width - padding-left - padding-right - border-left-width - border-right-width`. Prefer `box-sizing: border-box`.
**Trade-offs**: `border-box` simplifies outer sizing. Margins remain external, and adjacent vertical margins collapse to `max(previous margin-bottom, next margin-top)`.

## Build Bounded Fluid Values
**When to use**: Let typography, spacing, or dimensions change continuously without exceeding design limits (Chs 1, 3, 6).
**How**: Model change with `y = mx + b`, where `m = change in property value / change in viewport width`. Apply `property: clamp(minValue, preferredValue, maxValue);`; equivalently, `max(MIN, min(VAL, MAX))`. Use `min()` for an upper limit and `max()` for a lower limit.
**Trade-offs**: Fluid sizing avoids abrupt breakpoint jumps. Bounds must be chosen for readability and usability; an unbounded viewport value can become extreme.

## Convert a Fixed Layout to Liquid
**When to use**: Preserve fixed-layout proportions while allowing the page to shrink (Ch 6).
**How**: 1. Set a readable outer `max-width`. 2. Convert each child with `element percentage = (element fixed width / parent fixed width) × 100`. 3. Convert scalable margins and padding the same way. For media, use `width: 100%; height: auto;`.
**Trade-offs**: Proportions survive resizing, but percentage padding—including top and bottom—uses parent width. Percentage heights require an explicit parent height.

## Select Responsive Thresholds and Viewports
**When to use**: Change layout rules at thresholds or size against mobile browser UI (Ch 6).
**How**: Use `@media (600px <= width <= 1024px)` for a closed interval. Use `svh` for the stable visible minimum, `lvh` for maximum coverage, and `dvh` for the current visible viewport. Prefer Grid, Flexbox, and fluid CSS before breakpoints.
**Trade-offs**: Media queries create discrete changes. `dvh` tracks browser chrome but may cause reflow; `100vh` can overflow the visible mobile viewport.

## Allocate CSS Grid Tracks
**When to use**: Compute fixed, flexible, intrinsic, or responsive two-dimensional tracks (Ch 4).
**How**: Deduct fixed costs first: `R = C - F - G - B - P`. Sum flex factors as `T`; an `nfr` track receives `W = (n / T) * R`. Account for intrinsic protection with `actual_track_width = max(calculated_flex_value, min_content_width)`. For responsive cards use `repeat(auto-fit, minmax(180px, 1fr))`.
**Trade-offs**: `fr` divides remaining space, not total width. `auto-fit` collapses empty tracks; `auto-fill` preserves them. Intrinsic minimums can override the simple split.

## Place Grid Items by Lines
**When to use**: Position or span items reliably in an explicit grid (Ch 4).
**How**: Grid lines are one-based. Use `grid-column: 3 / 4`, `grid-column: 2 / span 3`, or `grid-column: 1 / -1`. For a start line `n` spanning `m` tracks, `end_line = n + m`.
**Trade-offs**: Negative lines adapt to changing explicit track counts but do not target auto-generated implicit tracks. Verify coordinates with the browser Grid overlay.

## Distribute Flexbox Space
**When to use**: Allocate underflow or overflow along one axis (Ch 5).
**How**: 1. Determine the flex base size; a specific `flex-basis` overrides `width`. 2. For underflow: `available_unused_space = container_width - sum_of_initial_sizes`, then allocate by `item_flex_grow_factor / sum_of_flex_grow_factors`. 3. For overflow, weight shrinkage with `item_width * item_flex_shrink_factor`. 4. Clamp to `min-width` or `max-width` and redistribute.
**Trade-offs**: Equal shrink factors do not imply equal pixel reductions. Fractional grow factors totaling less than `1` may leave unused space. Shorthands such as `flex: 1 1 200px` reset all three components.

## Make JavaScript Arithmetic Predictable
**When to use**: Process user input, decimals, large integers, or formatted numeric output (Ch 2).
**How**: Convert with `Number(value)`, compare with `===`, group with parentheses, and validate with `Number.isFinite()` or `Number.isSafeInteger()`. Compare approximations using `Math.abs(a - b) < Number.EPSILON`. Choose `Math.round()`, `Math.floor()`, `Math.ceil()`, or `Math.trunc()` deliberately; `.toFixed()` and `.toPrecision()` return strings.
**Trade-offs**: `number` is approximate IEEE 754 arithmetic. `BigInt` preserves large integers but cannot mix with `number`, `Math` methods, or ordinary rendering APIs.

## Wrap Cyclic Values
**When to use**: Implement carousels, looping frames, palette indexes, or hue rotation (Chs 2, 7).
**How**: Normalize in either direction with `((dividend % divisor) + divisor) % divisor`. For hue, use `shiftedHue = (hue + shift) mod 360`; complementary hue is `C = (H + 180) % 360`. CSS can declare `hsl(calc(var(--base-hue) + 180) 100% 50%)`.
**Trade-offs**: JavaScript `%` alone is signed remainder and can return negative indexes. CSS `mod()` has newer browser requirements.

## Calculate Coordinates, Motion, and Progress
**When to use**: Measure drags, animate values, or arrange radial controls (Ch 1).
**How**: Scroll progress: `progress = scrollY / totalHeight`, where `totalHeight = document.body.scrollHeight - window.innerHeight`. Distance: `Math.sqrt(dx * dx + dy * dy)`. Constant motion: `position = initial + speed * time`. Circular placement: `x = centerX + radius * Math.cos(angle)` and `y = centerY + radius * Math.sin(angle)`.
**Trade-offs**: Keep `clientX`, `clientY`, and `getBoundingClientRect()` in the same viewport-relative coordinate system. Subtract half an item’s dimensions to center it on a radial point.

## Validate Color Contrast
**When to use**: Check text and UI colors against WCAG thresholds (Ch 7).
**How**: 1. Normalize each RGB channel with `c = channel / 255`. 2. Linearize: if `c <= 0.04045`, use `c / 12.92`; otherwise use `((c + 0.055) / 1.055) ** 2.4`. 3. Calculate `L = 0.2126Rₗ + 0.7152Gₗ + 0.0722Bₗ`. 4. Compute `CR = (L₁ + 0.05) / (L₂ + 0.05)`, with the lighter value first.
**Trade-offs**: Visual judgment and hue difference are unreliable. Normal text requires `4.5:1` for AA and `7:1` for AAA; large text requires `3:1` and `4.5:1`.

## Transform and Composite Colors
**When to use**: Generate grayscale, dark themes, opacity, or blend effects (Ch 7).
**How**: Perceived grayscale: `gray = 0.299R + 0.587G + 0.114B`. For dark mode use `Ldark = 100 - Llight` in HSL or `Ldark = 1 - Llight` in OKLCH, then reduce saturation or chroma and recheck contrast. Composite with `Cout = Cₛαₛ + Cᵦαᵦ(1 - αₛ)` and `αout = αₛ + αᵦ(1 - αₛ)`.
**Trade-offs**: Raw RGB inversion distorts hierarchy. Blend results depend on the backdrop; unchecked OKLCH values may exceed ordinary display gamuts.
