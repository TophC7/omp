# Chapter 4: CSS Grid math

## Core Idea

CSS Grid is a two-dimensional algebraic layout system. Setting `display: grid` establishes a **grid formatting context** in which the container computes the sizes and positions of its child grid items rather than laying them out in normal block or inline flow.

Grid combines two mathematical systems:

1. A **discrete coordinate system** formed by numbered horizontal and vertical grid lines.
2. A **constraint-based sizing system** that allocates fixed, intrinsic, and flexible track sizes.

For a declaration such as `grid-template-columns: 1fr 2fr 1fr`, let `x = 1fr` and `w` be the available width:

`x + 2x + x = w`

`4x = w`

`x = w / 4`

The browser solves this relationship again whenever the container size changes. Understanding the coordinates, available-space budget, and track constraints makes Grid layouts more intentional and easier to troubleshoot than trial-and-error “Grid hacking.”

## Frameworks Introduced

### Grid formatting context

When a container uses `display: grid`:

- Its children leave the default block or inline flow.
- The container becomes responsible for child sizing and placement.
- Inline children do not line-wrap; they are placed in individual grid cells.
- Rows and columns can be controlled as a unified two-dimensional layout.

### Coordinate-placement framework

Treat a grid as a Cartesian plane:

- Columns occupy the horizontal axis.
- Rows occupy the vertical axis.
- A cell is bounded by two vertical and two horizontal grid lines.
- Positive line numbers begin at `1` from the top-left.
- Negative line numbers count backward from the bottom-right.

Place an item by specifying its boundary lines, not by naming a cell. For example, `grid-column: 3 / 4` places an item between vertical lines 3 and 4.

Use the browser’s Grid overlay and line-number annotations when verifying these coordinates.

### Grid track sizing algorithm

The **grid track sizing algorithm** resolves each row or column in four ordered phases:

1. **Determine which tracks exist**
   - **Explicit tracks** come from `grid-template-columns` and `grid-template-rows`.
   - **Implicit tracks** are created when items are placed outside the explicit grid or when Grid needs additional tracks.

2. **Set intrinsic track sizes**
   - The minimum contribution is the smallest size that avoids clipping.
   - The maximum contribution is the space needed for fully expanded content.

3. **Apply content-based growth or shrinkage**
   - Resolve constraints from values such as `min-content`, `max-content`, and `minmax()`.

4. **Distribute remaining space**
   - Allocate leftover space among tracks using `fr` values.

The complete flexible-track process computes a **hypothetical fr size**, tests it against track constraints, removes tracks that reach a minimum or maximum, and recalculates distribution for the remaining tracks.

### Track-sizing decision framework

- Use a fixed unit such as `px` when a track requires a fixed size.
- Use `fr` when tracks should divide remaining space proportionally.
- Use `minmax(min, max)` when a track needs explicit lower and upper constraints.
- Use `auto` when sizing should follow content and item-level `min-width` or `max-width`.
- Prefer `fit-content(limit)` when the maximum must be visible in the grid definition.
- Use `repeat(n, pattern)` for a fixed repeating sequence.
- Use `repeat(auto-fill, ...)` to preserve empty tracks.
- Use `repeat(auto-fit, ...)` to collapse empty tracks and redistribute their space.

## Key Concepts

1. **Grid lines, tracks, and cells**  
   A track exists between two adjacent grid lines. A cell exists between four lines. A three-column grid has four vertical lines; a two-row grid has three horizontal lines.

2. **One-based line numbering**  
   CSS Grid lines start at `1`, not `0`. The third column is bounded by lines `3` and `4`.

3. **Placement shorthands**  
   `grid-column` is shorthand for `grid-column-start` and `grid-column-end`. Similarly, `grid-row` represents `grid-row-start` and `grid-row-end`.

4. **Span notation**  
   If an item starts at line `n` and spans `m` tracks, its end line is:

   `end_line = n + m`

   Therefore, `grid-column: 2 / span 3` is equivalent to `grid-column: 2 / 5`. Use `span` when the number of occupied tracks matters more than the absolute ending line.

5. **Negative indexing**  
   Line `-1` is the final explicit grid line and `-2` is the second-to-last. Use `grid-column: 1 / -1` for a full-width item whose grid may change size. Negative line numbers apply only to **explicit tracks**, not auto-generated implicit tracks.

6. **Fractional units**  
   An `fr` is a flexible length, represented by the `<flex>` data type. It receives a fraction of the space left after fixed tracks and gaps—and, under `box-sizing: border-box`, applicable borders and padding—have been removed.

   Let:

   - `C` = container size
   - `F` = total fixed-track size
   - `G` = total gap size
   - `B` = relevant border widths
   - `P` = relevant padding
   - `R = C - F - G - B - P`
   - `T` = sum of all `fr` values

   For a track sized `nfr`:

   `W = (n / T) * R`

7. **Minimum-content protection**  
   If fixed tracks consume all available space, a flexible track can calculate to `0px`. Content may still force the rendered track to its intrinsic minimum:

   `actual_track_width = max(calculated_flex_value, min_content_width)`

   An empty flexible track with no minimum content contribution can remain `0px`.

8. **`minmax()` constraints**  
   `minmax(min, max)` keeps a track greater than or equal to `min` and less than or equal to `max`. If `max` is less than `min`, the browser ignores `max` and uses `min`. An `fr` value is invalid as the minimum argument but is particularly useful as the maximum, as in `minmax(250px, 1fr)`.

9. **Intrinsic and bounded sizing**
   - `min-content` is the smallest size that avoids overflow, often determined by the widest unbreakable content.
   - `max-content` is the size needed to display content without wrapping.
   - `auto` is essentially `minmax(min-content, max-content)`, but also respects item-level minimum and maximum properties. For columns:

     `minmax(max(min-width, min-content), min(max-width, max-content))`

   - `fit-content(limit)` uses:

     `max(minimum, min(limit, max-content))`

     It allows growth toward the content size without exceeding `limit`, while preserving the applicable minimum.

10. **Repeating tracks**  
    `repeat(n, pattern)` expands a track pattern `n` times. If the pattern contains three tracks and repeats twice:

    `total_tracks = pattern_length * repetitions = 3 * 2 = 6`

    The chapter models automatic repetition as:

    `num_repetitions = floor((container_width - sum_of_gaps) / track_width)`

## Mental Models

### 1. Lines are coordinates; tracks are intervals

Do not think “put this item in column 3.” Think “place this item between vertical lines 3 and 4.” This model also explains multi-cell placement, `span`, and negative indexing.

### 2. Fixed costs first, flexible shares second

Treat container space as a budget. Deduct fixed tracks, gaps, borders, and padding before dividing the remainder among `fr` tracks. An `fr` is a share of the remainder, not a percentage of the container’s declared width.

### 3. Track sizing is constrained equation solving

Grid does not perform a single division and stop. It first computes a hypothetical flexible size, checks intrinsic and `minmax()` constraints, fixes any tracks that hit boundaries, and redistributes the remaining space. A minimum can therefore change the widths of neighboring `fr` tracks.

### 4. Explicit boundaries enable reliable end-relative placement

Negative coordinates are references to the boundaries of the explicit grid. Implicit tracks sit outside that dependable coordinate system. If an item must remain in the last row, define that row explicitly before relying on `-2 / -1`.

## Anti-patterns

- **Using zero-based assumptions.** Grid line `0` is not the first line; line numbering starts at `1`.
- **Hard-coding an end line in a dynamic grid.** Avoid `grid-column: 1 / span 3` when the column count can change. Prefer `grid-column: 1 / -1`.
- **Using negative indices with implicit tracks.** A footer assigned `grid-row: -2 / -1` will not target the final row created by `grid-auto-rows`. Define explicit rows when end-relative placement is required.
- **Dividing the full container width among `fr` tracks.** Deduct fixed tracks, every gap, and—under `border-box`—the relevant padding and borders first.
- **Assuming `1fr` guarantees visible free space.** If fixed costs equal or exceed the container size, `<flex>` resolves to `0px`; content may then overflow at its minimum width.
- **Using `fr` as the minimum in `minmax()`.** Flexible lengths are invalid in the minimum position. Use a fixed or intrinsic minimum and place `fr` in the maximum position.
- **Using `auto` when the grid must own a strict cap.** Item-level constraints may live elsewhere and be difficult to audit. Prefer `fit-content(limit)` when the maximum belongs in the track definition.
- **Choosing `auto-fill` while expecting existing items to stretch.** `auto-fill` preserves empty tracks. Use `auto-fit` when unused tracks should collapse and release their space.
- **Relying exclusively on visual trial and error.** Inspect line numbers and calculate the available-space budget before changing unrelated Grid properties.

## Code Examples

Use `auto-fit` with `minmax()` when responsive columns must remain at least `180px` wide, grow into available space, and collapse when unused:

```css
.gallery { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); }
```

The minimum controls readability, `1fr` permits growth, and `auto-fit` prevents empty columns from reserving space.

## Reference Tables

| Placement goal | CSS syntax | Decision rule |
|---|---|---|
| One cell in column 3, row 2 | `grid-column: 3 / 4; grid-row: 2 / 3` | Specify the four bounding lines |
| Cover three tracks from line 2 | `grid-column: 2 / span 3` | End line is `2 + 3 = 5` |
| Cover every explicit column | `grid-column: 1 / -1` | Prefer for changing column counts |
| Occupy the final explicit row | `grid-row: -2 / -1` | Valid only when that row is explicit |

| Track value | Mathematical behavior | Use when |
|---|---|---|
| `px` | Fixed allocation | A dimension must remain fixed |
| `fr` | Proportional share of remaining space | Tracks should expand together |
| `min-content` | Intrinsic minimum | The widest unbreakable content sets the floor |
| `max-content` | No-wrap intrinsic size | Content should determine full width |
| `auto` | Content-aware range respecting item constraints | Item CSS should control bounds |
| `minmax(min, max)` | Explicit bounded interval | A responsive track needs a floor or ceiling |
| `fit-content(limit)` | Content-sized track capped by `limit` | The cap should live in the grid definition |

| Repetition mode | Empty-track behavior | Prefer when |
|---|---|---|
| `repeat(n, pattern)` | Creates exactly `n` pattern repetitions | The track count is known |
| `auto-fill` | Retains empty tracks at their calculated size | Preserving the available grid structure matters |
| `auto-fit` | Collapses empty tracks to `0px` and redistributes space | Existing items should fill the container |

## Worked Example

Assume `box-sizing: border-box` and a grid with:

- Container width: `800px`
- Columns: `200px 2fr 1fr`
- Gap: `30px`
- Border: `6px` on each side
- Padding: `15px` on each side

There are three columns, so there are two horizontal gaps.

### 1. Calculate fixed-track space

`F = 200px`

### 2. Calculate total gap space

`G = 2 * 30px = 60px`

### 3. Calculate horizontal borders and padding

`B = 2 * 6px = 12px`

`P = 2 * 15px = 30px`

### 4. Calculate remaining free space

`R = C - F - G - B - P`

`R = 800px - 200px - 60px - 12px - 30px`

`R = 498px`

### 5. Calculate the flexible-unit total

`T = 2 + 1 = 3`

Therefore:

`1fr = 498px / 3 = 166px`

### 6. Resolve each flexible track

Second column:

`W = (2 / 3) * 498px = 332px`

Third column:

`W = (1 / 3) * 498px = 166px`

### Runtime outcome

The rendered columns are `200px`, `332px`, and `166px`. Together with `60px` of gaps, `30px` of padding, and `12px` of borders:

`200px + 332px + 166px + 60px + 30px + 12px = 800px`

Ignoring padding and borders would incorrectly allocate those `42px` to the flexible tracks, producing wider columns than the container’s actual content box permits.

## Key Takeaways

- Grid placement uses one-based line coordinates; items occupy the intervals between those lines.
- Use `span` for relative track counts and negative lines for end-relative placement within the explicit grid.
- Calculate `fr` values from remaining space, not total declared container size.
- Expect intrinsic minimums and `minmax()` boundaries to modify a simple fractional split.
- Prefer `fit-content(limit)` for a grid-local maximum and `auto` for content-aware sizing that respects item-level constraints.
- Use `auto-fit` to collapse unused tracks; use `auto-fill` to preserve them.
- When a flexible column disappears or overflows, verify fixed tracks, gaps, borders, padding, and minimum-content contributions before changing the layout.

## Connects To

- **Ch 1 — Web dev math fundamentals:** Supplies the arithmetic and proportional reasoning behind available-space budgets.
- **Ch 2 — Math basics for JavaScript:** Connects to algebraic solving and operations such as `floor()` and `max()`.
- **Ch 3 — Math basics for CSS:** Provides the box-model, sizing-unit, padding, border, and `box-sizing` foundations used in track calculations.
- **Ch 5 — Flexbox math:** Contrasts Grid’s two-dimensional coordinate and track model with Flexbox’s one-dimensional constraint model.
- **Ch 6 — The mathematics of responsive design:** Extends `minmax()`, `auto-fit`, `auto-fill`, and proportional tracks into layouts that adapt to changing container sizes.
