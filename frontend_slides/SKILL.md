---
name: frontend-slides
description: >
  Create stunning, animation-rich HTML presentations from scratch or by
  converting PowerPoint files. Use when the user wants to build a presentation,
  convert a PPT/PPTX to web, or create slides for a talk/pitch. Creates
  zero-dependency, self-contained HTML slide decks.
---

# Frontend Slides

Create zero-dependency, animation-rich HTML presentations that run entirely in
the browser.

## Core Principles

1.  **Zero Dependencies** — Single HTML files with inline CSS/JS. No npm, no
    build tools.
2.  **Show, Don't Tell** — Generate visual previews, not abstract choices.
    People discover what they want by seeing it.
3.  **Distinctive Design** — No generic "AI slop." Every presentation must feel
    custom-crafted.
4.  **Viewport Fitting (NON-NEGOTIABLE)** — Every slide MUST fit exactly within
    100vh. No scrolling within slides. Content overflows? Split into multiple
    slides.

## Design Aesthetics

Focus on: - **Typography**: Beautiful, unique fonts. Avoid generic fonts like
Arial and Inter. - **Color & Theme**: Cohesive aesthetic with CSS variables.
Dominant colors with sharp accents. - **Motion**: CSS animations for effects and
micro-interactions. Focus on high-impact moments. - **Backgrounds**: Atmosphere
and depth — not solid colors. Layer CSS gradients, geometric patterns.

Avoid generic AI-generated aesthetics: overused fonts, cliched color schemes,
predictable layouts.

## Viewport Fitting Rules

-   Every `.slide`: `height: 100vh; height: 100dvh; overflow: hidden;`
-   ALL font sizes: use `clamp(min, preferred, max)` — never fixed px/rem
-   Content containers need `max-height` constraints
-   Images: `max-height: min(50vh, 400px)`
-   Include `prefers-reduced-motion` support

### Content Density Limits Per Slide

Slide Type    | Maximum Content
------------- | ---------------------------------------------------
Title slide   | 1 heading + 1 subtitle + optional tagline
Content slide | 1 heading + 4-6 bullets OR 1 heading + 2 paragraphs
Feature grid  | 1 heading + 6 cards max (2x3 or 3x2)
Code slide    | 1 heading + 8-10 lines of code
Quote slide   | 1 quote (max 3 lines) + attribution
Image slide   | 1 heading + 1 image (max 60vh height)

**Content exceeds limits? Split into multiple slides. Never cram, never
scroll.**

## Workflow

### Phase 1: Content Discovery

Ask the user about purpose, length, content readiness, and editing preferences.
If they have content, ask them to share it.

### Phase 2: Style Discovery

Generate 3 distinct single-slide HTML previews showing typography, colors,
animation, and overall aesthetic. Let the user pick their preferred style.

Mood-to-style mapping: - Impressed/Confident → Bold, professional, trustworthy -
Excited/Energized → Innovative, bold, creative - Calm/Focused → Clear,
thoughtful, minimal - Inspired/Moved → Emotional, memorable

### Phase 3: Generate Presentation

Generate the full presentation as a single self-contained HTML file: - All
CSS/JS inline - Use fonts from Google Fonts — never system fonts - Detailed
comments explaining each section - Every section with clear comment block
headers

### Phase 4: PPT Conversion (if applicable)

When converting PowerPoint files: 1. Extract content (text, images, slide order)
2. Confirm with user 3. Style selection (Phase 2) 4. Generate HTML preserving
all content

### Phase 5: Delivery

Open the presentation in browser. Summarize: file location, style name, slide
count, navigation (arrow keys, space, scroll/swipe, click nav dots).
