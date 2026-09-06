# The Slop Gate: Anti-Pattern Catalog

This reference lists the mechanical failure conditions that trigger a gate
failure. Each gate is tagged with a severity level: **HIGH** (the loudest tells
in the Reddit data, responsible for >1% of on-topic complaints), **MEDIUM**
(real but lower-signal), or **LOW** (occasionally flagged but minor). If any
HIGH or MEDIUM pattern appears in existing or generated code, rewrite it
immediately. LOW gates are advisory.

Severity rankings are grounded in a 47-subreddit, 3.2M-post Reddit analysis of
what people flag as AI slop (source: vibecoded-design-tells).

--------------------------------------------------------------------------------

## Palette and Surface Clichés

### The AI Purple / Neon Glow

**Severity: HIGH**

*   The signature gradient running from deep indigo (`#6366f1`) to electric
    violet (`#a855f7`) over a slate-900 backdrop is banned.
*   Indiscriminate radial glow blobs placed behind card grids or hero text are
    banned.
*   Instead, choose a neutral foundation (Zinc, Slate, Neutral, Stone, or
    monochromatic cool grey) paired with a singular high-contrast accent (Deep
    Emerald, Electric Cobalt, Burnt Ochre, Crimson, or Vermillion).

### The Artisanal Craft Cliché

**Severity: HIGH**

*   For consumer goods, culinary, lifestyle, hardware, or heritage products,
    language models consistently default to the exact same warm paper palette:
    *   Banned background hexes: `#f5f1ea`, `#f7f5f1`, `#fbf8f1`, `#efeae0`,
        `#ece6db`, `#faf7f1`, `#e8dfcb`.
    *   Banned brass and clay accents: `#b08947`, `#b6553a`, `#9a2436`,
        `#9c6e2a`, `#bc7c3a`, `#7d5621`.
    *   Banned espresso text: `#1a1714`, `#1a1814`, `#1b1814`.
*   When building lifestyle or premium brands, rotate through alternative
    aesthetics:
    *   Cold Luxury: Slate-950 base with chrome, smoke, and pure silver
        highlights.
    *   Forest Technical: Deep pine greens, muted bone accents, and sharp
        typography.
    *   Monochromatic Pop: Off-white canvas, stark near-black ink, and one
        unexpected electric accent.

### The New Tasteful Default (2026 Tell)

**Severity: HIGH**

*   The 2026 AI-tasteful look — warm cream/beige background + serif display
    font + sage/forest green accent — is now the single most recognizable "AI
    tried to be tasteful" signal. Reddit clocks it instantly: "the beige and
    green theme alone is a dead giveaway."
*   Banned cream/beige page backgrounds: `#faf8f5`, `#f5f1e8`, `#f3eee3`,
    `#fdfbf7`, `#f7f3ec`, `#faf6ef`, `#f6f1e7`, `#fbf7f0`, `#f4efe4`, Tailwind
    `bg-stone-50/100`, `bg-amber-50`, `bg-orange-50` as the *page* background.
*   Banned serif display fonts when paired with cream: `Instrument Serif`,
    `Fraunces`, `Playfair Display`, `Spectral`, `Cormorant`, `DM Serif`.
*   Banned sage/forest primary when paired with cream: hues around emerald/green
    700-900 (`#15573a`, `#1a4d3a`).
*   The combination of any two of these three (cream background + serif
    heading + sage accent) is the strong signal.
*   **This tell is not a banned color. It is an unspecified default.** If the
    project genuinely is a warm editorial brand and cream + serif is a real
    brand decision, leave it alone. The tell is reaching for it because it is
    what "good" auto-completes to.

### Unbounded Glassmorphism

**Severity: LOW**

*   Applying `backdrop-filter: blur()` without an opaque fallback violates
    accessibility standards.
*   Every frosted glass component must include `@media
    (prefers-reduced-transparency: reduce)` fallbacks providing a solid,
    high-contrast fill.

### Contrast Drift

**Severity: MEDIUM**

*   Low-contrast gray placeholder text and disabled-looking body text are
    prohibited.
*   All text must meet WCAG AA contrast ratios against its immediate background:
    *   Body text ($< 18\text{px}$ or non-bold): minimum 4.5:1 ratio.
    *   Large display text ($\ge 18\text{px}$ bold or $\ge 24\text{px}$
        regular): minimum 3:1 ratio.
    *   Active borders and icon controls: minimum 3:1 ratio.

--------------------------------------------------------------------------------

## Structural and Compositional Traps

### The Uniform 3-Card Grid Trap

**Severity: MEDIUM**

*   Do not stack uniform rows of 3 or 4 identical white cards with centered
    Lucide icons inside colored circular badges.
*   Introduce rhythm:
    *   Split layouts with one dominant anchor element and two secondary items.
    *   Asymmetric CSS grid areas (`grid-template-areas`).
    *   Horizontal timeline ribbons or structured data lists.

### The Viewport-Spilling Hero

**Severity: HIGH**

*   The hero section must resolve fully within the initial desktop viewport
    (`min-h-[100dvh]`).
*   Cap desktop top padding at `pt-20` to `pt-24` (maximum $6\text{rem}$).
    Excessive top padding floats hero content halfway down the screen.
*   Cap the hero text stack at four elements:
    1.  Optional eyebrow or brand ticker (zero or one).
    2.  Headline (maximum 2 lines on desktop).
    3.  Subtitle (maximum 20 words across 3 lines).
    4.  Actions (primary CTA plus at most one secondary CTA).
*   Move trust logos, pricing tags, and feature bullet lists to distinct
    sections below the fold.

### The Eyebrow Epidemic

**Severity: MEDIUM**

*   An eyebrow is a small, uppercase, wide-tracked label placed above a headline
    (`text-xs uppercase tracking-[0.2em]`).
*   Hard limitation: maximum 1 eyebrow per 3 content sections on a page. If a
    page has 9 sections, at most 3 may feature eyebrows.
*   Never place eyebrows in consecutive sections. If a section needs grouping,
    let position and headline clarity do the work.

### Zigzag Alternation

**Severity: MEDIUM**

*   Alternating [Image Left / Text Right] followed by [Text Left / Image Right]
    across multiple sections creates monotonous rhythm.
*   Maximum 2 consecutive sections may use split zigzag layouts. Break the
    rhythm with a full-width interactive moment, a data strip, or a structured
    bento.

### Bento Cell Integrity

**Severity: LOW**

*   Every bento grid must have exactly as many cells as there is real content.
    Never insert blank placeholder cards to fill grid space.
*   Multi-cell bentos require visual variety: integrate live interactive
    modules, real imagery, or distinct typography density across tiles rather
    than identical white boxes.

--------------------------------------------------------------------------------

## Typographic Anti-Patterns

### Font Monoculture and Unearned Serifs

**Severity: MEDIUM**

*   Do not reach reflexively for `Inter` or `Geist` as the default for every
    project.
*   Do not reach for `Fraunces` or `Instrument Serif` the instant a prompt hints
    at "creative" or "editorial."
*   Reserve serif typefaces strictly for briefs with genuine heritage, literary,
    or high-fashion requirements. For modern tech and design tooling, favor
    distinct grotesque display fonts.

### Mixed-Family Single-Word Inversion

**Severity: MEDIUM**

*   Highlighting a single word in a sans-serif headline by switching that single
    word to an italic serif (`and <span class="font-serif italic">spatial</span>
    design`) is amateurish AI slop.
*   Word emphasis must stay within the same type family using italic, bold, or
    underline weights.

### Italic Descender Truncation

**Severity: LOW**

*   Applying tight line-height (`leading-none` or `leading-[1]`) to display
    typography with italicized descenders (`g`, `j`, `p`, `q`, `y`) clips bottom
    letter strokes.
*   Maintain a minimum `leading-[1.1]` and add reserve padding (`pb-1`) on
    wrapping headline containers.

### Runaway Line Lengths

**Severity: LOW**

*   Body text must never span the full width of wide containers.
*   Constrain all reading paragraphs to a maximum measure of 65 characters
    (`max-w-[65ch]`).

--------------------------------------------------------------------------------

## Content and Interaction Anti-Patterns

### Div-Based Fake Screenshots

**Severity: MEDIUM**

*   Drawing mock application dashboards, fake task cards, and simulated terminal
    windows using CSS `div` shapes and rounded pills is forbidden.
*   Either render real working components, use authentic product photography, or
    use clean semantic placeholder slots.

### Unearned Engineering Precision

**Severity: MEDIUM**

*   Arbitrary invented performance numbers ("99.99% uptime", "10x throughput",
    "4.2x ROI") make products feel fake.
*   Use authentic domain data, label demo metrics clearly, or state the direct
    customer benefit in words.

### Generic Action Copy

**Severity: HIGH**

*   Action labels like "Get Started", "Submit", "Click Here", or "Learn More"
    are prohibited.
*   Write specific, task-oriented microcopy: "Deploy Edge Cluster", "Generate
    Access Token", "Inspect Schema Diff".

### Wrapped CTA Text

**Severity: LOW**

*   Primary action button text must fit on a single line on desktop viewports.
    Wrapping button labels signal uncalibrated padding or excessive copy.

### Duplicate CTA Intent

**Severity: MEDIUM**

*   Having multiple buttons on a single view that trigger the same flow with
    mismatched labels ("Get in touch", "Contact us", "Let's talk") is
    prohibited. Choose one clear action verb and maintain consistency across
    header, body, and footer.

--------------------------------------------------------------------------------

## Gradient & Color Anti-Patterns

### Gradient Text on Headings

**Severity: HIGH**

*   Applying `bg-clip-text text-transparent` with a gradient background to
    headings or hero text is one of the top-3 tells in the Reddit data.
*   Gradient-filled body text especially signals generation, because almost no
    deliberate brand applies it to real copy.
*   Default to solid color fills on all headings and text. Allow at most one
    restrained gradient as a decorative accent on a non-text surface.

### Purple-to-Blue/Pink Gradient

**Severity: HIGH**

*   The purple-to-blue (or purple-to-pink) gradient on heroes, buttons, and
    cards is a template default.
*   Banned gradient patterns: `from-purple-* to-blue-*`, `from-violet-*
    to-indigo-*`, `from-indigo-* to-pink-*`, and CSS `linear-gradient` stops
    combining `#6366f1`, `#3b82f6`, `#8b5cf6`.
*   Default to solid fills. If a gradient is needed, keep stops analogous and
    low-contrast, never the rainbow purple-to-blue.

--------------------------------------------------------------------------------

## Interaction & Icon Anti-Patterns

### Emoji-as-Icons

**Severity: MEDIUM**

*   Using emoji characters (🚀 📊 ⚡ 🎯 💡 🔥 ✨ 🛡️ 🌐 📈) as functional icons in feature
    cards, navigation, or section headers is a strong AI tell.
*   Emoji render inconsistently across platforms (Apple vs Google vs Windows),
    cannot be styled with CSS color, and signal that the developer did not
    invest in a proper icon system.
*   Use SVG icon libraries (Lucide, Heroicons, Phosphor, or Material Symbols) or
    custom SVG iconography. Reserve emoji for genuinely informal contexts (chat,
    social, playful consumer apps) where they are a deliberate brand choice.

### Rounded Everything / Pill Overuse

**Severity: MEDIUM**

*   Applying `rounded-full`, `rounded-3xl`, or `border-radius: 9999px` to every
    surface, button, and container reads as unthemed defaults.
*   Use a deliberate radius scale by component role: sharp for data-dense
    tooling, moderate for standard UI, pill only for status tags and small
    badges.
*   Maximum pill buttons: one primary CTA per view. Secondary and tertiary
    actions use the base radius.
