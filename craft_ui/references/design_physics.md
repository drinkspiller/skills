# Design Engineering & Interaction Physics

This reference details the mathematical and physical laws required to make web
interfaces feel tangible, responsive, and grounded.

--------------------------------------------------------------------------------

## Concentric Border Radius Formula

When one rounded element sits inside another, their visual corners must share
the same center point. When the inner radius equals the outer radius, the corner
gap appears pinched and distorted.

### Mathematical Law

$$R_{\text{inner}} = \max\bigl(0,\, R_{\text{outer}} - \text{padding}\bigr)$$

If $R_{\text{outer}} \le \text{padding}$, the inner child must have square
corners ($R_{\text{inner}} = 0$).

### Implementation Reference

```html
<!-- Outer container: 16px radius, 8px padding. Inner child must be 16 - 8 = 8px radius -->
<div class="rounded-2xl p-2 bg-neutral-900 border border-neutral-800">
  <div class="rounded-lg bg-neutral-950 p-4">
    Inner content with perfectly concentric curvature
  </div>
</div>

<!-- Outer container: 24px radius, 12px padding. Inner child must be 24 - 12 = 12px radius -->
<div class="rounded-3xl p-3 bg-neutral-900">
  <div class="rounded-xl bg-neutral-950 p-6">
    Balanced visual curvature
  </div>
</div>
```

--------------------------------------------------------------------------------

## Optical Centroid Alignment

Bounding-box geometric centering frequently produces elements that look
off-center to the human eye. Adjust coordinates to align the shape's visual
center of mass.

### Asymmetric Glyph Compensation

*   **Play Icons in Circles:** The center of mass of an equilateral triangle
    points toward its base. Shift the SVG path $1\text{px}$ to $2\text{px}$
    toward the right point (`translate-x-[1.5px]`).
*   **Directional Arrows & Carets:** Shift $1\text{px}$ along their directional
    axis when paired with typography.
*   **Badges & Status Dots:** When paired beside capital letters, shift the
    vertical alignment upward by $0.5\text{px}$ to align with uppercase cap
    height rather than font midline.

```html
<!-- Optical centering for play button -->
<button class="relative flex h-12 w-12 items-center justify-center rounded-full bg-white text-black shadow-sm">
  <svg class="h-5 w-5 translate-x-[1.5px] fill-current" viewBox="0 0 24 24">
    <path d="M8 5v14l11-7z"/>
  </svg>
</button>
```

--------------------------------------------------------------------------------

## Tactile Push Physics

Buttons and interactive cards must feel physical. A clickable element that does
not compress on press feels dead.

### Physical Compression Rules

*   **Active Displacement:** On mouse down or screen tap, displace downward by
    $1\text{px}$ or scale down by $1.5\%$:
    *   Translation mode: `active:translate-y-[1px]`
    *   Scale mode: `active:scale-[0.985]`
*   **Instant Press Response:** Transition time going into `:active` must be
    $0\text{ms}$. Any delay makes the button feel sluggish.
*   **Elastic Release:** Transition time coming out of `:active` should be
    $120\text{ms}$ to $150\text{ms}$ with smooth easing.

```css
.btn-tactile {
  transform: translateY(0);
  transition: transform 140ms cubic-bezier(0.16, 1, 0.3, 1),
              background-color 140ms ease,
              box-shadow 140ms ease;
}

.btn-tactile:active {
  transform: translateY(1px) scale(0.99);
  transition-duration: 0ms;
}
```

--------------------------------------------------------------------------------

## Transition Scoping & Timing Brackets

Using `transition: all` is prohibited. It forces the browser to evaluate every
layout property, producing stutter on low-power devices.

### Explicit Property Targeting

Only animate non-layout composite properties:

```css
/* CORRECT */
transition: transform 160ms cubic-bezier(0.16, 1, 0.3, 1),
            opacity 160ms cubic-bezier(0.16, 1, 0.3, 1),
            background-color 160ms ease,
            border-color 160ms ease;

/* BANNED */
transition: all 0.3s ease;
```

### Motion Timing Brackets

*   **Micro-Interactions (Hovers, active taps, tooltips):** $100\text{ms} -
    160\text{ms}$.
*   **Macro State Shifts (Drawers, modals, tab switching):** $200\text{ms} -
    280\text{ms}$.
*   **Choreographed Reveals (Page transitions, stepped flows):** $300\text{ms} -
    420\text{ms}$ max.

### Preferred Easing Curves

*   Primary UI Spring: `cubic-bezier(0.16, 1, 0.3, 1)` (snappy entrance, soft
    settling).
*   Exit Curve: `cubic-bezier(0.7, 0, 0.84, 0)` (accelerating exit).

--------------------------------------------------------------------------------

## Viewport and Image Stability

### Viewport Height Discipline

Never use `h-screen` or `100vh` on top-level heroes. Dynamic mobile browser
chrome (such as the Safari address bar) expands and contracts the viewport,
causing visible layout reflows. Always use dynamic viewport units:

```css
min-height: 100dvh;
```

### Image Containment Rings

When embedding product shots, mockups, or photography on light or dark pages,
edges can blend into background surfaces. Apply a subtle $1\text{px}$ inner ring
or border:

```html
<img src="..." alt="..." class="rounded-xl ring-1 ring-black/5 dark:ring-white/10 shadow-sm" />
```

### Transition Suppression on Theme Toggle and Mount

Do not allow transitions to fire when the page hydrates or when toggling between
light and dark themes:

```javascript
// Temporarily add a class to disable transitions during theme toggles
document.documentElement.classList.add('no-transitions');
toggleTheme();
requestAnimationFrame(() => {
  document.documentElement.classList.remove('no-transitions');
});
```

```css
.no-transitions, .no-transitions * {
  transition: none !important;
}
```
