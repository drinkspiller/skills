# Instructional Grammar for Step-by-Step Guides

This reference documents the cognitive, structural, typographic, and visual
conventions the `assembly-guide` skill applies to every assembly, maintenance,
replacement, and teardown guide.

## 1. Cognitive Foundations

Step-by-step guides fail in three predictable ways. Every rule below exists to
prevent one of them:

1.  **Coordinate translation overhead**: Prose like *"remove the second screw
    from the lower-left corner behind the black bracket"* forces the builder to
    rotate axes in their head while holding a tool. Color-matched markers bind
    each bullet to an annotation on the visual, so finding the target takes no
    search.
2.  **Action-after-hazard traps**: Builders execute bullets top to bottom. A
    caution placed after the action (*"Disconnect the cable. Be sure to press
    the latch first!"*) breaks connectors. Hazard and equipment-damage callouts
    (`⚠`) always precede the action bullet they guard.
3.  **Ambiguous completion states**: Adverbs like *"tighten securely"* or
    *"insert properly"* leave first-time builders guessing. Replace them with
    observable datums: a visual pass/fail check (*"until the copper ring is no
    longer visible"*), an angle (*"35°-40° to avoid the hotend cables"*), a
    torque (*"1.5 Nm / 13.3 lb-in"*), or an expected feel (*"moderate force
    against the magnetic inserts"*).

## 2. Layouts and Procedure Types

<!-- mdformat off(prevent table wrapping) -->

| Dimension | Manual layout (`manual`) | Workbench layout (`workbench`) | Rule |
| :--- | :--- | :--- | :--- |
| **Best for** | Kit builds, maintenance round-trips, upgrades, calibration | Device teardown, fault isolation, drop-in replacement | Use `roundtrip` whenever reassembly is asymmetric; use `teardown` only for symmetric swaps |
| **Front matter** | Title, product summary, variant note, logistics row, **Table of Contents card**, tools and parts tables, 1:1 fastener card | Same content, with the **Table of Contents hidden** so Step 1 starts higher on screen | Always include logistics and a tools step when tools could be confused |
| **Step header** | `2px` orange accent rule (`#FA6831`), condensed uppercase `STEP N`, 2-6 word title | `1px` gray rule, blue `Step N` badge (`#0071CE`) with a concise objective title | Keep titles short and parallel |
| **Visuals** | Screen: **all visuals shown simultaneously** (`1-up` beside bullets, `2-up` or `3-up` in a row above bullets; thumbnails hidden). Print: single visuals full width | **Single `4:3` active stage (`55%` width)** beside bullets with clickable **thumbnail switcher buttons** below; hovering/clicking a colored bullet switches to the frame carrying that marker | Cap each step at **1-3 visuals**: 1-up for one action, 2-up for `locate → act`, 3-up for `context → action → result` |
| **Bullet glyph** | **Solid hexagon** in the marker color, black for non-spatial bullets | **Hollow ring** in the marker color, black for non-spatial bullets | Every colored bullet matches a marker of the same color in that step |
| **Reassembly** | Explicit parts preparation step, then full assembly, torque, firmware, and calibration | Reverse-order note plus per-step `📌` reminders | Never use the reverse-order note when reassembly adds torque limits, datums, single-use consumables, or calibration |
| **Closure** | Milestone notes, tool stowage, functional self-test, lined notes pages in print | Reassembly note and post-repair test | End every guide with an observable functional check and tool stowage |

<!-- mdformat on -->

## 3. Callout Colors and Shapes

### Contrast-First Color Order

Assign colors per step (they reset on the next step), top to bottom in bullet
order, using the contrast-first sequence. The first three hues are far apart, so
small steps never pair near neighbors.

<!-- mdformat off(prevent table wrapping) -->

| Order | Token | Hex | Halo | Notes |
| :--- | :--- | :--- | :--- | :--- |
| Neutral | `black` | `#18181B` | none | Non-spatial bullets, staging lists, and the single disambiguation box in a tools lineup |
| 1 | `red` | `#D92D20` | white | First spatial target |
| 2 | `blue` | `#2563EB` | white | Second target |
| 3 | `green` | `#16A34A` | white | Third target |
| 4 | `orange` | `#F97316` | white | Only when a step needs 4+ colors |
| 5 | `magenta` | `#DB2777` | white | Only when a step needs 5+ colors |
| 6 | `cyan` | `#0284C7` | white | Rarely needed |
| 7 | `yellow` | `#C8D400` | dark | Rarely needed; dark halo for contrast |

<!-- mdformat on -->

*   Never pair near neighbors (red/orange, orange/yellow, blue/cyan,
    red/magenta) in a step with 3 or fewer colors (`G-COLOR-CONFUSABLE`).
*   Use at most **3 marker colors per visual** (`G-MARKER-COLORS`). Split the
    visual or merge bullets beyond that.
*   Never name a marker color in prose (*"the red ring"*). The bullet glyph
    already carries the color, and recoloring makes the word stale
    (`G-COLOR-WORD`).
*   `render_guide.py recolor guide.json` remaps every step to the contrast-first
    order while keeping bullet-to-marker pairs intact.

### Staging Steps Stay Neutral & Use Real 3D Part Renders

Tools and parts staging steps list items rather than locate them, so they use
black bullets and no colored markers (`G-STAGING-COLOR`). Box at most one item
with a neutral `black` rect, and only when two sizes could be confused (for
example, the TX 8 key between TX 6 and TX 10).

*   **3D renders for 3D parts (`G-GENERIC-PART-SVG`, `G-PLACEHOLDER-SHAPE`)**:
    When staging printed or COTS mechanical parts, always use actual **3D
    renders** (`"src"`) that show each part's true 3D shape, bosses, flanges,
    teeth, and cutouts—never flat 2D `<circle>`/`<ellipse>`/`<rect>` SVG
    primitives (which make rings, caps, decks, and spindles look like identical
    concentric circles) or unknown `tool_lineup` placeholder boxes.
*   **Plate-to-part mapping & revision deltas**: When printed parts are grouped
    onto multi-object `.step` build plates, show 3D thumbnails of the parts on
    each plate, note how to split multi-object plates in the slicer
    (*"Right-click → Split → To objects"* for smaller beds like a `180 × 180 mm`
    Prusa Mini), and when a revision modifies only one part, explicitly state
    which plate changed vs. which plates do not need re-printing.

### Multi-Part Sub-Assemblies: Paired Exploded Stack + Ghosted In-Context Renders

Isolated single-part renders (`turret_spindle` alone, `retainer_cap` alone) fail
whenever 3 or more components stack coaxially or couple inside an enclosure
(`G-SUBASSEMBLY-SINGLE-IMAGE`). For every multi-part sub-assembly (such as a
servo horn + hub adapter plate + printed pulley stack, a spindle + belt +
bearing stack, or a multi-tier PCB stack), provide **at least two 3D visuals**:

1.  **Exploded Stack 3D Render**:
    *   Separate the parts along their coaxial insertion axis with a visible
        **coaxial alignment line** through the common axis.
    *   Render mating layers in distinct high-contrast colors
        (`"neutralize": false`) and label the stack in numbered build order
        (`1..N`).
    *   Explicitly call out **hidden underside features** (*"4 pockets on its
        bottom fit over the 4 screw heads"*), **deferred fastener holes** (*"1.
        Toothed metal horn (no centre screw yet)"*), **asymmetric part
        orientation** (*"raised 25T splined boss facing down onto the brass
        shaft"*), and the **exact hex/Torx driver size** on each fastener group
        (*"(2.0 mm key)"*, *"(2.5 mm key)"*).
2.  **Assembled In-Context (Ghosted / X-Ray) 3D Render**:
    *   Show the mated sub-assembly at its installed position with obstructing
        surrounding housings, decks, or spindles rendered **semi-transparent
        (ghosted, `alpha ~0.18–0.25`)** while the active mated parts (e.g.,
        pulley, hub plate, timing belt, driven gear) stay opaque and labeled so
        internal routing and tooth engagement are immediately clear.

### Neutral Base Visuals

Markers only read as foreground when nothing else in the frame is saturated. The
renderer desaturates every base visual by default (photos, CAD renders,
schematics, tool lineups, screens) and draws markers on top at full saturation.

*   Author schematic SVGs in grays with dark strokes; do not fill parts with
    marker hues.
*   Set `"neutralize": false` on an image only when hue itself is the datum (for
    example, wire colors on a connector).

### Marker Shapes, Camera Framing, and Non-Overlap Rules

*   **`circle`**: Screws, bolts, grub screws, alignment pins, round buttons.
    When a bullet names `N` fasteners on an unobstructed top/bottom view, draw
    `N` rings of its color (`G-FASTENER-COUNT-SYNC`).
    *   **No overlapping circles (`G-MARKER-OVERLAP`)**: In perspective or
        exploded views where 3–4 screws sit close together (for example, 4
        `M3x8` screws above a `Ø14 mm` servo horn circle), individual `circle`
        rings overlap into a clumsy cluster. Use a single **`arrow`** (or a
        tight **`rect`**) pointing to the screw group instead of overlapping
        circles.
*   **`rect`**: Rectangular connectors, IC packages, on-screen rows, or a
    sub-assembly layer in an exploded view. Size the box tightly to the physical
    part only—never let a `rect` cross over right-hand diagram text labels.
*   **`arrow`**: Linear motion, insertion axis, pointer to a narrow datum, or
    pointer to a perspective fastener cluster.
*   **`arc`**: Clockwise (`cw`) or counterclockwise (`ccw`) rotation. Pair with
    explicit "clockwise" or "counterclockwise" text when the view is inverted.
*   **`loupe`**: A circular 2x-3x inset for a small feature inside a wide shot,
    placed in an empty corner with a leader line.
*   **Camera-projected coordinates & `4:3` aspect ratio**: Always render CAD
    visuals at a **`4:3` aspect ratio** (`800 × 600` or `1200 × 900`) to match
    the `4:3` SVG marker overlay canvas, choose an elevation (`-70°` to `-90°`
    for underside pockets) where no boss or hole is hidden behind a skirt wall,
    and compute `(x, y)` in `0..100` directly from the 3D camera projection
    (`WorldToDisplay()`) rather than guessing by eye.
*   **Close-up zoom framing for small sub-boards**: When a step mounts a small
    board or component inside a large shell (such as a `42 × 33 mm` adapter
    inside a `Ø136 mm` base), focus and zoom the camera onto that bay so the
    active component fills **`50–75%` of the frame** instead of appearing tiny
    in a full-enclosure overview.

## 4. Semantic Callouts (Non-Action Lines)

### `⚠` Warning (`type: "warning"`)

*   **Use for**: Burn hazards, live mains or battery shorts, fragile connector
    latches, wire-crushing zip ties, or irreversible damage.
*   **Placement**: Strictly before the action bullet where the hazard appears.
    If the step opens on a hot or energized assembly, the warning is the first
    item.
*   **Typography**: Red triangle icon with red text. Bold the core prohibition
    (*"**Press the latch before disconnecting.**"*).

### `ⓘ` Info (`type: "info"`)

*   **Use for**: Torque values, expected feel, pass/fail adjustment checks,
    firmware reminders, compatibility notes.
*   **Placement**: `indent: 1` under the action it qualifies, `indent: 0` for
    step-wide state.
*   **Prose rule**: Never start with "Note:" or "Info:".

### `📌` Pin (`type: "pin"`)

*   **Use for**: Persistent constraints, on-screen wizard sync, or reassembly
    deltas in teardown guides.
*   **Prose rule**: Never start with "Reminder:".

## 5. Pacing, Staging, and Language

1.  **Tools first, including workholding**: Name tools by exact size and drive
    (`TX 8 Torx key`, `2.5 mm Allen key`, `Phillips #00`). Suggest surface
    protection from items on hand (an empty box over a heated bed, a mat under a
    display).
2.  **Power and thermal order**: Powered positioning → hot operations → explicit
    cooldown → power off and unplug (or disconnect the battery) → surface
    shielding.
3.  **Loosen vs. remove**: *Loosen* (with "a few turns are enough") for captive
    screws and clamps; *release* or *remove* when hardware comes out, naming the
    exact size so fasteners are not swapped on reassembly.
4.  **Counter-torque**: When torquing a threaded part on a fragile assembly,
    give counter-holding its own bullet and visual before the torque bullet.
5.  **Cable routing**: Name the exact channel, slot, and any excluded wires.
    Never write "route the cables neatly".
6.  **Parts preparation & hardware disambiguation**: Before installing
    replacement or kit parts, stage them with quantities in a dedicated step so
    worn, unused, and active hardware never mix:
    *   **Exact COTS SKUs & lookalike warnings**: Always name the exact
        manufacturer SKU/part number (for example, `Seeed SKU 103030216`,
        `Waveshare Bus Servo Adapter (A) SKU 25514`) and warn against
        incompatible lookalikes (`ReSpeaker XVF3800`,
        `Waveshare Driver HAT SKU 27577`).
    *   **Separate machine screws from brass heat-set inserts**: List machine
        screws/nuts/washers separately from brass heat-set inserts (`M2`,
        `M2.5`, `M3`), and explicitly warn against using pointed self-tapping
        screws in brass inserts.
    *   **Power supplies, cables & optional components**: Include required
        external power bricks (`12V 3A 5.5 × 2.1 mm DC power supply`) and data
        cables (`USB-C`). When a schematic or floor pocket includes an auxiliary
        component (such as a `470 µF 25V` smoothing capacitor), state upfront
        whether it is **required or optional for initial bring-up**, give the
        exact search query and physical package size
        (`470uF 25V electrolytic capacitor 10x12.5mm`), and specify leg polarity
        (`negative stripe (−) to GND, longer positive (+) leg to 12 V`).
    *   **Unused kit accessories & COTS-to-printed coupling**: When a COTS kit
        ships with multiple horns or brackets in the bag (for example, a driven
        `25T` splined top horn vs. a smooth-bore `Ø6.05 mm` passive bottom idler
        horn), state which piece to use and which to set aside. When a standard
        smooth-bore metal pulley (`5/6/6.35 mm` bore + grub screws) cannot bolt
        directly to a toothed servo horn, explain why the **printed hub plate +
        printable pulley stack** (`pulley_hub_plate` +
        `gt2_20t_pulley_printable`) is used instead and that **both printed
        parts are required**. When a part can be either purchased COTS or
        printed in TPU (such as a `GT2 160 mm (80T) 6 mm` closed-loop belt),
        list both options and the exact COTS search string (`2GT-160-6`).
    *   **Integral printed bosses vs. discrete hardware standoffs**: When a PCB
        mounts onto posts molded into a 3D-printed floor, explicitly distinguish
        **integral printed floor posts (with melted brass inserts — nothing
        separate to buy)** from **discrete hex standoffs/spacers** installed
        between upper boards, and give the numbered bottom-to-top stack order.
    *   **Unmarked parallel connectors**: Never invent a port number
        (`"Port 1"`) when a COTS board has two unmarked headers wired in
        parallel (such as the two white 3-pin servo bus headers on
        `Waveshare SKU 25514`). State that **either header works**, recommend
        the header closer to where the cable arrives, and note the keying latch
        orientation.
7.  **Closed-loop finish**: End with an active test, stow temporary jigs and
    shields, and close with a short completion note.

### Builder Register

*   **Human part names, not CAD identifiers.** Map model IDs to names with
    `display_names` (`"base_shell": "the base shell"`); the renderer applies
    them to titles, bullets, tables, captions, and diagram labels
    (`G-CAD-LEAK`).
*   **No designer coordinates.** Drop `X/Y/Z =` heights and other values a
    builder cannot measure.
*   **Values in bold, code only for code.** Backtick spans render as bold values
    unless they are commands, paths, or on-screen strings (which stay
    monospace).
*   **Describe the product, never the guide.** Titles, subtitles, and bullets
    never reference other publishers' guide styles or call the guide
    "print-ready" (`G-META-COPY`).

## 6. Non-Hardware Contexts

When the user asks for a step-by-step guide to a software, infrastructure, lab,
or operational workflow, keep the same mechanics rather than writing a generic
numbered list:

*   **Tools and parts → prerequisites**: Binaries, permissions, flags, and
    backups, staged with exact versions and paths.
*   **Surface protection and power isolation → blast-radius guards**: Snapshot
    state, drain traffic, or branch before mutating steps.
*   **Visuals and markers → synced screens and diagrams**: `ui_screen` panels or
    neutral architecture SVGs with markers on the exact flag, key, port, or
    control the bullet names.
*   **Torque and visual datums → output datums**: The exact status code, log
    line, or metric threshold that proves the step worked.
