# Chapter 6: Graphics and Multimedia

## Core Idea
Modern HTML handles rich media natively through declarative elements (`<img>`, `<picture>`, `<svg>`, `<canvas>`, `<video>`, `<audio>`), eliminating reliance on legacy third-party browser plug-ins. Responsive art direction and performance optimization depend on matching image dimensions and modern formats (WebP, AVIF) to device capabilities via `<picture>` and `srcset`.

## Frameworks Introduced
- **Responsive Art Direction Framework (`<picture>` vs. `srcset`)**:
  - When to use: Serving optimized images across diverse viewports, pixel densities, and browser format capabilities.
  - How:
    - Use `<img>` with `srcset` and `sizes` for resolution switching (same image cropped identically, served at different pixel resolutions: `1x`, `2x`, or width descriptors `400w`, `800w`, `1200w`).
    - Use `<picture>` with nested `<source media="...">` for art direction (swapping to a tightly cropped square on mobile vs. a wide panorama on desktop).
    - Use `<source type="image/webp">` inside `<picture>` for format negotiation, placing cutting-edge formats first and standard JPEG/PNG in the fallback `<img>`.
- **Cumulative Layout Shift (CLS) Prevention Protocol**:
  - When to use: Embedding any visual media (`<img>`, `<video>`, `<iframe>`).
  - How: Always specify explicit `width` and `height` attributes on the HTML element (e.g., `width="800" height="450"`). Modern browser rendering engines compute an intrinsic aspect-ratio from these attributes before the image binary downloads, reserving the exact layout space and eliminating layout jumping during page load.
- **Native Video & Audio Delivery Pipeline**:
  - When to use: Delivering media without third-party embeds (YouTube, Vimeo).
  - How: Enclose multiple `<source>` elements inside `<video>` or `<audio>` sorted by codec efficiency (MP4/H.264, WebM/VP9). Provide fallback text for legacy clients. Attach closed captions and subtitles using `<track kind="subtitles" srclang="en" src="captions.vtt">` in WebVTT format for accessibility.

## Key Concepts
- **`<img>`**: Void element embedding raster graphics; mandatory `src` and `alt` attributes.
- **`alt` (Alternative Text)**: Textual description read aloud by screen readers and displayed when image assets fail to load; essential for accessibility and web crawlers.
- **`<picture>`**: Wrapper container enabling declarative art direction and format negotiation across nested `<source>` tags.
- **`<source>`**: Void element specifying alternate media sources, MIME types, and media queries inside `<picture>`, `<video>`, or `<audio>`.
- **`srcset`**: Attribute containing a comma-separated list of image URLs paired with width (`w`) or pixel density (`x`) descriptors.
- **`<svg>` (Scalable Vector Graphics)**: XML-based resolution-independent vector graphics format capable of inline DOM manipulation and CSS styling.
- **`<canvas>`**: Scriptable bitmap graphics container manipulated procedurally via JavaScript 2D or WebGL rendering contexts.
- **`<video>` / `<audio>`**: Native media players supporting playback controls, looping, autoplay policies, and track synchronization.
- **`<iframe>`**: Inline frame embedding an isolated HTML browsing context from an internal or external source.

## Mental Models
- **Think of `<picture>` as a Content Negotiation Engine**: The browser evaluates `<source>` tags from top to bottom. The first `<source>` whose media query matches and whose format is supported by the engine wins; all other image downloads are bypassed entirely, saving mobile bandwidth.
- **Think of SVG as Text-Based Architecture and Canvas as an Etch-a-Sketch**: SVG creates explicit mathematical DOM nodes (circles, paths, rectangles) that remain crisp at infinite zoom and can be inspected in DevTools. Canvas is a blank pixel grid where JavaScript paints colors that cannot be inspected as individual elements once drawn.

## Anti-patterns
- **Missing or Decorative `alt` Text**: Leaving off `alt` entirely (fails W3C validation) or writing `alt="image"` / `alt="photo.jpg"`. For purely decorative spacers, use `alt=""` so screen readers ignore them; for informational images, provide a concise 12–16 word description of the visual information.
- **Omitting `width` and `height` Attributes**: Leaving visual media dimensions entirely to CSS. Forces the browser to calculate dimensions only after image headers download, causing jarring page content shifts (Cumulative Layout Shift) that hurt Core Web Vitals.
- **Using Raster Images for Simple Icons/Logos**: Using JPEG or PNG for line logos and ui icons. Causes pixelation on high-DPI (Retina) screens and inflates payload sizes compared to optimized SVG vectors.
- **Unmuted Autoplay Videos**: Setting `<video autoplay>` without `muted`. Modern browsers block unmuted autoplay by default to protect users from sudden loud audio. Autoplaying background video must include `<video autoplay muted loop playsinline>`.

## Code Examples
```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Multimedia and Responsive Graphics</title>
  </head>
  <body>
    <!-- Responsive image with format negotiation and art direction -->
    <figure>
      <picture>
        <!-- Modern WebP format for wide desktop viewports -->
        <source media="(min-width: 1024px)" srcset="images/hero-desktop.webp" type="image/webp">
        <source media="(min-width: 1024px)" srcset="images/hero-desktop.jpg">
        
        <!-- Cropped portrait view for mobile screens -->
        <source media="(min-width: 480px)" srcset="images/hero-mobile.webp" type="image/webp">
        <source media="(min-width: 480px)" srcset="images/hero-mobile.jpg">
        
        <!-- Standard fallback with explicit dimensions to prevent CLS -->
        <img src="images/hero-mobile.jpg" alt="Aerial view of Tokyo skyline illuminated at dusk" width="800" height="600" loading="lazy">
      </picture>
      <figcaption>Figure 1: Tokyo urban center viewed from Roppongi Hills.</figcaption>
    </figure>

    <!-- Accessible native video player with subtitle tracks -->
    <section>
      <h2>Keynote Address</h2>
      <video controls width="640" height="360" poster="media/poster.jpg" preload="metadata">
        <source src="media/keynote.webm" type="video/webm">
        <source src="media/keynote.mp4" type="video/mp4">
        <track kind="subtitles" src="media/subtitles-en.vtt" srclang="en" label="English Subtitles" default>
        <p>Your browser does not support HTML5 video. <a href="media/keynote.mp4">Download the video file (MP4)</a>.</p>
      </video>
    </section>
  </body>
</html>
```
- **What it demonstrates**: `<picture>` container managing WebP/JPEG format negotiation and mobile-first art direction; layout shift prevention with explicit dimensions; accessible `<video>` player with fallback links and WebVTT subtitle track.

## Reference Tables

### Core Multimedia Elements
| Element | Primary Attributes | Content Model | Use Case |
|---|---|---|---|
| `<img>` | `src`, `alt`, `width`, `height`, `loading="lazy"` | Void (no children) | Single raster/vector photo, illustration, diagram |
| `<picture>` | None (container) | Zero or more `<source>`, exactly one `<img>` | Multi-source responsive images, format negotiation |
| `<svg>` | `viewBox`, `xmlns`, `width`, `height` | Vector nodes (`<path>`, `<rect>`, `<circle>`) | Logos, scalable icons, charts, interactive diagrams |
| `<canvas>` | `width`, `height` | Transparent pixel surface | Dynamic JavaScript charts, particle effects, games |
| `<video>` | `controls`, `poster`, `preload`, `autoplay`, `muted` | `<source>`, `<track>`, fallback text | Local video playback without third-party plugins |
| `<audio>` | `controls`, `preload`, `autoplay`, `loop` | `<source>`, fallback text | Speech podcasts, audio clips, background music |
| `<iframe>` | `src`, `width`, `height`, `loading`, `sandbox` | Fallback text | Embedding third-party maps, YouTube, widgets |

### Image Format Selection Guide
| Format | Compression Type | Transparency? | Animation? | Ideal Use Case |
|---|---|---|---|---|
| **AVIF** | Next-Gen Lossy/Lossless | Yes | Yes | Maximum compression efficiency for web photos |
| **WebP** | Modern Lossy/Lossless | Yes | Yes | Universal modern alternative to JPEG and PNG |
| **JPEG** | Legacy Lossy | No | No | Universal fallback for complex photographic imagery |
| **PNG** | Lossless | Yes (8-bit alpha) | No | Screenshots, diagrams with sharp text, legacy transparency |
| **SVG** | Vector XML | Yes | Yes (CSS/JS) | Logos, icons, geometric UI graphics, typography |

## Worked Example
An e-commerce company serves 2MB uncompressed PNG product photos on product detail pages. Mobile users suffer high data costs and mobile Lighthouse performance scores are in the red.
1. **Format & Resolution Strategy**:
   - Convert master photos into modern WebP format and legacy JPEG fallbacks.
   - Generate two breakpoints: 400px wide for mobile and 1000px wide for desktop.
2. **Implementation**:
   - Construct a `<picture>` element with MIME type checks and explicit aspect ratio dimensions (`width="1000" height="1000"`).
   - Add `loading="lazy"` to defer off-screen thumbnail downloads.
3. **Refactored Code**:
```html
<picture>
  <source type="image/webp" media="(min-width: 768px)" srcset="products/watch-1000.webp">
  <source type="image/jpeg" media="(min-width: 768px)" srcset="products/watch-1000.jpg">
  <source type="image/webp" srcset="products/watch-400.webp">
  <img src="products/watch-400.jpg" alt="Chronograph wristwatch with brown leather strap and silver dial" width="1000" height="1000" loading="lazy">
</picture>
```
4. **Outcome**: Mobile payload drops from 2MB to 45KB; zero layout shift on slow cellular connections.

## Key Takeaways
1. Every informational `<img>` must possess a concise, descriptive `alt` attribute; decorative images use `alt=""`.
2. Always supply explicit `width` and `height` dimensions on images and videos to prevent Cumulative Layout Shift.
3. Use `<picture>` with `type="image/webp"` to deliver modern compressed formats while retaining full backwards compatibility.
4. SVGs provide infinite scalability and tiny file sizes for logos, icons, and UI glyphs.
5. HTML5 `<video>` and `<audio>` deliver media natively, requiring `<source>` tags for cross-browser codec support and `<track>` for subtitles.

## Connects To
- **Ch 04**: Encloses media within semantic figures (`<figure>` and `<figcaption>`).
- **Ch 13**: Explores CSS responsive image styling (`max-width: 100%`) and media query breakpoints.
- **Ch 14**: Demonstrates CSS visual effects on images (`transform`, `border-radius`, `box-shadow`).
