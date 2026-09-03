# Chapter 5: Flexbox math

## Core Idea

Flexbox distributes space along one dimension: the container’s **main axis**. With `flex-direction: row`, size means width; with `flex-direction: column`, size means height.

The browser resolves a flex layout in three broad stages:

1. Determine each item’s **flex base size**.
2. Compare the sum of those sizes with the container:
   - **Underflow:** distribute unused space with `flex-grow`.
   - **Overflow:** remove excess space with `flex-shrink`.
3. Apply minimum and maximum constraints, then redistribute space when an item reaches a hard limit.

Use this sequence when a Flexbox result appears unpredictable. Prefer tracing base size, free space or overflow, flex factors, and constraints rather than inspecting only the rendered width.

## Frameworks Introduced

### Flex base size decision rule

For each flex item:

1. If `flex-basis` has a specific value—a length, percentage, `content`, `max-content`, `min-content`, or `fit-content`—use it as the **flex base size**.
2. If `flex-basis: auto`:
   - Use `width` when the main axis is horizontal and `width` is specified.
   - Otherwise, use the item’s intrinsic content size.

Therefore, `flex-basis: 100px; width: 200px;` produces a base size of `100px`. A non-`auto` `flex-basis` takes precedence over `width`.

For a vertical main axis, the corresponding sizing and constraint properties are `height`, `min-height`, and `max-height`.

### Underflow framework: flex-grow

When initial item sizes occupy less space than the container:

`available_unused_space = container_width - sum_of_initial_sizes`

For ordinary relative grow-factor distribution:

`item_unused_portion = item_flex_grow_factor / sum_of_flex_grow_factors`

`item_unused_space = item_unused_portion * available_unused_space`

`item_final_width = item_initial_size + item_unused_space`

Use `flex-grow` to divide free space proportionally. A factor of `2` receives twice the allocation of a factor of `1`, assuming the factors are being treated as relative ratios.

### Overflow framework: flex-shrink

When initial item sizes exceed the container:

`overflow = sum_of_initial_sizes - container_width`

The browser weights each shrink factor by the item’s initial size:

`item_weighted_shrink_factor = item_width * item_flex_shrink_factor`

`item_overflow_portion = item_weighted_shrink_factor / sum_of_weighted_shrink_factors`

`item_overflow_space = item_overflow_portion * overflow`

`item_final_width = item_initial_size - item_overflow_space`

Prefer thinking in terms of the **weighted shrink factor**, not `flex-shrink` alone. Two items with `flex-shrink: 1` need not lose the same number of pixels when their base sizes differ.

### Fractional flex-grow decision rule

When one or more `flex-grow` values are between `0` and `1`, inspect their sum:

- **Sum greater than or equal to `1`:** treat grow values as relative ratios using the standard grow calculation.
- **Sum less than `1`:** treat each value as a request for that fraction of the free space:

`item_unused_space = item_flex_grow_factor * available_unused_space`

In the second case, not all free space must be consumed. There is no corresponding algorithm shift for `flex-shrink`; shrink values remain relative ratios because shrinking is intended to resolve overflow.

### Constraint redistribution framework

After calculating proposed flexed sizes:

1. Clamp items that violate `min-width` or `max-width`.
2. Recalculate remaining overflow or underflow.
3. Redistribute that remainder among items that have not reached a constraint.
4. Repeat conceptually until the available space and constraints are satisfied—or hard minimums make fitting impossible.

Use `min-width` as a hard stop on shrinking and `max-width` as a hard stop on growing.

## Key Concepts

1. **Main axis** — The single dimension controlled by Flexbox. It is horizontal for `flex-direction: row` and vertical for `flex-direction: column`.
2. **Flex base size** — The item’s starting size before growing or shrinking.
3. **Flex factors** — The `flex-grow` and `flex-shrink` properties that control space distribution.
4. **Flex grow factor** — An item’s `flex-grow` value, used to allocate available unused space.
5. **Flex shrink factor** — An item’s `flex-shrink` value.
6. **Weighted shrink factor** — `item_width * item_flex_shrink_factor`; this most directly determines an item’s share of overflow.
7. **Underflow scenario** — Initial item sizes leave unused container space.
8. **Overflow scenario** — Initial item sizes exceed container space.
9. **Min/max constraints** — `min-width` and `max-width`, or their height equivalents, act as hard limits and trigger redistribution.
10. **`flex` shorthand** — Sets `flex-grow`, `flex-shrink`, and `flex-basis` together:

   `flex: flex-grow flex-shrink flex-basis;`

The default combination on flex items is `flex: 0 1 auto;`.

## Mental Models

### 1. Budget allocation

Treat the container’s main-axis size as a budget. Base sizes make the initial claims. If money remains, `flex-grow` allocates it; if claims exceed the budget, weighted `flex-shrink` determines the reductions.

### 2. Grow is ratio-based; shrink is size-weighted

For normal growth, compare grow factors directly. For shrinking, multiply each shrink factor by its initial size first. This explains why equal shrink factors do not necessarily produce equal pixel reductions.

### 3. Constraints freeze an item

When an item reaches `min-width` or `max-width`, treat it as unavailable for further movement in that direction. Redistribute the unresolved space among the remaining items.

### 4. The shorthand is a complete state

Treat every `flex` declaration as setting all three components, including implicit values. Do not assume that an earlier longhand value survives a later shorthand declaration.

## Anti-patterns

- **Reasoning from `width` while ignoring `flex-basis`.** A specific `flex-basis` overrides the declared `width` when selecting the base size.
- **Assuming `flex-shrink: 1` means equal pixel shrinkage.** Shrink allocation depends on `base size * flex-shrink`, not the factor alone.
- **Using `flex-grow` without checking the sum of fractional values.** If all values are in `(0, 1)` and total less than `1`, the browser may leave free space unused.
- **Mixing shorthand and longhand declarations carelessly.** A later `flex: 1` sets `flex-grow: 1`, `flex-shrink: 1`, and `flex-basis: 0`, potentially overriding an earlier `flex-shrink: 0`.
- **Expecting flex-shrink to defeat hard minimums.** Four items with `min-width: 225px` require at least `900px`; they cannot fit inside an `800px` container.
- **Using large grow factors as absolute widths.** Grow factors represent proportions of free space, not pixel dimensions.
- **Ignoring constraints during manual calculations.** The first grow or shrink result is only proposed; `min-width` and `max-width` can force another distribution pass.

## Code Examples

Use the shorthand to define a flexible column with an explicit starting size and hard lower and upper bounds:

```css
.column { flex: 1 1 200px; min-width: 100px; max-width: 300px; }
```

The item starts from a `200px` flex base size, may grow and shrink with factor `1`, cannot shrink below `100px`, and cannot grow above `300px`.

## Reference Tables

### Base size selection

| Condition | Flex base size |
|---|---|
| `flex-basis` is a specific length or percentage | The `flex-basis` value |
| `flex-basis` is `content`, `max-content`, `min-content`, or `fit-content` | The specified keyword’s value |
| `flex-basis: auto` and horizontal-axis `width` exists | The `width` value |
| `flex-basis: auto` and no relevant explicit size exists | Intrinsic content size |

### Space-distribution decision table

| Container state | Governing property | Allocation basis |
|---|---|---|
| Underflow | `flex-grow` | Grow factor relative to total grow factors |
| Underflow with fractional grow factors totaling less than `1` | `flex-grow` | Each factor multiplied directly by free space |
| Overflow | `flex-shrink` | Base size multiplied by shrink factor |
| Item reaches a minimum or maximum | `min-width` / `max-width` | Clamp item, then redistribute remainder |

### Practical factor choices

| Intent | Declaration strategy |
|---|---|
| Item must not grow or shrink | `flex: 0 0 auto;` |
| Item should shrink less proportionally than default items | Use `flex-shrink` between, but not including, `0` and `1` |
| Item should shrink more proportionally than default items | Use `flex-shrink` greater than `1` |
| Fix the starting size directly | Set `flex-basis` to a specific value |
| Prevent excessive shrinking | Set `min-width` on a horizontal main axis |
| Prevent excessive growth | Set `max-width` on a horizontal main axis |

## Worked Example

Consider a `600px` container with three items. Each begins at `100px`, with `flex-grow` factors `1`, `2`, and `3`. Every item also has `max-width: 220px`.

### 1. Calculate initial occupancy

`sum_of_initial_sizes = 100px + 100px + 100px = 300px`

### 2. Calculate unused space

`available_unused_space = 600px - 300px = 300px`

### 3. Calculate grow-factor proportions

`sum_of_flex_grow_factors = 1 + 2 + 3 = 6`

- Item 1: `1 / 6`
- Item 2: `2 / 6`
- Item 3: `3 / 6`

### 4. Calculate proposed growth

- Item 1: `(1 / 6) * 300px = 50px`
- Item 2: `(2 / 6) * 300px = 100px`
- Item 3: `(3 / 6) * 300px = 150px`

Proposed widths:

- Item 1: `100px + 50px = 150px`
- Item 2: `100px + 100px = 200px`
- Item 3: `100px + 150px = 250px`

### 5. Apply `max-width`

Item 3 exceeds `max-width: 220px`, so clamp it:

- Item 1: `150px`
- Item 2: `200px`
- Item 3: `220px`

Current total:

`150px + 200px + 220px = 570px`

The container still has:

`600px - 570px = 30px`

### 6. Redistribute the remaining underflow

Item 3 is constrained, so distribute the `30px` between items 1 and 2 according to grow factors `1` and `2`.

`remaining_grow_total = 1 + 2 = 3`

- Item 1 ratio: `1 / 3 = 0.33`
- Item 2 ratio: `2 / 3 = 0.67`

Additional growth:

- Item 1: `30px * 0.33 = 10px`
- Item 2: `30px * 0.67 = 20px`

### 7. Determine rendered widths

- Item 1: `150px + 10px = 160px`
- Item 2: `200px + 20px = 220px`
- Item 3: `220px`

Check:

`160px + 220px + 220px = 600px`

The rendered items exactly fill the container, and no item exceeds the `220px` maximum.

## Key Takeaways

- Begin every Flexbox diagnosis with the **flex base size**; all later calculations depend on it.
- Use `flex-grow` for underflow and weighted `flex-shrink` for overflow.
- Calculate shrinking from `base size * flex-shrink`, not from `flex-shrink` alone.
- Check whether fractional `flex-grow` values total less than `1`; if so, free space can remain.
- Prefer the `flex` shorthand when you want all three flex properties to be explicit, but account for every value it sets.
- Use `min-width` and `max-width` as hard stops, knowing that constrained items force space to be redistributed.
- Verify manual calculations by checking that final widths sum to the available container width unless fractional growth intentionally leaves unused space or minimum constraints make fitting impossible.

## Connects To

- [Web dev math fundamentals](Ch 1) — Ratios, proportions, sums, and subtraction underpin grow and shrink allocation.
- [Math basics for CSS](Ch 3) — Flexbox calculations depend on CSS dimensions, percentages, intrinsic sizing, and the box model.
- [CSS Grid math](Ch 4) — Compare Flexbox’s one-dimensional distribution with Grid’s two-dimensional track sizing.
- [The mathematics of responsive design](Ch 6) — Use flexible sizing and min/max constraints to make components adapt across available widths.
