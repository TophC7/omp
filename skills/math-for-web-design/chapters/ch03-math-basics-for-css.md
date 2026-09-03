# Chapter 3: Math basics for CSS

## Core Idea

CSS layout is a runtime mathematical system. Before rendering, the browser resolves relative measurements against their reference values, converts compatible units as needed, evaluates expressions, applies inheritance, and computes each element’s box dimensions.

Use relative units to express relationships, `calc()` to make mixed-unit arithmetic explicit, and `min()`, `max()`, or `clamp()` to constrain responsive values. Prefer `box-sizing: border-box` when the declared dimensions should equal the element’s rendered border box. When debugging, identify the reference value first: percentages, `em`, `rem`, and viewport units do not share the same coordinate system.

## Frameworks Introduced

### 1. Resolve → Calculate → Constrain → Render

Analyze a CSS value in four stages:

1. **Resolve references:** Determine what each relative value uses as its base.
2. **Calculate:** Convert compatible measurements and evaluate arithmetic.
3. **Constrain:** Apply `min()`, `max()`, or `clamp()` bounds.
4. **Render:** Incorporate inheritance and box-model additions or subtractions.

For example, with `width: calc(100% - 2rem)`, a 600px parent, and a 16px root font size:

- `100% = 600px`
- `2rem = 2 × 16px = 32px`
- Final width: `600px - 32px = 568px`

The general formula is:

`final_value = (parent_width × percentage / 100) - (root_font_size × rem_value)`

### 2. Reference-Value Framework

Before calculating a percentage, ask: **percentage of what?**

- Width-like dimensions generally reference a parent or containing block’s width.
- Height-like dimensions generally reference a defined parent or containing block’s height.
- Percentage `line-height` references the element’s own `font-size`.
- Percentage `border-radius` uses the element’s width horizontally and height vertically.
- Percentage padding and margins—including top and bottom—use the containing block’s width.

### 3. Multiplicative-Chain Framework

Nested `em` and percentage values form multiplicative progressions rather than additive ones.

For nested `em` font sizes:

`computed_size = base_size × ∏mᵢ`

where `∏mᵢ` is the product of all ancestor multipliers.

For nested percentage widths:

`child_width = root_width × ∏pᵢ`

where each `pᵢ` is the percentage expressed as a decimal fraction.

Use this model whenever several generations of descendants apply relative sizing.

### 4. Box Equation Framework

Treat every element as an equation, not merely a visual rectangle.

Under `content-box`:

`rendered width = width + padding-left + padding-right + border-left-width + border-right-width`

Under `border-box`:

`content width = width - padding-left - padding-right - border-left-width - border-right-width`

Margins affect spacing around the box, not the element’s own dimensions.

## Key Concepts

1. **CSS unit conversion:** CSS defines `1in = 96px`, regardless of physical screen DPI. Therefore, `1pt = 96px / 72 = 1.333px`, and `1pc = 12pt = 16px`.

2. **`rem` versus `em`:** `1rem` equals the root element’s font size in pixels. `1em` equals the current element’s computed font size. Prefer `rem` for typography that should not compound through nested elements.

3. **Compounding `em` values:** If a 16px base contains `font-size: 1.5em`, followed by a descendant using `1.2em`, the descendant computes to `16px × 1.5 × 1.2 = 28.8px`.

4. **Viewport units:** `1vw = viewport_width / 100`, `1vh = viewport_height / 100`, `1vmin = min(viewport_width, viewport_height) / 100`, and `1vmax = max(viewport_width, viewport_height) / 100`. Dynamic viewport units such as `dvh` adjust to the visible viewport area as mobile UI changes.

5. **CSS arithmetic:** Arithmetic expressions must appear inside a CSS math function such as `calc()`. The syntax `width: 100% - 2rem` is invalid; use `width: calc(100% - 2rem)`.

6. **Compatible types:** CSS can combine compatible types such as `px` and `rem`, or `deg` and `rad`, but not incompatible types such as lengths and angles. For multiplication or division, one operand must be scalar; for division, the scalar must be on the right.

7. **Constraint functions:** `min()` supplies an upper limit by selecting the smallest candidate. `max()` supplies a lower limit by selecting the largest. `clamp(MIN, VAL, MAX)` applies both bounds and is equivalent to `max(MIN, min(VAL, MAX))`.

8. **CSS variables in expressions:** Insert custom properties with `var()`, as in `calc(var(--gap) * 2)`. A fallback such as `var(--heading-size, 2rem)` prevents a missing variable from invalidating the declaration.

9. **Computed-value inheritance:** Descendants generally inherit a parent’s computed value, not its original specified expression. A percentage `line-height` becomes a computed length before inheritance, while a unitless `line-height` remains a multiplier.

10. **Margin collapsing:** Adjacent vertical margins do not necessarily add. The collapse rule is `max(previous margin-bottom, next margin-top)`.

## Mental Models

### CSS as a Dependency Graph

A declaration may depend on the root font size, viewport dimensions, containing-block dimensions, inherited values, and custom properties. When one dependency changes, the browser reevaluates the affected value. Use this model for responsive calculations rather than imagining relative units as fixed measurements.

### Relative Units as Coordinate Systems

`rem`, `em`, `%`, `vw`, and `vh` describe values in different coordinate systems. Mixing them is safe only after identifying each reference. Resolve them mentally to pixels when debugging, while leaving the relationship explicit in CSS with `calc()`.

### Inheritance as Value Transmission

Inheritance does not simply copy source text. The browser usually computes the parent’s value first and transmits that result. The important exception is percentage-based properties whose final values depend on layout, including `margin`, `padding`, `text-indent`, `height`, and `top`.

### The Declared Box Is Not Always the Rendered Box

With `content-box`, declared `width` describes only the content area. With `border-box`, declared `width` describes the content, padding, and border together. Always establish which equation applies before diagnosing overflow.

## Anti-patterns

- **Writing arithmetic outside a math function:** `width: 100% - 2rem` is invalid. Wrap the expression in `calc()`.
- **Omitting spaces around `+` or `-`:** `calc(100vh-3rem)` is invalid; use `calc(100vh - 3rem)`.
- **Combining incompatible dimensions:** Do not add a length to an angle, as in `calc(10px + 45deg)`.
- **Multiplying two unit-bearing values:** `calc(1rem * 2rem)` is invalid. Prefer a unitless scale such as `calc(1.5 * 1rem)`.
- **Assuming nested relative values add:** Two nested `50%` widths produce `25%` of the root width, not `100%`.
- **Using deeply nested `em` font sizes without calculating the chain:** The multipliers compound and can produce unexpectedly large text.
- **Assuming vertical percentage margins or padding use height:** They are calculated from the containing block’s width.
- **Using percentage `line-height` when descendants change font size:** Descendants inherit the parent’s computed line height. Prefer a unitless value when the proportional relationship should survive inheritance.
- **Expecting `content-box` width to include padding and borders:** Add those components to obtain the rendered width, or switch to `border-box`.
- **Expecting adjacent vertical margins to add:** Margin collapsing selects the larger margin.
- **Using a custom property without a fallback when it may be absent:** A missing variable can invalidate the entire property.
- **Ignoring a failed expression:** A browser typically ignores the invalid declaration and uses the property’s default or another applicable cascade value. Inspect computed styles in devtools.

## Code Examples

Use `calc()` to divide a fixed-width container into equal columns after reserving space for its gutters:

```css
.container {
  width: 800px;
}
.column {
  width: calc((100% - 40px) / 3);
  margin-right: 20px;
}
.column:last-child {
  margin-right: 0;
}
```

The two 20px gutters consume 40px; the remaining width is divided equally among three columns.

## Reference Tables

### Units and Reference Values

| Unit or property | Mathematical rule or reference |
|---|---|
| `in` | `1in = 96px` |
| `pt` | `1pt = 96px / 72 = 1.333px` |
| `pc` | `1pc = 12pt = 16px` |
| `rem` | Root element’s `font-size` |
| `em` | Current element’s computed `font-size` |
| `vw` | `viewport_width / 100` |
| `vh` | `viewport_height / 100` |
| `%` for `width`, `margin`, `padding` | Containing block’s width |
| `%` for `height` | Parent height, if defined |
| `%` for `line-height` | Element’s own `font-size` |
| `%` for `border-radius` | Element width horizontally; element height vertically |

### CSS Math Decision Rules

| Need | Prefer | Rule |
|---|---|---|
| Mixed-unit arithmetic | `calc()` | Supports compatible data types at runtime |
| Maximum allowed value | `min()` | Returns the smallest candidate |
| Minimum allowed value | `max()` | Returns the largest candidate |
| Minimum and maximum bounds | `clamp()` | `clamp(MIN, VAL, MAX)` |
| Cyclic wrapping | `mod()` | Result takes the divisor’s sign |
| Signed remainder | `rem()` | Result takes the dividend’s sign |
| Exponential scale | `pow(base, exponent)` | Higher positive exponents increase scale |
| Growth that levels off | `log(x, base)` | Base is optional; omitted base is `e` |
| Root-based scaling | `sqrt(x)` | Useful for less aggressive scaling |
| Rounding to an interval | `round(strategy, number, interval)` | Strategies: `down`, `nearest`, `to-zero`, `up` |

### Additional Math Functions

| Function | Result | JavaScript equivalent | Browser floors stated in the chapter |
|---|---|---|---|
| `exp(x)` | `e` raised to `x` | `Math.exp()` | Chrome 120+, Firefox 118+, Safari 15.4+ |
| `hypot(x, y, ...)` | Square root of the sum of squared arguments | `Math.hypot()` | Chrome 120+, Firefox 118+, Safari 15.4+ |
| `log(x, base)` | Logarithm of `x` | `Math.log()` | Chrome 120+, Firefox 118+, Safari 15.4+ |
| `mod(dividend, divisor)` | Modulus; sign follows divisor | `((a % b) + b) % b` | Chrome 125+, Firefox 118+, Safari 15.4+ |
| `pow(base, exponent)` | Exponentiation | `Math.pow()` | Chrome 120+, Firefox 118+, Safari 15.4+ |
| `rem(dividend, divisor)` | Remainder; sign follows dividend | `x % y` | Chrome 125+, Firefox 118+, Safari 15.4+ |
| `round(...)` | Rounded value, optionally to an interval | `Math.floor()`, `Math.round()`, `Math.trunc()`, `Math.ceil()` | Chrome 125+, Firefox 118+, Safari 15.4+ |
| `sqrt(x)` | Square root | `Math.sqrt()` | Chrome 120+, Firefox 118+, Safari 15.4+ |

### Box-Sizing Equations

| Model | Declared `width` represents | Rendered width |
|---|---|---|
| `content-box` | Content only | Content + horizontal padding + horizontal borders |
| `border-box` | Content + padding + borders | Declared `width` |
| Either model | Margins | External spacing; not part of the element’s own width |

## Worked Example

Consider two `h2` elements at different nesting depths. The root font size is 16px. A `main` uses `font-size: 1.25em`; an `article` inside it uses `font-size: 1.75em`; and every `h2` uses `font-size: 2em`.

### First heading: directly inside `main`

1. Compute `main`:

   `16px × 1.25 = 20px`

2. Compute its `h2`:

   `20px × 2 = 40px`

The first heading renders at **40px**.

### Second heading: inside `article`

1. Start with the computed `main` size:

   `20px`

2. Compute `article`:

   `20px × 1.75 = 35px`

3. Compute the nested `h2`:

   `35px × 2 = 70px`

The second heading renders at **70px**.

Although both headings specify `2em`, they use different inherited reference sizes. The multiplicative chain—not the local declaration alone—determines the outcome.

Use `font-size: 2rem` when every `h2` should have the same root-relative size. With a 16px root:

`2rem = 2 × 16px = 32px`

Both headings then render at **32px**, independent of nesting depth.

## Key Takeaways

- Identify every relative value’s reference before doing CSS math.
- Use `calc()` for explicit mixed-unit arithmetic, and obey compatibility, scalar, whitespace, and precedence rules.
- Use `min()` for an upper bound, `max()` for a lower bound, and `clamp()` when both limits matter.
- Prefer `rem` over nested `em` values when typography should not compound.
- Prefer unitless `line-height` because descendants inherit the multiplier and apply it to their own font sizes.
- Prefer `border-box` when declared dimensions should match rendered outer dimensions.
- Debug layout by inspecting computed values, then apply the correct inheritance and box-model equations.

## Connects To

- **Ch 1 — Web dev math fundamentals:** Applies products, percentages, order of operations, bounds, and geometric progressions to CSS rendering.
- **Ch 2 — Math basics for JavaScript:** Connects CSS functions to `Math.exp()`, `Math.hypot()`, `Math.log()`, `Math.pow()`, `Math.sqrt()`, rounding methods, and JavaScript’s `%` operator.
- **Ch 4 — CSS Grid math:** Extends gutter subtraction and equal-column formulas into grid track sizing.
- **Ch 5 — Flexbox math:** Builds on container dimensions, available space, and computed box sizes.
- **Ch 6 — The mathematics of responsive design:** Expands viewport units, percentages, dynamic viewport units, and constrained fluid values.
- **Ch 7 — The mathematics of color:** Uses angle arithmetic, `hsl()`, and `mod()` for cyclic hue calculations such as complementary colors.
