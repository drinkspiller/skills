---
name: assembly-guide
description: >-
  Authors, lints, renders, and critiques mistake-proof step-by-step assembly,
  disassembly, maintenance, and teardown guides for any hardware, 3D-printed CAD
  model, electronics build, lab setup, or operational workflow. Enforces
  color-matched bullet-to-visual callouts, neutral base visuals, pre-action
  hazard warnings, exact fastener and torque specs, tool and parts staging, and
  closed-loop verification, then delivers an interactive HTML guide and a print
  PDF checked by automated render audits and one visual review. Use when asked to
  create an assembly guide, build instructions, repair or teardown manual, or
  step-by-step maintenance procedure.
---

# Step-by-Step Assembly Guides (`assembly-guide`)

Produces assembly, maintenance, replacement, and teardown guides for whatever
context the user supplies. Every build ships two deliverables from one source:
an **interactive HTML guide** for on-screen use and a **print PDF** for the
bench.

## Bundled Toolkit & References

<!-- mdformat off(prevent table wrapping) -->

| Resource | Purpose |
| :--- | :--- |
| [references/instructional_grammar.md](references/instructional_grammar.md) | Layouts (`manual` vs. `workbench`), contrast-first colors, neutral visuals, marker shapes, camera zoom & projection, callout icons, pacing, and builder register |
| [references/schema_and_visual_authoring.md](references/schema_and_visual_authoring.md) | `guide.json` schema, `0-100` camera-projected marker coordinates, visual sources, and Markdown rules |
| `scripts/render_guide.py` | Zero-dependency CLI: `lint`, `build` (HTML, PDF, Markdown), `audit`, `recolor`, `init-sample` |

<!-- mdformat on -->

## 1. Five Communication Laws

Read [references/instructional_grammar.md](references/instructional_grammar.md)
before drafting the first guide in a session. Every guide obeys five laws:

1.  **Dual redundancy**: A builder can complete each step from the 1-3 visuals
    alone *or* from the bullets alone.
2.  **Color-matched spatial binding**: Each spatial bullet gets a color in
    contrast-first order (`red` → `blue` → `green` → `orange` → `magenta` →
    `cyan` → `yellow`; `black` for non-spatial bullets) and a matching marker
    (`circle`, `rect`, `arrow`, `arc`, or `loupe`) on the visual. At most 3
    marker colors per visual, and no near-neighbor pairs (red/orange, blue/cyan)
    in small steps. Base visuals stay neutral so only markers carry color.
3.  **One step, one physical objective**: 1-3 visuals and ≤ 7 bullets for one
    coherent transition. Never mix unrelated subsystems.
4.  **Hazards before actions**: `⚠` warnings sit strictly before the action
    where the mistake can happen.
5.  **Observable datums**: Replace "securely" and "properly" with fastener sizes
    and counts, torque, angles, visual pass/fail checks, and expected feel. Keep
    designer data (CAD identifiers, `X/Y/Z` heights) out of builder copy.

Guide copy describes the product being built. It never references other
publishers' guide styles or calls itself "print-ready".

## 2. Context Intake & Procedure Type

Adapt to whatever input the user provides without inventing dimensions:

*   **CAD project or BOM**: Extract part names, fastener schedule, insert and
    nut-trap locations, cable channels, and mating axes. Map model IDs to human
    names with `display_names`. Always use **3D renders of the actual part
    geometry** (`"src"`) for printed/COTS parts staging and assembly steps—never
    represent 3D parts with generic 2D SVG circles/rectangles or placeholder
    boxes. For multi-part sub-assemblies (e.g., servo horn + hub plate + pulley
    stack, bearing + spindle + belt coupling, or multi-tier PCB stacks), provide
    **paired 3D renders**: an **Exploded Stack view** (coaxial alignment line +
    numbered `1..N` stack order naming hidden underside pockets, deferred screw
    holes, and hex key sizes) and an **Assembled In-Context (ghosted/X-ray)
    view** (obstructing outer housings rendered semi-transparent so internal
    belt or gear engagement is visible).
*   **Photos, video frames, or draft notes**: Sequence frames from a consistent
    builder viewpoint and group them into 1-up, 2-up, or 3-up steps.
*   **Lab rig, rack setup, or software workflow**: Decompose into atomic state
    changes and use `"tool_lineup"`, `"ui_screen"`, and `"svg"` visuals.

Choose the procedure type (`archetype`):

*   **`assembly`**: First-time build. Stage tools and fasteners up front, build
    subassemblies in collision-free order, add milestone notes on long builds,
    and end with calibration or a self-test.
*   **`roundtrip`** (default for repairs): Disassembly → parts preparation →
    explicit assembly → functional check and tool stowage. Required whenever
    reassembly adds torque limits, routing exclusions, single-use consumables,
    seal or datum checks, or calibration.
*   **`teardown`**: Symmetric disassembly that closes with a reverse-order
    reassembly note. Only valid when reassembly is a true mirror.

Choose the default layout (`default_dialect`):

*   **`manual` (Manual layout)**: Displays all step visuals simultaneously in a
    side-by-side grid (`1-up` beside bullets; `2-up` or `3-up` above bullets),
    uses solid colored **hexagon** bullet glyphs, an orange accent bar, and
    shows the **Table of Contents** card at the top—ideal for reading paired
    *Exploded* + *Assembled* sub-assembly views side by side or printing.
*   **`workbench` (Workbench layout)**: Displays a single large `4:3` active
    stage (`55%` width) beside the bullets with clickable **thumbnail switcher
    buttons** underneath (hovering or clicking a colored bullet automatically
    switches the stage to the frame carrying that marker color), uses hollow
    colored **ring** bullet glyphs, a blue accent bar, and hides the Table of
    Contents so Step 1 starts higher on screen.

The interactive HTML guide includes a live header toggle between both layouts.

## 3. Standard Guide Arc

1.  **Introduction and variant note**: Exact scope; point sibling hardware
    revisions elsewhere up front.
2.  **Tools step**: Exact sizes in a neutral lineup with black bullets; box at
    most one easily confused item. Include workholding and surface protection.
3.  **State preparation and isolation**: Powered positioning and hot operations
    first, then cooldown, power off and unplug, and shielding.
4.  **Atomic disassembly steps**: Loosen vs. remove, ring counts that match
    fastener counts, latch warnings before connectors.
5.  **Parts preparation**: Stage new parts and consumables with quantities,
    showing **3D renders of every printed/COTS part** (never flat 2D circles or
    generic boxes), separating **machine screws/nuts/washers** from **brass
    heat-set inserts**, listing required **power supplies and data cables**,
    calling out **exact COTS SKUs + incompatible lookalike warnings**, marking
    **optional vs. required components** with exact search queries and package
    dimensions, and disambiguating **unused kit parts** (e.g., driven `25T`
    splined servo horn vs. unused smooth-bore idler disc) or **COTS vs.
    printable options** (e.g., fiberglass `GT2` belt vs. `TPU 95A` printed belt,
    or why a printed hub plate + pulley stack is used instead of a smooth-bore
    aluminum stepper pulley).
6.  **Assembly, counter-torque, and datum checks**: Counter-hold before torque,
    state rotation direction, indent `ⓘ` torque checks, pair **Exploded Stack +
    Assembled In-Context (ghosted)** 3D renders on multi-part sub-assemblies,
    distinguish **integral printed floor posts** from **discrete hardware
    standoffs**, and never invent port labels (`"Port 1"`) when a COTS board has
    unmarked parallel headers.
7.  **Closed-loop verification and stowage**: Observable functional test, stow
    jigs and shields, short completion note.

## 4. Workflow: Author → Build → Verify Once → Deliver

Read
[references/schema_and_visual_authoring.md](references/schema_and_visual_authoring.md)
for the `guide.json` schema and marker coordinates.

```bash
# Resolve SKILL_DIR to the directory containing this SKILL.md
SKILL_DIR="<path-to-assembly-guide-skill>"
RG="python3 $SKILL_DIR/scripts/render_guide.py"
```

1.  **Author `guide.json`** next to the user's project or in a scratch output
    directory (keep generated preview artifacts out of version-controlled source
    trees unless requested). When rendering 3D CAD views:
    *   Render every step visual at an exact **`4:3` aspect ratio** (`800 × 600`
        or `1200 × 900`) and compute `0-100` marker coordinates directly from
        the 3D camera projection (`WorldToDisplay()` / `project()`) so rings
        land dead-center on holes and bosses.
    *   Choose camera angles (`-70°` to `-90°` for underside pockets) that never
        occlude a boss behind a skirt wall, and **zoom tightly** onto small
        active sub-boards (`50–75%` frame occupancy) instead of showing a tiny
        board inside a full-enclosure overview.
    *   For tightly clustered fasteners in perspective or exploded stacks, use a
        single `arrow` or `rect` marker instead of overlapping `circle` rings
        (`G-MARKER-OVERLAP`), and keep boxes/arrows clear of text labels.
    *   **No Gouraud / Averaged-Normal Shading on CAD Renders**: Never render
        STL/CAD triangulations with `smooth_shading=True` or unsplit vertex
        normals (`compute_normals()` defaults to `split_vertices=False` in
        PyVista/VTK, averaging 90° hole-rim normals with flat face normals and
        creating radial Gouraud sunburst streaks across flat surfaces). Always
        tessellate finely (`tolerance <= 0.015`, `angular_tolerance <= 0.08`),
        weld (`clean(tolerance=1e-4, absolute=True)`), split creases
        (`compute_normals(cell_normals=True, point_normals=True,
        split_vertices=True, feature_angle=25.0, auto_orient_normals=False,
        consistent_normals=False)`), render with `smooth_shading=False` and
        `show_edges=False`, and overlay true `extract_feature_edges(feature_angle=25.0)`.
2.  **Lint until clean**: `$RG recolor guide.json` (contrast-first colors), then
    `$RG lint guide.json --strict`.
3.  **Build both deliverables with the rendered audit**:

    ```bash
    $RG build guide.json --html out/guide.html --pdf out/guide.pdf \
      --markdown out/guide.md --audit --strict
    ```

    `--audit` renders the guide in headless Chrome and checks text that touches
    or crosses frame edges, lineup labels wider than their slots, > 3 marker
    colors per visual, overlapping circle markers (`G-MARKER-OVERLAP`), accent
    stripes on rounded boxes, misaligned table columns, and PDF pagination
    (orphaned milestones, stranded step headers). Images are embedded by default
    so the HTML is portable. When `--pdf` is set, the HTML header gets a
    **Download PDF** button that links to the PDF by relative path, so publish
    both files in the same directory (or set `"pdf_url"` in `guide.json`). Fix
    every lint and audit finding before the visual check.

4.  **Do one visual check, then at most one fix cycle.** The lint and audit
    gates already catch layout, color, copy, and pagination defects, so the
    visual check covers only what automation cannot judge. Render the PDF
    (`pdftoppm -png -r 70 out/guide.pdf out/pg`) and look at every page for:

    *   **Marker placement & zoom**: Each marker sits dead-center on the exact
        feature its bullet names (the right screw, boss, row, or connector),
        circles do not overlap (`G-MARKER-OVERLAP`), boxes do not cross over
        diagram text labels, and small sub-boards are zoomed large enough to
        inspect clearly.
    *   **Diagram sense**: Schematic labels use builder names, and each visual
        shows something the bullets need (drop decorative or redundant visuals
        rather than annotating them).
    *   **Copy sense**: Bullets still read naturally after display-name
        substitution and coordinate removal (no dangling "at" or empty
        parentheses, no repeated articles like "three the bearing deck").
    *   **Legibility**: Rings and labels are readable at page size.

    Fix everything found in a single edit pass, rebuild with `--audit --strict`,
    and confirm the fixed pages. If a problem survives that one fix cycle,
    report it to the user with the page image instead of looping.

5.  **Deliver both files together.** Publish the HTML and PDF side by side in
    the output or static web directory and link both: the HTML for on-screen
    use, the PDF for the bench.

## 5. Quality Checklist

*   [ ] `lint --strict` and `build --audit --strict` both pass with 0 warnings.
*   [ ] Every 3D-printed or COTS mechanical part is shown with a **3D render of
    its actual geometry** (`"src"`), never generic 2D SVG circles/boxes or
    unknown `tool_lineup` placeholder shapes (`G-GENERIC-PART-SVG`,
    `G-PLACEHOLDER-SHAPE`).
*   [ ] Multi-part sub-assemblies include both an **Exploded Stack 3D render**
    (coaxial alignment line + numbered `1..N` stack order) and an **Assembled
    In-Context (ghosted) 3D render** (`G-SUBASSEMBLY-SINGLE-IMAGE`).
*   [ ] Step visuals are rendered at `4:3` with camera-projected (`0-100`)
    marker coordinates, unobstructed hole visibility, close-up zoom framing for
    small sub-boards (`50–75%` of frame), and zero overlapping circle markers or
    label collisions (`G-MARKER-OVERLAP`).
*   [ ] BOM and step copy separate heat-set inserts from machine screws, include
    power supplies/cables and exact COTS SKUs + lookalike warnings, mark
    optional parts with search queries, distinguish integral printed bosses from
    discrete standoffs, and explain unmarked parallel headers.
*   [ ] Every spatial bullet color appears on a marker in the same step, in
    contrast-first order, with ≤ 3 colors per visual.
*   [ ] Staging steps use black bullets and at most one neutral box.
*   [ ] Every `⚠` sits above the action it guards.
*   [ ] Fastener counts in bullets match ring counts on the visuals.
*   [ ] No CAD identifiers, coordinates, marker color names, or meta copy in
    builder-facing text or diagram labels.
*   [ ] `teardown` is never used when torque values, consumables, or calibration
    exist.
*   [ ] One visual check passed (marker placement, diagram and copy sense,
    legibility), and both the HTML and PDF were delivered.
