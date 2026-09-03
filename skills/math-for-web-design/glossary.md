# Glossary

**Alpha compositing and blend modes** — Source-over computes premultiplied output as `Cout = Cₛαₛ + Cᵦαᵦ(1 - αₛ)` and `αout = αₛ + αᵦ(1 - αₛ)` on normalized channels; `multiply`, `screen`, `darken`, `lighten`, `difference`, and `exclusion` combine source and backdrop channels per pixel (Ch 7).
**Aspect ratio and ratio** — Ratios use `a:b`, `a / b`, decimals, or percentages; CSS `aspect-ratio` defines width divided by height, such as `16 / 9` (Ch 1, Ch 4, Ch 5, Ch 6).
**Auto-fill and auto-fit** — `auto-fill` preserves empty Grid tracks, whereas `auto-fit` collapses them and redistributes their space (Ch 4).
**Box-sizing models** — `content-box` places padding and borders outside declared dimensions, whereas `border-box` includes them (Ch 3, Ch 4).
**Color harmony and dark-mode transformation** — Complementary `+180°`, triadic `±120°`, and analogous `±30°` relationships guide palettes; dark mode can invert perceptual lightness, reduce chroma or saturation, shift hue, and recalculate contrast (Ch 7).
**Color models: RGB, HSL, LAB, and OKLCH** — RGB is additive; HSL rotates hue intuitively but lacks perceptual uniformity; LAB models perceptual lightness and opponent axes; OKLCH exposes lightness, chroma, and hue (Ch 7).
**Contrast ratio, relative luminance, and WCAG thresholds** — Gamma-linearized RGB gives `L = 0.2126Rₗ + 0.7152Gₗ + 0.0722Bₗ`, contrast is `(L₁ + 0.05) / (L₂ + 0.05)`, and AA/AAA require `4.5:1`/`7:1` for normal text or `3:1`/`4.5:1` for qualifying large text (Ch 7).
**CSS math functions** — `calc()` performs compatible arithmetic, as in `calc(100% - 2rem)`; `min()` selects the smallest candidate, `max()` the largest, and `clamp(MIN, VAL, MAX)` equals `max(MIN, min(VAL, MAX))` (Ch 1, Ch 3, Ch 6).
**CSS-versus-JavaScript decision rule** — Use CSS for render-time relationships; use JavaScript for interactions, animation state, runtime data, or complex logic (Ch 1, Ch 6).
**Custom properties** — Values inserted with `var()`, including fallbacks such as `var(--heading-size, 2rem)`, can participate in CSS expressions (Ch 3, Ch 7).
**`em`, `rem`, and multiplicative chains** — `em` references current font size and compounds through nesting; `rem` references the root; nested relative values multiply rather than add (Ch 3, Ch 6).
**`fit-content(limit)`** — This bounded intrinsic Grid size equals `max(minimum, min(limit, max-content))` (Ch 4).
**Flex sizing and shorthand** — A flex item starts from non-`auto` `flex-basis`, otherwise explicit or intrinsic size; `flex-grow` distributes underflow, while overflow uses each item’s weighted `base size * flex-shrink`; `flex: grow shrink basis` defaults to `flex: 0 1 auto`. The main axis is horizontal for `row`, vertical for `column` (Ch 5).
**Floating-point approximation, safe integers, and BigInt** — JavaScript IEEE 754 binary64 `number` makes many decimals inexact; compare similarly scaled values with `Math.abs(a - b) < Number.EPSILON`. Exact integers run from `-(2 ** 53 - 1)` through `2 ** 53 - 1`, testable with `Number.isSafeInteger()`; `BigInt` represents larger exact integers (Ch 2).
**Fractional unit** — An `fr` gets a proportional share of Grid space left after fixed tracks, gaps, borders, and padding (Ch 4).
**Grid formatting context** — `display: grid` creates a two-dimensional layout whose container controls child tracks and placement (Ch 4).
**Grid tracks, lines, and sizing** — Templates create explicit tracks; implicit tracks cannot reliably use negative end lines. One-based lines place items, `-1` is the final explicit line, and `span` gives track count. Grid resolves intrinsic growth, then gives remaining space to flexible tracks (Ch 4).
**Intrinsic sizing** — `min-content` is the smallest nonoverflowing size, while `max-content` is the unwrapped content size (Ch 4, Ch 5).
**Liquid layout** — Convert fixed dimensions with `(element width / parent width) * 100` and apply a readable `max-width` (Ch 6).
**Media query** — Media queries apply discrete changes, including `@media (600px <= width <= 1024px)` (Ch 6).
**`minmax()`** — `minmax(min, max)` constrains a Grid track, with `fr` allowed as the maximum but not the minimum (Ch 4).
**Modulo and remainder** — JavaScript `%` follows the dividend’s sign, while cyclic modulo is `((dividend % divisor) + divisor) % divisor` (Ch 2, Ch 3, Ch 7).
**Percentage containing block** — Percentage widths, margins, and padding use containing-block width, whereas percentage heights require a defined parent height (Ch 3, Ch 6).
**Pseudo-random numbers and LCGs** — `Math.random()` returns a nonsecure value in `[0, 1)`, while a reproducible LCG updates `seed = (seed * 16807) % 2147483647` and normalizes with `(seed - 1) / 2147483646` (Ch 2).
**Responsive implementation ladder** — Prefer Grid or Flexbox, percentages, viewport units, CSS math, media queries, then JavaScript as complexity increases (Ch 6).
**Viewport coordinate system and units** — Coordinates start top-left, with positive x rightward and y downward; `vw`, `vh`, `vmin`, `vmax`, `vi`, and `vb` use viewport dimensions, while `sv*`, `lv*`, and `dv*` use small, large, and currently visible mobile viewports (Ch 1, Ch 3, Ch 6).
**Weighted grayscale** — Perceived grayscale uses `gray = 0.299R + 0.587G + 0.114B` rather than averaging RGB channels (Ch 7).
