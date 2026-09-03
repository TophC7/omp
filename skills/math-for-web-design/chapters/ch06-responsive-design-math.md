# Chapter 6: The mathematics of responsive design

## Core Idea

Responsive design is **adaptation expressed mathematically**. A layout should preserve three outcomes across screen sizes and device capabilities:

1. Text remains legible.
2. Images scale without distortion.
3. Page components reorganize to remain usable.

Build this behavior by defining relationships rather than isolated dimensions:

- Use percentages when an element should scale with its parent.
- Use viewport units when it should scale with the browser viewport.
- Use CSS Grid or Flexbox when tracks or items can adapt automatically.
- Use media queries when layout rules must change at a threshold.
- Use `calc()`, `min()`, `max()`, and `clamp()` when values should vary fluidly or remain bounded.
- Use JavaScript only when the calculation depends on runtime data, interactions, content changes, or complex conditional logic.

Prefer fluid relationships over fixed dimensions because fixed-width layouts become brittle as soon as the available width is smaller than the declared width.

## Frameworks Introduced

### Responsive implementation ladder

Use the least complex mechanism capable of expressing the required behavior:

1. **Grid or Flexbox:** Let tracks grow, shrink, wrap, use `fr`, or apply `auto-fit` and `auto-fill`.
2. **Proportional layout:** Relate dimensions and spacing to a parent with `%`.
3. **Viewport-relative layout:** Relate dimensions to the initial containing block with `vw`, `vh`, `vmin`, `vmax`, or their logical and mobile-aware variants.
4. **CSS math functions:** Express continuous, bounded relationships with `calc()`, `min()`, `max()`, and `clamp()`.
5. **Media queries:** Apply discrete layout-level decisions at explicit width, height, or aspect-ratio conditions.
6. **JavaScript:** Calculate from runtime measurements or data and manipulate the DOM when CSS cannot express the behavior.

### Three-stage liquid layout conversion

Convert a fixed-width layout into a **liquid layout** as follows:

1. Choose a readable maximum width and apply it to the outermost container with `max-width`.
2. Convert each fixed child width using:

   \[
   \text{element percentage}
   =
   \left(
   \frac{\text{element fixed width}}{\text{parent fixed width}}
   \right)
   \times 100
   \]

3. Apply the same formula to fixed margins and padding that should scale with the layout.

### Bounded fluid sizing

Model a fluid property as a linear relationship and then cap it:

\[
y = mx + b
\]

\[
m
=
\frac{\text{change in property value}}{\text{change in viewport width}}
\]

For the chapter’s `clamp()` calculations:

\[
\text{preferredValue}
=
\frac{\text{maxValue} - \text{minValue}}
{\text{maxVW} - \text{minVW}}
\times 100
\]

Then declare:

`property: clamp(minValue, preferredValue, maxValue);`

### Proportional runtime allocation

When JavaScript receives weighted items dynamically, allocate usable width in two stages:

\[
\text{totalGapWidth}
=
\text{gap}
\times
(\text{widgetCount} - 1)
\]

\[
\text{usableWidth}
=
\text{containerWidth}
-
\text{totalGapWidth}
\]

For each widget:

\[
\text{widget width}
=
\frac{\text{widget weight}}{\text{total weight}}
\times
\text{usableWidth}
\]

Set the calculated result through `widget.style.flexBasis`.

## Key Concepts

1. **Media query conditional logic**  
   `min-width: 768px` means viewport width is greater than or equal to `768px`; `max-width: 768px` means less than or equal to it. Use media queries for discrete rule changes rather than ordinary scaling.

2. **Range syntax**  
   Modern CSS can express a closed interval directly:

   `@media (600px <= width <= 1024px)`

   The supported comparison operators are `<`, `<=`, `>`, and `>=`, with the `width` and `height` media feature keywords. Prefer range syntax for clarity unless supporting old browsers.

3. **Percentage containing block**  
   Percentages do not all mean “percentage of the screen.” Horizontal widths, margins, and padding resolve against the parent’s width. Even vertical percentage margins and padding resolve against the parent’s width.

4. **Percentage height resolution**  
   `height`, `min-height`, and `max-height` percentages require an explicit parent height. Without one, the percentage has nothing definite to resolve against and may be treated as `auto` or `0`, depending on layout context.

5. **Nested percentages**  
   Percentage relationships multiply through the containing hierarchy. If `.outer` is `80%` of a `1000px` parent and `.inner` is `50%` of `.outer`, their widths are `800px` and `400px`, respectively.

6. **Initial containing block**  
   Classic viewport units are relative to the initial containing block—the browser viewport for these layout purposes—not to an element’s parent.

7. **Logical viewport units**  
   `vb` measures the viewport block dimension and `vi` measures the viewport inline dimension. Use them for writing-mode-aware layouts, including multilingual and vertical writing designs.

8. **Small, large, and dynamic viewports**  
   The `sv*`, `lv*`, and `dv*` families distinguish the viewport with browser UI visible, hidden, or changing in real time.

9. **Fluid CSS functions**  
   Use `calc()` to combine units or express a linear calculation. Use `min()` and `max()` to enforce one-sided limits. Use `clamp()` to combine a minimum, fluid preferred value, and maximum.

10. **Dynamic proportional sizing**  
    CSS can allocate known proportions, but JavaScript is appropriate when weights arrive from an API or calculations depend on live container measurements.

## Mental Models

### 1. Parent, viewport, or runtime?

Before choosing a unit, identify the reference frame:

- **Parent:** use `%`.
- **Viewport:** use `vw`, `vh`, `vmin`, `vmax`, or related families.
- **Runtime data or measurements:** calculate with JavaScript.

A child declared as `width: 75%` inside an `800px` parent is `600px` wide even if the screen itself is `2000px` wide.

### 2. Continuous behavior versus threshold behavior

Use fluid units and CSS functions when a value should change continuously. Use a media query when the rule itself should change, such as moving from one column to two columns or revealing navigation.

Prefer `clamp()` for gradual growth because breakpoint-only designs can produce abrupt layout shifts.

### 3. Minimum, maximum, and current mobile viewport

Treat mobile viewport height as three related measurements:

- `svh`: stable minimum content area with browser UI visible.
- `lvh`: maximum content area with browser UI hidden.
- `dvh`: current content area, updated as browser UI appears or disappears.

Choose according to whether safety, maximum coverage, or real-time coverage is most important.

### 4. Space must be allocated after subtraction

For proportional JavaScript layouts, do not divide the entire container width among items and then add gaps. Subtract total gap width first, then distribute only the usable width by weight.

## Anti-patterns

- **Fixed-width primary content:** A wide fixed element creates horizontal scrolling when the viewport becomes narrower.
- **Fixed image width and height:** Resizing both dimensions independently can distort the image. Prefer a proportional width with `height: auto`.
- **Reaching for media queries immediately:** Grid and Flexbox may already provide the required growing, shrinking, wrapping, or automatic track behavior.
- **Overlapping breakpoints:** `max-width: 768px` and `min-width: 768px` both match at exactly `768px`. Use nonoverlapping bounds such as `767px` and `768px`, or design the cascade intentionally.
- **Mixing breakpoint units:** Stick with `em` or `px`, not both. Using `em` ties breakpoints to font size and can improve accessibility.
- **Assuming vertical percentage padding uses parent height:** `padding-top`, `padding-bottom`, `margin-top`, and `margin-bottom` percentages resolve against parent width.
- **Using percentage height without an explicit parent height:** The browser lacks a definite value against which to resolve the percentage.
- **Using `100vh` blindly on mobile:** Browser chrome can make the element taller than the visible viewport, hiding bottom content or creating overflow.
- **Applying `dvh` throughout text-heavy pages:** Dynamic resizing can cause reflow while scrolling. Reserve it for crucial full-screen elements.
- **Using JavaScript for CSS-solvable layout:** Prefer CSS because percentages, viewport units, Grid, Flexbox, and CSS math functions cover most responsive sizing.
- **Ignoring gaps during weighted allocation:** This makes item widths plus gaps exceed the container’s available width.

## Code Examples

Use proportional image sizing when an image should fit any container without distortion:

```css
.hero img { display: block; width: 100%; height: auto; }
```

At a `1000px` container width, the image becomes `1000px` wide. At `375px`, it becomes `375px` wide. `height: auto` preserves the image’s proportions.

## Reference Tables

### Media query feature expressions

| Expression | Applies when |
|---|---|
| `min-width: value` | Viewport width is greater than or equal to `value` |
| `max-width: value` | Viewport width is less than or equal to `value` |
| `min-height: value` | Viewport height is greater than or equal to `value` |
| `max-height: value` | Viewport height is less than or equal to `value` |
| `aspect-ratio: value` | Viewport width divided by height equals `value` |

Traditional Boolean syntax supports `and`, comma-separated OR conditions, and `not`. Prefer range syntax on modern browsers; use Boolean combinations when legacy support requires them.

### Percentage resolution rules

| Property category | Percentage resolves against |
|---|---|
| `width`, `min-width`, `max-width` | Parent width |
| Left/right margin or padding | Parent width |
| Top/bottom margin or padding | Parent width |
| `height`, `min-height`, `max-height` | Explicit parent height |
| Absolutely positioned offsets | Containing block |
| Logical block and inline equivalents | Corresponding containing-block basis |

### Viewport unit selection

| Family | Measurement | Use when |
|---|---|---|
| `vw`, `vh` | Classic viewport width or height | Standard viewport-relative sizing |
| `vmin`, `vmax` | Smaller or larger viewport dimension | Sizing should follow viewport shape |
| `vi`, `vb` | Inline or block viewport dimension | Layout must be writing-mode aware |
| `sv*` | Small viewport with browser UI visible | Initial mobile overflow must be avoided |
| `lv*` | Large viewport with browser UI hidden | Content should target maximum available area |
| `dv*` | Current dynamic viewport | A crucial panel must track changing browser UI |

For any viewport family, one unit is `1%` of its defined viewport dimension. For example, if the viewport width is `1600px`, then `1vw = 1600px / 100 = 16px`.

### CSS math decision rules

| Tool | Use when |
|---|---|
| `calc()` | Combining units or expressing a linear calculation |
| `min()` | Selecting an upper-bounded result |
| `max()` | Selecting a lower-bounded result |
| `clamp(min, preferred, max)` | Allowing fluid growth between explicit bounds |

## Worked Example

Convert a fixed `960px` article layout into a liquid layout. The fixed design contains:

- An `article` width of `640px`
- An `aside` width of `320px`
- `16px` padding on the header and article
- `12px` padding on the aside

### Step 1: Cap the outer layout

Set the body’s maximum width to `960px`:

`body { max-width: 960px; }`

The layout can scale down on smaller screens but does not grow beyond the selected readable maximum.

### Step 2: Convert component widths

For the article:

\[
\left(\frac{640}{960}\right)\times100
=
66.666\ldots\%
\approx
66.67\%
\]

Therefore:

`article { width: 66.67%; }`

For the aside:

\[
\left(\frac{320}{960}\right)\times100
=
33.333\ldots\%
\approx
33.33\%
\]

Therefore:

`aside { width: 33.33%; }`

Together, the two component proportions represent the original `640:320`, or `2:1`, relationship.

### Step 3: Convert spacing

For `16px` padding:

\[
\left(\frac{16}{960}\right)\times100
=
1.666\ldots\%
\approx
1.67\%
\]

Apply `1.67%` to the header and article padding.

For `12px` padding:

\[
\left(\frac{12}{960}\right)\times100
=
1.25\%
\]

Apply `1.25%` to the aside padding.

### Runtime outcome

The fixed component dimensions become parent-relative proportions. As the body narrows, the article, aside, and converted spacing shrink with it while preserving their intended relationships. On wider screens, `max-width: 960px` prevents the content from becoming excessively wide.

## Key Takeaways

- Responsive design is a system of mathematical relationships, not a collection of device-specific widths.
- Prefer Grid, Flexbox, percentages, viewport units, and CSS math before adding media-query breakpoints.
- Remember that vertical percentage margins and padding resolve against parent width, while percentage heights require an explicit parent height.
- Use `svh` for a stable mobile-safe minimum and `dvh` when a crucial element must track the current visible viewport.
- Use `clamp()` to replace abrupt breakpoint jumps with bounded fluid behavior.
- Convert fixed layouts with the formula `(element fixed width / parent fixed width) * 100`.
- Bring in JavaScript when sizing depends on unknown runtime weights, live measurements, interactions, or DOM rearrangement.

## Connects To

- **Ch 1 — Web dev math fundamentals:** Ratios, proportions, percentages, inequalities, and linear relationships underpin responsive calculations.
- **Ch 2 — Math basics for JavaScript:** Weighted allocation uses arithmetic, `reduce()`, DOM measurements, and calculated style assignment.
- **Ch 3 — Math basics for CSS:** Relative units, comparison operators, and `calc()`, `min()`, `max()`, and `clamp()` provide the CSS expression layer.
- **Ch 4 — CSS Grid math:** Use `fr`, `auto-fit`, and `auto-fill` before introducing viewport-dependent layout switches.
- **Ch 5 — Flexbox math:** Flex growth, shrinkage, wrapping, `flex-basis`, and gap calculations support inherently responsive layouts.
