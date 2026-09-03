# Chapter 2: Math basics for JavaScript

## Core Idea

JavaScript makes numeric work concise, but reliable math requires explicit decisions about types, precision, operators, ranges, and output formats.

Most JavaScript values used for layout, animation, dates, pricing, and array traversal have the `number` type. JavaScript stores these values as 64-bit IEEE 754 floating-point numbers, so integers and decimals share one representation. This simplifies arithmetic but introduces two boundaries:

- Integers are exact only from `-(2 ** 53 - 1)` through `2 ** 53 - 1`.
- Many decimal fractions are approximations, so direct equality can fail even when the mathematical values appear equal.

Use strict comparisons, explicit numeric conversion, parentheses, range checks, true modulo, and task-specific rounding to make calculations predictable. Use `BigInt` only when exact integers must exceed the safe `number` range.

## Frameworks Introduced

### Expression-safety framework

Build expressions from **operands**—numbers, variables, object properties, or function results—and **operators**, then verify four things:

1. **Types:** Convert string input before arithmetic or comparison.
2. **Grouping:** Use parentheses to expose the intended order.
3. **Range:** Check whether integers are safe and results are finite.
4. **Precision:** Round or use an EPSILON comparison when decimals must be compared.

Prefer `===` and `!==` because they do not perform type coercion. Prefer `+=` and `-=` over `++` and `--` when mutation timing could be ambiguous.

### Numeric-type decision framework

Use `number` when values:

- Participate in layout, styles, animation, or DOM APIs.
- Need decimal fractions.
- Remain within the safe integer range.

Use `BigInt` when values:

- Are integers only.
- May exceed `Number.MAX_SAFE_INTEGER` or fall below `Number.MIN_SAFE_INTEGER`.
- Must remain exact during behind-the-scenes calculations.

Do not mix `number` and `bigint` in arithmetic expressions. Convert explicitly with `BigInt()` or an `n` integer suffix.

### Cyclic-value framework

JavaScript’s `%` is a **remainder operator**, not mathematical modulo. Its result has the same sign as the dividend, so a negative dividend can produce a negative array index.

For wrapping indexes, use:

`((dividend % divisor) + divisor) % divisor`

Use true modulo for carousels, tab panels, color palettes, pagination controls, and looping animation frames.

### Output-control framework

Separate calculation from presentation:

- Use `Math.round()`, `Math.floor()`, `Math.ceil()`, or `Math.trunc()` when a whole-number result is required.
- Use `.toFixed(digits)` for a fixed number of decimal places.
- Use `.toPrecision(digits)` for significant digits.
- Remember that `.toFixed()` and `.toPrecision()` return strings; convert back with `parseFloat()` before further numeric work.

## Key Concepts

1. **Operator precedence**  
   JavaScript evaluates higher-precedence operators first. The practical sequence for common arithmetic is parentheses, exponentiation, multiplication/division/remainder, addition/subtraction, comparisons, logical operators, and assignment. For example, `10 + 4 * 2 ** 2` evaluates to `26`.

2. **Pre-increment and post-increment**  
   With `let y = x++;`, assignment happens before incrementing. With `let y = ++x;`, incrementing happens before assignment. Use these operators mainly as loop counters; prefer `x += 1` when clarity matters.

3. **Strict equality and coercion**  
   `"5" == 5` is `true`, but `"5" === 5` is `false`. Convert expected numeric input first—for example, `Number(input)`—then compare with `===`.

4. **Falsy, truthy, and nullish values**  
   Falsy values are `false`, `0`, `-0`, `0n`, `""`, `''`, `null`, `undefined`, `NaN`, and deprecated `document.all`. Everything else is truthy. Use `value || fallback` when every falsy value should trigger the fallback. Use `value ?? fallback` when only `null` or `undefined` should do so.

5. **Safe integers**  
   `Number.MAX_SAFE_INTEGER` is `9007199254740991`; `Number.MIN_SAFE_INTEGER` is `-9007199254740991`. Outside this range, nearby integers may become indistinguishable. Use `Number.isSafeInteger(value)` before relying on exact integer identity.

6. **Special numeric values**  
   `NaN`, `Infinity`, and `-Infinity` all have the `number` type. Because `NaN === NaN` is `false`, test it with `Number.isNaN(value)`. Use `Number.isFinite(value)` to reject either infinity.

7. **Floating-point approximation**  
   Values such as `0.1` and `0.2` do not have exact finite binary representations. Therefore, `0.1 + 0.2 === 0.3` is `false`. For close values, use `Math.abs(a - b) < Number.EPSILON`. `Number.EPSILON` is `2 ** -52`, approximately `2.220446049250313e-16`.

8. **BigInt**  
   Create a BigInt with an `n` suffix, such as `9007199254740992n`, or with `BigInt("123456789012345678901234567890")`. BigInt division truncates the fractional part because BigInt supports integers only.

9. **Pseudo-random numbers**  
   `Math.random()` returns a pseudo-random floating-point value in `[0, 1)`. It is suitable for games, shuffling, simulations, and visual variation, but not cryptography, secure tokens, or passwords. Its internal seed is not exposed or controllable.

## Mental Models

### 1. A JavaScript number is a floating-point container

Do not model `number` as “integer or decimal.” Model it as one IEEE 754 floating-point format that can represent both. This explains why whole-number arithmetic is exact only within the safe range and why many decimal calculations are approximate.

### 2. Expressions are precedence trees

Read an expression as a tree rather than strictly from left to right. In `a += b * 3`, multiplication occurs first, producing the equivalent of `a = a + (b * 3)`. Add parentheses when the intended tree is not immediately obvious.

### 3. Cyclic indexes live on a circle

A carousel index does not stop at either end; it wraps around a circle of length `n`. Moving backward from index `0` should reach index `n - 1`, not `-1`. Mathematical modulo performs this wrapping; JavaScript remainder may not.

## Anti-patterns

- **Using loose equality for DOM or user input:** `"100" == 100` hides a type mismatch. Convert first and use `===`.
- **Assuming `+` always means addition:** If one operand is a string, `+` can concatenate. `"20" + 23` produces `"2023"`.
- **Using `||` when `0`, `false`, or `""` are valid:** Prefer `??` when only missing values should receive a default.
- **Comparing decimal calculations directly:** Avoid checks such as `calculated === expected` when binary approximation may be present.
- **Trusting integers outside the safe range:** `Number.MAX_SAFE_INTEGER + 1` and `Number.MAX_SAFE_INTEGER + 2` can produce the same value.
- **Mixing `number` and `bigint` in arithmetic:** `5n + 1` throws a `TypeError`. Convert the second operand to `1n`.
- **Using BigInt for rendering:** BigInt is unsupported by `Math` methods, does not automatically work with DOM or CSS APIs, and conflicts with `JSON.stringify()`.
- **Using `%` directly for backward wrapping:** `(index - 1) % items.length` can produce `-1`.
- **Forgetting that formatting methods return strings:** `"123.46"` from `.toFixed(2)` is display text, not a numeric result.
- **Using `Math.random()` for security:** Its pseudo-random sequence is not appropriate for cryptographic uses.

## Code Examples

Use a true modulo utility whenever a value must wrap reliably in either direction:

```js
function mod(dividend, divisor) { return ((dividend % divisor) + divisor) % divisor; }
```

The second remainder operation normalizes the adjusted result so it has the divisor’s sign.

## Reference Tables

### Operator decision table

| Need | Syntax | Practitioner rule |
|---|---|---|
| Add or concatenate | `+` | Convert operands first when numeric addition is required. |
| Increment or decrement | `++`, `--` | Prefer `+= 1` or `-= 1` except for clear loop counters. |
| Exponentiation | `**` | Evaluates before `*`, `/`, and `%`. |
| Remainder | `%` | Use directly for remainder; normalize it for cyclic indexes. |
| Strict equality | `===`, `!==` | Prefer for predictable comparisons. |
| Boolean default | `expr1 \|\| expr2` | Use when any falsy left value should select the default. |
| Nullish default | `expr1 ?? expr2` | Use when only `null` or `undefined` should select the default. |

### Numeric validation and conversion

| Task | API or syntax |
|---|---|
| Inspect a value’s type | `typeof value` |
| Convert to number | `Number(value)` or unary `+value` |
| Parse an integer prefix | `parseInt(value)` |
| Parse a floating-point prefix | `parseFloat(value)` |
| Test safe integer range | `Number.isSafeInteger(value)` |
| Test specifically for `NaN` | `Number.isNaN(value)` |
| Reject infinities | `Number.isFinite(value)` |
| Create a BigInt | `123n` or `BigInt(value)` |

### Rounding methods

| Method | Behavior | Negative-value implication |
|---|---|---|
| `Math.round(n)` | Nearest whole number; `.5` goes toward `+∞` | `Math.round(-2.5)` is `-2` |
| `Math.floor(n)` | Toward `-∞` | `Math.floor(-2.9)` is `-3` |
| `Math.ceil(n)` | Toward `+∞` | `Math.ceil(-2.1)` is `-2` |
| `Math.trunc(n)` | Removes the fractional part | Moves toward zero |
| `n.toFixed(digits)` | Fixed decimal places | Returns a string |
| `n.toPrecision(digits)` | Fixed significant digits | Returns a string |

Use **bankers’ rounding**, also called **round half to even**, when repeated financial or statistical rounding should reduce bias. Exact halfway values go to the nearest even whole number; other values use ordinary nearest-number rounding.

### Range-generation formulas

| Required range | Formula |
|---|---|
| Float in `[0, max)` | `Math.random() * max` |
| Float in `[min, max)` | `Math.random() * (max - min) + min` |
| Integer in `[min, max]` | `Math.floor(Math.random() * (max - min + 1)) + min` |
| Array index in `[0, array.length)` | `Math.floor(Math.random() * array.length)` |

For repeatable randomness, the chapter’s seedable **Linear Congruential Generator (LCG)** updates its state with `seed = (seed * 16807) % 2147483647` and normalizes with `(seed - 1) / 2147483646`.

## Worked Example

Consider a five-image carousel with indexes `0` through `4`. The current image is at index `0`, and the user clicks **Back**.

A naive remainder update gives:

1. Start with `index = 0`.
2. Subtract one: `index - 1 = -1`.
3. Apply JavaScript remainder: `-1 % 5 = -1`.
4. Attempt to read `images[-1]`.
5. The array lookup returns `undefined`, so the carousel fails or behaves unexpectedly.

Apply true modulo instead:

1. Compute the initial remainder: `-1 % 5 = -1`.
2. Add the divisor: `-1 + 5 = 4`.
3. Normalize again: `4 % 5 = 4`.
4. Set `currentIndex` to `4`.
5. Render `images[4]`, the fifth and final image.

Forward movement wraps symmetrically. From index `4`, moving forward gives:

1. `4 + 1 = 5`
2. `5 % 5 = 0`
3. The carousel renders the first image.

True modulo therefore keeps every runtime index within the valid range `[0, images.length - 1]`, regardless of movement direction.

## Key Takeaways

- Prefer explicit numeric conversion, strict equality, and parentheses because JavaScript otherwise permits coercion and precedence-driven surprises.
- Treat ordinary JavaScript numbers as IEEE 754 floating-point values, not as separate integer and decimal types.
- Check exact integers with `Number.isSafeInteger()` and use `BigInt` only when arbitrarily large integer precision is required.
- Compare approximate decimals with `Math.abs(a - b) < Number.EPSILON` or round them for the required output.
- Use true modulo rather than `%` alone for backward and forward cyclic UI behavior.
- Choose rounding by direction and purpose; remember that `.toFixed()` and `.toPrecision()` produce strings.
- Use `Math.random()` for nonsecure visual and interactive variation, and a seedable generator when repeatability is required.

## Connects To

- **Ch 1: Web dev math fundamentals** — Expression structure, order of operations, exponentiation, remainders, and mathematical modulo.
- **Ch 3: Math basics for CSS** — Numeric conversion and rounding before passing calculated values to CSS.
- **Ch 4: CSS Grid math** — Safe arithmetic, division, and rounding for track and gutter calculations.
- **Ch 5: Flexbox math** — Numeric reasoning for available space, dimensions, and distributed layout.
- **Ch 6: The mathematics of responsive design** — Parenthesized formulas, breakpoint comparisons, scaling, and decimal precision.
- **Ch 7: The mathematics of color** — Random RGB components, hexadecimal representations, and bounded numeric channels.
