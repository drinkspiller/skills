---
name: algorithmic-art
description: >
  Create algorithmic art using p5.js with seeded randomness and interactive
  parameter exploration. Use when users request creating art using code,
  generative art, algorithmic art, flow fields, or particle systems. Produces
  original algorithmic art with interactive HTML viewers.
---

# Algorithmic Art

Create computational art expressed through p5.js generative algorithms. Output
.md files (philosophy), .html files (interactive viewer), and .js files
(generative algorithms).

This happens in two steps: 1. Algorithmic Philosophy Creation (.md file) 2.
Express by creating p5.js generative art (.html + .js files)

## Step 1: Algorithmic Philosophy Creation

Create an ALGORITHMIC PHILOSOPHY (not static images or templates) that will be
interpreted through: - Computational processes, emergent behavior, mathematical
beauty - Seeded randomness, noise fields, organic systems - Particles, flows,
fields, forces - Parametric variation and controlled chaos

### The Critical Understanding

-   What is received: Subtle input from the user as a foundation — it should not
    constrain creative freedom.
-   What is created: An algorithmic philosophy/generative aesthetic movement.
-   What happens next: Express the philosophy in code — creating p5.js sketches
    that are 90% algorithmic generation, 10% essential parameters.

### How to Generate an Algorithmic Philosophy

**Name the movement** (1-2 words): "Organic Turbulence" / "Quantum Harmonics"

**Articulate the philosophy** (4-6 paragraphs): Express how this philosophy
manifests through computational processes, noise functions, particle behaviors,
temporal evolution, and parametric variation.

**Guidelines:** - Avoid redundancy — each algorithmic aspect mentioned once -
Emphasize craftsmanship — the algorithm should appear meticulously crafted -
Leave creative space for implementation choices

## Step 2: p5.js Implementation

### Technical Requirements

**Seeded Randomness (Art Blocks Pattern):** `javascript let seed = 12345;
randomSeed(seed); noiseSeed(seed);`

**Parameter Structure:** `javascript let params = { seed: 12345, // Add
parameters that control YOUR algorithm: // Quantities, scales, probabilities,
ratios, angles, thresholds };`

### Craftsmanship Requirements

-   **Balance**: Complexity without visual noise, order without rigidity
-   **Color Harmony**: Thoughtful palettes, not random RGB values
-   **Composition**: Even in randomness, maintain visual hierarchy and flow
-   **Performance**: Smooth execution, optimized for real-time if animated
-   **Reproducibility**: Same seed ALWAYS produces identical output

### Output Format

1.  **Algorithmic Philosophy** — As markdown
2.  **Single HTML Artifact** — Self-contained interactive generative art with:
    -   p5.js from CDN
    -   The algorithm
    -   Parameter controls (sliders for numeric params)
    -   Seed navigation (prev/next/random/jump)
    -   All inline — no external files except p5.js CDN
