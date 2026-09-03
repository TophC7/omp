# Chapter 1: Web dev math fundamentals

## Core Idea

Front-end math turns visual guesswork into explicit relationships between values. Layout dimensions, responsive units, animation progress, pointer positions, and typographic scales are all mathematical outputs derived from browser state, design constants, or user input.

Use **CSS math** when the browser can determine layout, sizing, spacing, or typography at render time. Prefer functions such as `calc()`, `min()`, `max()`, and `clamp()` because they keep responsive relationships declarative.

Use **JavaScript math** when calculations depend on interaction, animation, changing browser state, or complex conditions. JavaScript provides arithmetic operators, comparison expressions, custom logic, and the `Math` object for real-time calculations.

The required mathematics is practical rather than advanced: arithmetic, algebra, ratios, powers and roots, linear equations, inequalities, geometry, trigonometry, and coordinate systems.

## Frameworks Introduced

### The CSS-versus-JavaScript Decision Rule

| Requirement | Prefer | Reason |
|---|---|---|
| Layout, sizing, spacing, or typography determined at render time | CSS | The browser can resolve contextual units and declarative functions automatically. |
| Fluid values with explicit lower and upper bounds | CSS `clamp()` | It expresses a minimum, preferred value, and maximum directly. |
| Arithmetic involving mixed CSS units | CSS `calc()` | It keeps the calculation tied to the rendering context. |
| Interaction or user-driven behavior | JavaScript | Procedural logic can respond to events and changing state. |
| Animation requiring custom calculations | JavaScript | Values can be recalculated over time, including through `requestAnimationFrame()`. |
| Loops, conditionals, or complex logic | JavaScript | CSS math does not provide general-purpose procedural control. |

In many interfaces, use both: CSS for design and JavaScript for behavior.

### Input → Relationship → Output

Model a front-end calculation as three parts:

1. **Inputs** — viewport size, parent width, scroll position, elapsed time, pointer coordinates, or design constants.
2. **Relationship** — an arithmetic expression, ratio, equation, inequality, or trigonometric function.
3. **Output** — width, position, opacity, angle, scale, animation progress, or a Boolean decision.

For example, scroll progress uses the input `window.scrollY`, relates it to the available scrolling distance, and produces a normalized progress value:

`progress = scrollY / totalHeight`

where `totalHeight = document.body.scrollHeight - window.innerHeight`.

### Front-End Math Survival Kit

Use the smallest mathematical model that describes the behavior:

- **Arithmetic** for direct numeric manipulation.
- **Algebra** for relationships involving variable values.
- **Ratios** for proportional scaling.
- **Exponents and nth roots** for nonlinear effects and distance calculations.
- **Linear equations** for constant-rate change.
- **Inequalities** for breakpoints, bounds, and validation.
- **Geometry and coordinate systems** for positions, paths, and transforms.
- **Trigonometry** for angles, circular motion, waves, and radial layouts.

## Key Concepts

1. **Operand and operator**  
   An operand is an input to an expression: a number, string, variable, function result, or object property. An operator specifies an action. JavaScript arithmetic operators include `+`, `-`, `*`, `/`, `%`, and `**`.

2. **Expression**  
   An expression combines one or more operands with operators and produces a result. CSS can express arithmetic through functions such as `calc()`, while JavaScript supports dynamic expressions directly.

3. **Variable value and constant**  
   A variable value represents a quantity that may change, such as viewport width, scroll position, `speed`, or `time`. A constant, also called a **numeric literal**, is fixed, such as `2`, `0.5`, or `3rem`.

4. **Ratio and aspect ratio**  
   A ratio compares quantities and may be written as `a:b`, `a/b`, a decimal, or a percentage. An **aspect ratio** is width divided by height. A `16:9` element has 16 units of width for every 9 units of height.

5. **Exponent and nth root**  
   An exponent states how many times a base is multiplied by itself. The nth root is the value that produces the original value when raised to the nth power. A highest exponent of `2` makes an expression **quadratic**; a highest exponent of `1` makes it **linear**.

6. **Linear equation**  
   The standard form is `y = mx + b`, where `x` is the independent variable, `y` is the dependent variable, `m` is the slope or rate of change, and `b` is the y-intercept or starting value. Use this model for constant-speed motion and fluid values with a fixed offset.

7. **Inequality and comparison expression**  
   Inequalities decide whether values satisfy conditions. JavaScript uses explicit operators such as `>`, `<`, `!=`, `>=`, `<=`, and `==`. CSS often expresses comparisons implicitly: `min-width` implies `>=`, while `clamp(1rem, 2vw, 2rem)` bounds a value between `1rem` and `2rem`.

8. **Viewport coordinate system**  
   The viewport origin `(0, 0)` is at the top-left. Positive x extends rightward, and positive y extends downward. Coordinates are measured in pixels by default; negative values and values beyond the viewport dimensions are allowed.

9. **Trigonometric functions**  
   For a right triangle, sine is opposite divided by hypotenuse, cosine is adjacent divided by hypotenuse, and tangent is opposite divided by adjacent. `Math.sin()` and `Math.cos()` convert an angle and radius into circular positions; `Math.atan2()` supports angle and direction calculations.

## Mental Models

### Contextual Units Are Variable Inputs

Treat `%`, `vw`, `vh`, and `em` as inputs rather than fixed numbers. Their computed values depend on context such as parent dimensions, viewport dimensions, or font size. For example, `1vw` is one hundredth of the viewport width, and `1vh` is one hundredth of the viewport height.

### Layout Is Constraint Solving

A responsive declaration describes relationships and bounds rather than a single permanent size. Think of `width: calc(100% - 2rem)` as “available parent width minus a fixed allowance,” and `clamp(1rem, 2vw, 2rem)` as a preferred fluid value constrained by lower and upper limits.

### Motion Is Position as a Function of Time

Represent constant motion with `position = initial + speed * time`, equivalent to `y = mx + b`. Use nonlinear expressions when the rate must change. For example, `1 - Math.pow(time / duration, 2)` produces an opacity that fades slowly at first and then more quickly.

### UI Space Is a Coordinate Plane

Treat pointer positions, element bounds, and movement as points and vectors. APIs such as `getBoundingClientRect()`, `clientX`, and `clientY` report values relative to the viewport origin, so calculations must use a consistent coordinate system.

## Anti-patterns

- **Guessing and repeatedly tweaking values until a layout “looks right.”** Model spacing, alignment, and sizing explicitly so failures can be traced to inputs and relationships.
- **Assuming contextual units are fixed values.** The same `em` declaration can render differently in different inheritance contexts. Do not assume identical declarations guarantee identical computed sizes.
- **Using JavaScript for calculations the browser can resolve declaratively.** Prefer CSS for render-time layout, sizing, spacing, and typography; JavaScript adds unnecessary procedural logic in these cases.
- **Forcing complex behavior into CSS math.** CSS math does not provide loops, general conditionals, or arbitrary custom logic. Move interaction-driven or complex calculations to JavaScript.
- **Ignoring bounds on fluid values.** A viewport-relative value can continue growing or shrinking. Use `clamp()`, `min()`, or `max()` when the design requires limits.
- **Mixing coordinate references.** `clientX`, `clientY`, and `getBoundingClientRect()` are viewport-relative. Treating them as though they use another origin makes position and interaction calculations inconsistent.
- **Using proportional media dimensions without preserving aspect ratio.** Prefer `aspect-ratio` or an equivalent width-to-height calculation to avoid distortion.
- **Treating animation as disconnected frame values.** Model position, opacity, or scale as a function of elapsed time so motion remains explainable and adjustable.

## Code Examples

Use the Pythagorean theorem when an interaction needs the straight-line distance between two points:

```javascript
const dx = x2 - x1;
const dy = y2 - y1;
const distance = Math.sqrt(dx * dx + dy * dy);
```

The horizontal and vertical differences form the two sides of a right triangle. Squaring them, adding the results, and taking the square root produces the distance between `(x1, y1)` and `(x2, y2)`.

## Reference Tables

### Mathematical Models

| Model | Exact form | Front-end use |
|---|---|---|
| Remaining quantity | `whole - used` | Remaining viewport height or content width |
| Ratio | `a / b` | Aspect ratio, progress, scaling |
| Linear equation | `y = mx + b` | Constant-rate motion and responsive sizing |
| Distance | `√(dx² + dy²)` | Drag distance and point-to-point measurement |
| Circular x-coordinate | `centerX + radius * cos(angle)` | Radial layouts and circular motion |
| Circular y-coordinate | `centerY + radius * sin(angle)` | Radial layouts and circular motion |
| Quadratic fade | `1 - (time / duration)²` | Opacity that decreases faster over time |

### JavaScript `Math` Tools

| API | Use |
|---|---|
| `Math.round()` | Round to the nearest integer |
| `Math.floor()` | Round downward |
| `Math.ceil()` | Round upward |
| `Math.random()` | Generate random numbers |
| `Math.max()` / `Math.min()` | Determine numeric extremes |
| `Math.abs()` | Measure absolute value, distance, or change |
| `Math.pow()` | Perform exponentiation |
| `Math.sqrt()` | Calculate square roots |
| `Math.sin()` / `Math.cos()` | Calculate wave or circular positions |
| `Math.atan2()` | Work with angles and direction |

### Common CSS Mathematical Relationships

| Syntax | Relationship |
|---|---|
| `calc(100% - 2rem)` | Contextual whole minus fixed spacing |
| `calc(50vw + 20px)` | `y = mx + b`, with `m = 0.5` and `b = 20px` |
| `clamp(1rem, 2vw, 2rem)` | Lower bound, preferred value, upper bound |
| `aspect-ratio: 16 / 9` | Width-to-height ratio |
| `grid-template-columns: 3fr 2fr 1fr` | Column ratio `3:2:1` |
| `left: 50%` with `translateX(-50%)` | Parent-relative positioning corrected by element-relative translation |

## Worked Example

Arrange six `40px × 40px` menu items evenly around a circle centered at `(100px, 100px)` with a radius of `70px`.

The angle for item index `i` is:

`angle = (2 * Math.PI / totalItems) * i`

For the first item:

1. `totalItems = 6`
2. `i = 0`
3. `angle = (2 * Math.PI / 6) * 0`
4. `angle = 0`

Calculate the horizontal position:

1. `x = centerX + radius * Math.cos(angle) - 20`
2. `x = 100 + 70 * Math.cos(0) - 20`
3. `Math.cos(0) = 1`
4. `x = 100 + 70 - 20`
5. `x = 150`

Calculate the vertical position:

1. `y = centerY + radius * Math.sin(angle) - 20`
2. `y = 100 + 70 * Math.sin(0) - 20`
3. `Math.sin(0) = 0`
4. `y = 100 + 0 - 20`
5. `y = 80`

The first item receives a left position of `150px` and a top position of `80px`. Subtracting `20px`, half the item’s width and height, centers the `40px × 40px` item on the calculated point. Repeating the formula for indexes `0` through `5` spaces all six items evenly around the circle.

## Key Takeaways

- Treat front-end values as mathematical relationships, not isolated numbers.
- Use CSS math when the browser can resolve the result from rendering context; use JavaScript when behavior requires events, time, or complex logic.
- Model constant change with `y = mx + b`, proportional change with ratios, and bounded fluid values with `clamp()`.
- Keep coordinate origins consistent when combining pointer positions, element measurements, and transforms.
- Use geometry and trigonometry for distance, direction, rotation, circular placement, and wave-like motion.
- Prefer explicit formulas over visual trial and error because formulas make layouts and interactions easier to debug and maintain.

## Connects To

- **Ch 2 — Math basics for JavaScript:** Arithmetic and comparison operators, expressions, the `Math` object, `Math.pow()`, and `Math.sqrt()`.
- **Ch 3 — Math basics for CSS:** `calc()`, `clamp()`, CSS operators, contextual units, and the inheritance math behind `em`.
- **Ch 4 — CSS Grid math:** Fractional ratios, columns, gutters, and grid sizing.
- **Ch 5 — Flexbox math:** Ratios, proportions, and distribution of available space.
- **Ch 6 — The mathematics of responsive design:** Percentages, viewport units, scaling, constraints, and responsive breakpoints.
- **Ch 7 — The mathematics of color:** Numerical manipulation of brightness, contrast, and color values.
