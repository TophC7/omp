# Chapter 7: The mathematics of color

## Core Idea

Web colors are mathematical coordinates, not merely visual labels. Choose a color model according to the operation you need:

- Use **RGB** when working directly with display channels, hexadecimal colors, or pixel calculations.
- Use **HSL** when selecting and rotating hues for color harmony.
- Prefer **LAB** or **OKLCH** when changes should correspond more closely to perceived differences.
- Use **relative luminance** and the **contrast ratio**, not visual judgment, to validate accessibility.
- Transform lightness, chroma, saturation, and hue deliberately when generating dark-mode palettes.
- Treat opacity and blend modes as per-pixel mathematical operations on normalized channel values.

The central practitioner rule is to perform calculations in the color representation that matches the design decision, then validate the rendered result against accessibility and display constraints.

## Frameworks Introduced

### Color representation framework

Each model organizes color differently:

1. **RGB** represents additive red, green, and blue intensities in a cube.
2. **HSL** reorganizes color into hue, saturation, and lightness in a cylinder.
3. **LAB**, also called **CIELAB** or **CIELab**, represents perceptually uniform lightness and opponent color axes.
4. **OKLCH** combines perceptual lightness with intuitive chroma and hue controls.

Use HSL for simple hue relationships. Prefer OKLCH for perceptually even lightness or chroma scales.

### Color conversion pipeline

For RGB-to-HSL conversion:

1. Normalize channels: `Rₙ = R / 255`, `Gₙ = G / 255`, and `Bₙ = B / 255`.
2. Compute `min`, `max`, and chroma `C = max - min`.
3. Compute lightness: `L = (max + min) / 2`.
4. If `C = 0`, set `H = 0` and `S = 0`.
5. Otherwise compute saturation:

   `S = C / (1 - |2L - 1|)`

6. Derive hue from the maximum channel:
   - If `max = Rₙ`: `H = ((Gₙ - Bₙ) / C) + 6`, adding 6 only when `Gₙ < Bₙ`.
   - If `max = Gₙ`: `H = ((Bₙ - Rₙ) / C) + 2`.
   - If `max = Bₙ`: `H = ((Rₙ - Gₙ) / C) + 4`.
7. Multiply the sector result by `60°`; add `360°` if the result is negative.

For HSL-to-RGB conversion, normalize `H / 360`, `S / 100`, and `L / 100`. If saturation is zero, set every RGB channel to `L × 255`. Otherwise:

- If `L < 0.5`, `q = L × (1 + S)`.
- Otherwise, `q = L + S - L × S`.
- Then `p = 2L - q`.

Interpolate the RGB channels from hue positions `H + 1/3`, `H`, and `H - 1/3`, then scale each result by 255.

### Mathematical color-harmony framework

Treat hue as a circular value modulo `360°`. Generate related colors by adding fixed angular offsets to a base hue.

### Accessibility validation framework

1. Convert sRGB channels to normalized values.
2. Apply gamma correction to obtain linear channels.
3. Calculate relative luminance.
4. Calculate the contrast ratio.
5. Compare the ratio with the appropriate WCAG AA or AAA threshold.

### Paired light/dark palette framework

For each light-mode color:

1. Invert lightness.
2. Reduce saturation or chroma.
3. Optionally apply a small hue shift.
4. Recalculate contrast against the new background.

Do not treat dark mode as raw RGB inversion.

### Compositing framework

Blend calculations operate on normalized channel values from 0 to 1. First apply a blend function to source and backdrop colors, then account for alpha through **source-over compositing**.

## Key Concepts

1. **Additive color mixing** — RGB adds emitted light. `(0, 0, 0)` is black, `(255, 255, 255)` is white, and equal channel values form grayscale. The model contains `256³ = 16,777,216` possible channel combinations.

2. **Hex triplets** — `#rrggbb` stores two hexadecimal digits per RGB channel. `#rrggbbaa` adds alpha. A pair such as `33`, `66`, or `cc` can be shortened when every pair repeats: `#3366cc` is equivalent to `#36c`.

3. **Alpha channel** — CSS color functions add alpha after `/`, using either `[0, 1]` or `[0%, 100%]`. Zero is transparent; one or 100% is opaque.

4. **HSL coordinates** — Hue is an angle from `0°` through `359°`; saturation and lightness are percentages. `0%` saturation produces grayscale. `0%` lightness is black, `100%` is white, and `50%` is normal brightness.

5. **Perceptual uniformity** — LAB is designed so equal numeric changes correspond to equal perceived color differences. Its axes are:
   - `L`: 0 or 0% through 100 or 100%.
   - `A`: −125 green through 125 red, or −100% through 100%.
   - `B`: −125 blue through 125 yellow, or −100% through 100%.

6. **OKLCH control** — `L` ranges from 0 to 1 or 0% to 100%; `C` ranges from 0 to roughly 0.4–0.5; `H` ranges from `0°` through `359°`. Hold `C` and `H` constant when building a perceptually even lightness scale. Hold `L` and `H` constant when varying vividness.

7. **Weighted grayscale** — Human vision is more sensitive to green and less sensitive to blue. Convert RGB to perceived grayscale with:

   `gray = 0.299R + 0.587G + 0.114B`

8. **Relative luminance** — For each normalized sRGB channel `c`:

   - If `c <= 0.04045`, use `c / 12.92`.
   - Otherwise use `((c + 0.055) / 1.055) ** 2.4`.

   With linearized channels:

   `L = 0.2126Rₗ + 0.7152Gₗ + 0.0722Bₗ`

9. **Contrast ratio** — Let `L₁` be the lighter luminance and `L₂` the darker luminance:

   `CR = (L₁ + 0.05) / (L₂ + 0.05)`

   The result ranges from `1:1` to `21:1` and is independent of which color is foreground.

10. **Alpha compositing** — For source color `Cₛ`, source alpha `αₛ`, backdrop color `Cᵦ`, and backdrop alpha `αᵦ`:

    `Cout = Cₛαₛ + Cᵦαᵦ(1 - αₛ)`

    `αout = αₛ + αᵦ(1 - αₛ)`

    With an opaque backdrop, the color equation simplifies to `Cout = Cₛαₛ + Cᵦ(1 - αₛ)`.

## Mental Models

### Color spaces are coordinate systems

RGB is a cube, HSL is a cylinder, LAB is described as a sphere, and OKLCH is polar. Moving one coordinate means different things in each system. A numerical change is useful only when its axis represents the visual property you intend to change.

### Hue is modular arithmetic

Hue wraps around rather than stopping at `359°`. Think of it as a clock:

`shiftedHue = (hue + shift) mod 360`

When JavaScript shifts may be negative, use a positive modulo operation:

`((dividend % divisor) + divisor) % divisor`

### Accessibility is a pipeline, not a color guess

RGB values are not luminance values. Normalize, linearize, weight, compare, and then apply the WCAG threshold. Skipping gamma correction invalidates the result.

### Blending is channel arithmetic plus layering

Separable blend modes independently transform red, green, and blue. Non-separable modes transfer hue, saturation, or luminosity between whole colors. Opacity then controls how strongly the source contributes to the composite.

## Anti-patterns

- **Averaging RGB channels for grayscale.** `(R + G + B) / 3` ignores human visual sensitivity. Use the weighted grayscale formula.
- **Normalizing RGB by 100.** RGB channels range from 0 to 255, so divide by 255.
- **Assuming HSL steps look perceptually equal.** HSL hue rotation can change perceived brightness. Prefer OKLCH when uniform perception matters.
- **Using unchecked wide-gamut OKLCH colors.** Some values work on Display P3 screens but fail on lesser displays. Check them on regular monitors unless targeting Display P3 directly.
- **Approving contrast by eye.** Compute relative luminance and contrast, then test the correct AA or AAA threshold.
- **Reversing the contrast formula.** Always place the higher luminance in the numerator and the lower luminance in the denominator.
- **Inverting RGB for dark mode.** `255 - channel` can turn muted colors garish and distort hierarchy. Invert perceptual lightness, then adjust saturation, chroma, and hue.
- **Assuming blend modes mix every part of an element.** `background-blend-mode` blends background layers within the element; those layers do not blend with the element’s content.
- **Using blend modes without checking the backdrop.** `mix-blend-mode` depends on the parent backdrop and overlapping content, so a changed background can change the result.

## Code Examples

Use CSS custom properties and `calc()` when a palette should follow a base hue. CSS handles the hue wrapping automatically:

```css
:root {
  --base-hue: 39;
  --main-color: hsl(var(--base-hue) 100% 50%);
  --comp-color: hsl(calc(var(--base-hue) + 180) 100% 50%);
}
```

This creates a complementary pair whose hues remain `180°` apart when `--base-hue` changes.

## Reference Tables

### Choosing a color model

| Model or space | CSS syntax | Coordinate ranges | Prefer when |
|---|---|---|---|
| RGB | `rgb(R G B / A)` | Channels 0–255 or 0%–100% | Working with display channels, pixels, or hex values |
| Hex RGB | `#rrggbb` or `#rrggbbaa` | Each pair `00`–`ff` | Storing compact RGB values |
| HSL | `hsl(H S L / A)` | H 0–359; S/L 0%–100% | Rotating hues or generating simple harmonies |
| LAB | `lab(L A B / A)` | L 0%–100%; A/B −125–125 | Comparing perceptual color differences |
| OKLCH | `oklch(L C H / A)` | L 0–1; C about 0–0.4/0.5; H 0–359 | Building perceptually uniform scales and themes |

### Hue relationships

| Scheme | Offsets from base hue `H` | Decision rule |
|---|---:|---|
| Complementary | `+180°` | Use for an opposite hue |
| Analogous | `±30°`, optionally `±15°` | Use smaller offsets for less contrast |
| Triadic | `±120°` | Use for three evenly spaced hues |
| Split-complementary | `+150°`, `+210°` | Use the hues 30° to either side of the complement |

For a complementary hue:

`C = (H + 180) % 360`

### WCAG contrast thresholds

| Text classification | AA | AAA |
|---|---:|---:|
| Normal text below 18px | 4.5:1 | 7:1 |
| Regular text at least 18px | 3:1 | 4.5:1 |
| Bold text at least 14px | 3:1 | 4.5:1 |

### Common separable blend modes

| Mode | Per-channel function `B(Cᵦ, Cₛ)` | Runtime effect |
|---|---|---|
| `normal` | `Cₛ` | Source replaces backdrop |
| `multiply` | `Cᵦ * Cₛ` | Darkens; black yields black, white leaves the other color unchanged |
| `screen` | `1 - (1 - Cᵦ) * (1 - Cₛ)` | Lightens; white yields white, black leaves the other color unchanged |
| `darken` | `min(Cᵦ, Cₛ)` | Selects the darker channel |
| `lighten` | `max(Cᵦ, Cₛ)` | Selects the lighter channel |
| `difference` | `\|Cᵦ - Cₛ\|` | Identical channels become black |
| `exclusion` | `Cᵦ + Cₛ - 2CᵦCₛ` | Lower-contrast difference effect |

Use `mix-blend-mode` for an element against its backdrop. Use `background-blend-mode` for multiple backgrounds inside one element.

### Dark-mode transformation rules

| Property | Transformation |
|---|---|
| HSL lightness | `Ldark = 100 - Llight` |
| OKLCH lightness | `Ldark = 1 - Llight` |
| HSL saturation | Reduce by 10%–30% |
| OKLCH chroma | Multiply by 0.4–0.6 |
| Hue | Optionally shift by ±15°–30° |
| Final validation | Recalculate contrast against the dark background |

## Worked Example

Determine whether pure blue text on white meets WCAG contrast requirements.

**Colors**

- Blue: `rgb(0 0 255)`
- White: `rgb(255 255 255)`

### 1. Normalize blue

`Rₙ = 0 / 255 = 0`

`Gₙ = 0 / 255 = 0`

`Bₙ = 255 / 255 = 1`

### 2. Apply gamma correction

For zero-valued channels:

`Rₗ = 0 / 12.92 = 0`

`Gₗ = 0 / 12.92 = 0`

For blue, `1 > 0.04045`:

`Bₗ = ((1 + 0.055) / 1.055) ** 2.4 = 1`

### 3. Calculate blue’s relative luminance

`Lblue = 0.2126(0) + 0.7152(0) + 0.0722(1)`

`Lblue = 0.0722`

White has relative luminance `Lwhite = 1`.

### 4. Calculate contrast

White is lighter, so it supplies `L₁`:

`CR = (1 + 0.05) / (0.0722 + 0.05)`

`CR = 1.05 / 0.1222`

`CR = 8.59:1`

### 5. Connect the math to the rendered result

A ratio of `8.59:1` exceeds:

- Normal-text AA: `4.5:1`
- Normal-text AAA: `7:1`
- Large-text AA: `3:1`
- Large-text AAA: `4.5:1`

Therefore, pure blue text on white passes both AA and AAA for normal and large text.

The same blue on pure red does not work. Red has luminance `0.2126`, producing:

`CR = (0.2126 + 0.05) / (0.0722 + 0.05) = 2.15:1`

That rendered pairing fails even AA. Hue difference alone does not guarantee readable contrast.

## Key Takeaways

- Choose the color model that matches the operation: HSL for hue geometry, OKLCH for perceptually uniform adjustment, and RGB for channel-level calculations.
- Normalize RGB by 255 before conversion, luminance, or blend-mode math.
- Generate harmonies with modular hue offsets rather than selecting related colors by eye.
- Validate accessibility with gamma-corrected relative luminance and the WCAG contrast ratio.
- Prefer perceptual lightness inversion and controlled chroma or saturation reduction for dark mode; never rely on raw RGB inversion.
- Treat blend modes as deterministic formulas. Use `multiply` to darken, `screen` to lighten, and non-separable modes when transferring hue, saturation, color, or luminosity.
- Test OKLCH colors on regular monitors when not directly targeting Display P3.

## Connects To

- **Ch 1 — Web dev math fundamentals:** Normalization, weighted averages, ratios, coordinate systems, and interpolation underpin color calculations.
- **Ch 2 — Math basics for JavaScript:** Use `Math.min()`, `Math.max()`, `Math.abs()`, `Math.round()`, exponentiation with `**`, bitwise hex extraction, and positive modulo for color utilities.
- **Ch 3 — Math basics for CSS:** CSS custom properties, `calc()`, percentages, `rgb()`, `hsl()`, `lab()`, `oklch()`, and alpha syntax turn the formulas into declarative styles.
- **Ch 6 — The mathematics of responsive design:** `prefers-color-scheme` applies conditional styling through the same media-query mechanism used for responsive interfaces.
