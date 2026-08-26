---
name: design-mock-audit
description: Evaluates coded UI implementations against Figma mocks, design specifications, or baseline screenshots. Performs a 5-point audit covering layout and spacing, typography, colors and surface tokens, assets and copy, and interactive states. Produces a design craft narrative, discrepancy scorecard with severity ratings (P0-P3), and actionable CSS/code fixes. Use when the user asks "does this match the mock", "audit against figma", "verify design parity", "compare build with mock", "check figma fidelity", or runs /design-mock-audit or /visual-qa.
---

# Design Mock Audit

`design-mock-audit` evaluates coded user interfaces against their design source
of truth (Figma files, design specifications, or baseline mock screenshots). It
measures visual fidelity and design-system alignment, delivering an executive
craft narrative, a structured discrepancy scorecard, and ready-to-apply code
remediation.

## When to Use

-   When validating an implementation before developer handoff, code review, or
    release.
-   When verifying whether a newly generated frontend component accurately
    matches its Figma mockup.
-   When auditing visual regression or drift between production UI and design
    files.
-   Triggers on: `/design-mock-audit`, `/visual-qa:audit`, `/mock-audit`, *"does
    this match the mock"*, *"audit against Figma"*, *"check design parity"*,
    *"compare build with mock"*, or whenever a user provides a Figma URL / mock
    image alongside component code or a live screenshot.

## Workflow Overview

```
 1. Input Gate & Disambiguation ───► 2. Ingest Reference & Build ───► 3. 5-Point Evaluation ───► 4. Generate Scorecard & Fixes
    (Halt if missing or ambiguous)      (Figma API, Viewport, Code)       (Layout, Type, Colors, etc.)     (Narrative, Scorecard, Diffs)
```

## Step 1: Preflight Verification & Role Disambiguation

Before taking ANY action, calling tools, or generating scorecards:

### 1.1. Preflight Missing Input Gate

If neither a reference mock (Figma URL / screenshot) nor an implementation
target (live URL / screenshot / code) is provided in the prompt or context, YOU
MUST HALT IMMEDIATELY. Prompt the user:

```text
To run the design mock audit, please provide:
1. Reference Mock: A Figma URL (with node ID) or a mock screenshot.
2. Implementation: A live URL / local port, a build screenshot, or component source file path.
```

### 1.2. Asset Classification & Role Disambiguation ($N \times M$ Matrix)

Every image asset belongs to one of three roles:

-   `ROLE_MOCK`: Design ground truth (Figma artboard export, design spec).
-   `ROLE_BUILD`: Rendered application reality (browser screenshot, device
    viewport capture).
-   `ROLE_CONTEXT`: Supporting redline spec, token palette, or reference
    diagram.

The skill supports any $N \times M$ asset combination:

-   **2 Mocks + 0 Builds** (e.g., Desktop + Mobile specs): Audits both mock
    breakpoints against local component code or live server.
-   **0 Mocks + 2 Builds** (e.g., Desktop + Mobile browser captures): Audits
    both viewports against the provided Figma link.
-   **1 Mock + 1 Build**: Direct 1-to-1 visual and token audit.
-   **N Mocks + M Builds**: Matrix comparison across corresponding viewports and
    states.

### 1.3. Ambiguity Halt & Confirmation Gate

When multiple images or screenshots are supplied without explicit role labels in
the user prompt:

1.  **Always Inspect and State Visual Chrome Findings**: Examine image
    filenames, metadata, and visual indicators. State whether the images display
    browser address bars (`localhost`, `skyebot.c.googlers.com`), DevTools
    sidebars, OS taskbars, scrollbars, or Figma canvas borders/headers.
2.  **Mandatory Halt on Ambiguity**: If roles cannot be partitioned with
    certainty, or if multiple screenshots accompany a Figma link, DO NOT GUESS
    OR ARBITRARILY ASSIGN ROLES. YOU MUST HALT AND PRESENT ALL FOUR MULTI-ROLE
    OPTIONS:

```text
Multiple screenshots detected ([Image A], [Image B]). I inspected the images for visual chrome and layout cues. Please confirm their roles before I begin the audit:
1. [Image A] is Reference Mock, [Image B] is Implementation Build.
2. [Image B] is Reference Mock, [Image A] is Implementation Build.
3. Both are Reference Mocks (e.g., Desktop & Mobile design specs) — audit against local code/live server.
4. Both are Implementation Builds (e.g., Desktop & Mobile browser renders) — audit against the Figma link.
```

## Step 2: Ingest Reference Mocks & Implementation Targets

| Source Type                             | Ingestion Method       | Extracted Context      |
| :-------------------------------------- | :--------------------- | :--------------------- |
| **Figma URL / Node ID**                 | Use `figma-context`    | Visual frame           |
:                                         : script or Figma MCP    : screenshot, node layer :
:                                         : tools                  : hierarchy, CSS         :
:                                         : (`get_design_context`, : properties (font,      :
:                                         : `get_screenshot`,      : fill, stroke, radius), :
:                                         : `use_figma`).          : and design token       :
:                                         :                        : variables              :
:                                         :                        : (`get_variable_defs`). :
| **Static Mock Screenshot**              | View image directly    | Visual layout, color   |
:                                         : via `view_file`.       : palette, typography    :
:                                         :                        : hierarchy, and asset   :
:                                         :                        : composition.           :
| **Live URL / Local Server** (e.g.,      | Use browser tooling    | Viewport screenshot,   |
: `http\://skyebot.c.googlers.com\:PORT`) : (`gbrowser`,           : computed CSS styles,   :
:                                         : screenshot capture) to : container bounding     :
:                                         : render viewport.       : boxes, and interactive :
:                                         :                        : state triggers         :
:                                         :                        : (hover/focus).         :
| **Static Build Screenshot**             | View image directly    | Rendered visual        |
:                                         : via `view_file`.       : composition and        :
:                                         :                        : styling.               :
| **Source Code & Stylesheets**           | Read component         | Token usages, style    |
:                                         : templates (HTML, TSX,  : definitions, class     :
:                                         : JSX, Angular           : names, and DOM         :
:                                         : `.ng.html`) and        : structure.             :
:                                         : CSS/SCSS/Tailwind      :                        :
:                                         : classes.               :                        :

**Mandatory Multi-Node Inspection:** When multiple sibling nodes, slides, or
variants are provided (e.g., a carousel of integration slides), you MUST fetch
and inspect ALL provided Figma node IDs. It is explicitly forbidden to sample
only a single node.

## Step 3: Execute the 5-Point Parity Audit

Evaluate fidelity across five fundamental dimensions:

### 1. Spatial Layout & Box Model

-   **Container Geometry**: Compare container max-widths, flexbox/grid
    alignments, column counts, and aspect ratios.
-   **Spacing Rhythm**: Audit padding, margins, and gaps against the design
    system spacing scale (4px/8px grid). Flag arbitrary margin overrides.
-   **Alignment & Optical Weight**: Check baseline alignment, vertical
    centering, and edge flushness across related elements.

### 2. Typography Scale & Hierarchy

-   **Type Properties**: Compare font family, font weight (e.g., 400 vs 600),
    font size (px/rem), line height (`line-height`), and letter spacing
    (`letter-spacing`).
-   **Visual Hierarchy**: Verify that heading levels (H1-H4), body text, and
    captions maintain distinct contrast and size ratios matching the mock.
-   **Text Alignment & Wrapping**: Check text alignment (left, center, right),
    maximum line lengths, and multiline wrapping behavior.

### 3. Color & Surface Tokens

-   **Fills & Backgrounds**: Compare background colors against the palette or
    semantic tokens (e.g., primary surface, container high/low).
-   **Atmospheric Backdrop Washes & Nested Gradient Layers**: Deeply inspect
    nested gradient backplates, radial/linear gradient washes, and ambient
    washes behind floating mockup elements (rather than evaluating only the
    outermost container's background color).
-   **Contextual Chromatic Pairing**: Verify whether accent elements (e.g.,
    integration badges, category tags, icons, brand marks) chromatically drive
    or pair with ambient surface backdrops, gradient washes, tinted container
    glows, or colored drop shadows behind adjacent cards.
-   **Cross-Variant & Dynamic Theming**: When auditing collections, carousels,
    lists, or multi-tab components, check whether each variant/item introduces
    its own distinct theme, accent color, gradient, or lighting scheme.
-   **Borders & Strokes**: Verify border color, width, and style.
-   **Corner Radii**: Compare border-radius values (e.g., 8px vs 12px vs full
    pill).
-   **Elevation & Shadows**: Check `box-shadow` offset, blur radius, spread,
    color opacity, and elevation layers.
-   **Opacity & Blend Modes**: Verify backdrop filters, translucent overlays,
    and state opacities.

### 4. Asset & Content Parity

-   **Icons**: Verify icon glyph choice, dimensions (e.g., 20px vs 24px), stroke
    width, and alignment with adjacent text.
-   **Imagery**: Check aspect ratios, object-fit mode (`cover` vs `contain`),
    clipping masks, and placeholder rendering.
-   **Copy & Microcopy**: Verify exact copy strings, punctuation, capitalization
    (Title Case vs Sentence case), and truncation rules (`text-overflow:
    ellipsis`).

### 5. Interactive States & Responsiveness

-   **Component States**: If interactive access is available, verify default,
    hover, active, focus (visible focus rings), disabled, loading (skeletons),
    and empty states.
-   **Responsive Reflow**: When auditing multi-breakpoint specs (e.g., Desktop
    1440px and Mobile 390px), evaluate reflow behavior and partition the
    scorecard by breakpoint.

## Step 4: Classify Severity

Rate every identified discrepancy:

| Severity          | Impact           | Criteria                              |
| :---------------- | :--------------- | :------------------------------------ |
| **Critical (P0)** | Breaking         | Layout broken, primary action missing |
:                   :                  : or obscured, severe contrast failure  :
:                   :                  : (<3\:1 for text), wrong primary brand :
:                   :                  : color. Blocks release.                :
| **Major (P1)**    | Degraded         | Noticeable spacing deviation (>8px),  |
:                   :                  : wrong font weight/family, missing     :
:                   :                  : secondary state or element, incorrect :
:                   :                  : border radius or elevation, missing   :
:                   :                  : ambient gradient washes, or omission  :
:                   :                  : of per-item dynamic chromatic         :
:                   :                  : theming.                              :
| **Minor (P2)**    | Noticeable Delta | Subtle spacing mismatch (2-4px),      |
:                   :                  : slight color tone divergence, optical :
:                   :                  : alignment shift, minor microcopy      :
:                   :                  : discrepancy.                          :
| **Polish (P3)**   | Sub-pixel Craft  | Micro-spacing tweak, transition curve |
:                   :                  : adjustment, subpixel line-height      :
:                   :                  : refinement.                           :

## Step 5: Deliver the Report

Format the audit output into three distinct sections:

````markdown
# Design Mock Audit: [Component / Screen Name]

**Mock Source:** [Figma Node URL or Mock Screenshot Path]
**Build Source:** [Live URL, Component File, or Implementation Screenshot]
**Overall Parity Rating:** [Pass / Polish / Revise / Fail] — [e.g. 88% Match]

---

## Executive Craft Assessment
[2-3 concise paragraphs providing a qualitative design critique. Evaluate visual rhythm, optical balance, hierarchy, and aesthetic resonance. Identify where the implementation succeeds and where it loses the feeling of the mock.]

---

## Discrepancy Scorecard

*(Note: When auditing multi-breakpoint designs, partition this section into dedicated subsections, e.g. `### Desktop Parity (1440px)` and `### Mobile Responsive Parity (390px)`).*
*(Note: When dynamic chromatic theming is omitted across variants, you MUST provide a per-variant token mapping table in the scorecard and actionable CSS remediation).*

### 1. Spatial Layout & Box Model
| Element | Mock Expectation | Implementation State | Severity | Recommended Fix |
| :--- | :--- | :--- | :--- | :--- |
| Card Container | `padding: 24px` | `padding: 16px` | Major (P1) | Change padding to `24px` (`p-6`) |
| Action Button Gap | `gap: 12px` | `gap: 8px` | Minor (P2) | Update flex gap to `12px` (`gap-3`) |

### 2. Typography & Hierarchy
| Element | Mock Expectation | Implementation State | Severity | Recommended Fix |
| :--- | :--- | :--- | :--- | :--- |
| Title Font Weight | `Google Sans, 600 (SemiBold)` | `Google Sans, 400 (Regular)` | Major (P1) | Set `font-weight: 600` |
| Caption Line Height| `line-height: 20px` | `line-height: 16px` | Minor (P2) | Increase `line-height` to `1.25rem` |

### 3. Color & Surface Tokens
| Element | Mock Expectation | Implementation State | Severity | Recommended Fix |
| :--- | :--- | :--- | :--- | :--- |
| Card Background | `var(--md-sys-color-surface-container-low)` (`#F7F9FC`) | `#FFFFFF` | Major (P1) | Apply surface container token |
| Container Radius | `border-radius: 16px` | `border-radius: 8px` | Major (P1) | Set `rounded-2xl` / `16px` radius |
| Dynamic Theming | Per-variant accent glows | Hardcoded blue theme | Major (P1) | Implement per-variant token mapping (see below) |

*(Example Per-Variant Token Mapping Table for Dynamic Theming)*
| Variant / Item | Accent Color Token | Ambient Glow / Wash Token |
| :--- | :--- | :--- |
| Gmail Slide | `var(--theme-red-accent)` | `var(--theme-red-glow)` |
| Calendar Slide | `var(--theme-blue-accent)` | `var(--theme-blue-glow)` |

### 4. Asset & Content Parity
| Element | Mock Expectation | Implementation State | Severity | Recommended Fix |
| :--- | :--- | :--- | :--- | :--- |
| Close Icon | 24x24px, centered optical padding | 18x18px, off-center | Minor (P2) | Increase size to 24px, add `align-items: center` |

### 5. Interactive States & Responsiveness
| Element | Mock Expectation | Implementation State | Severity | Recommended Fix |
| :--- | :--- | :--- | :--- | :--- |
| Focus Ring | Visible 2px outline with 2px offset | None | Major (P1) | Add `:focus-visible` outline styles |

---

## Actionable Remediation Diffs

```css
/* Example targeted fix snippet */
.target-card {
- padding: 16px;
- border-radius: 8px;
+ padding: 24px;
+ border-radius: 16px;
+ background-color: var(--md-sys-color-surface-container-low);
}
```

---

## Next Steps
- Apply the above patches directly to the codebase if source files are present.
````

## Remediation Protocol

After delivering the scorecard:

1.  If local component source code is present in the workspace, offer to apply
    the Critical (P0) and Major (P1) fixes surgically.
2.  If the user approves, apply the code modifications using
    `replace_file_content`.
3.  Re-verify the updated build to ensure visual convergence.
