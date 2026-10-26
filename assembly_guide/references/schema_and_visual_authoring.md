# Guide JSON Schema & Visual Authoring Reference

`scripts/render_guide.py` validates a declarative `guide.json` specification
against the authoring lint gates and compiles it into an interactive HTML guide
(`--html`), a print PDF rendered from the same HTML through headless Chrome
(`--pdf`), and portable GitHub Flavored Markdown (`--markdown`). `--audit` adds
rendered-geometry and pagination checks.

## 1. Top-Level `guide.json` Schema

```json
{
  "title": "How to replace the print fan",
  "subtitle": "Remove the old fan, route the new cable, and run the fan self-test.",
  "category": "Printer maintenance",
  "guide_id": "fan-replacement-v1",
  "canonical_url": "https://example.com/guides/fan-replacement",
  "archetype": "roundtrip",
  "default_dialect": "manual",
  "difficulty": "Moderate",
  "time_required": "25–40 minutes",
  "variants": [
    {
      "label": "Multi-tool printers",
      "note": "Use the multi-tool fan guide instead."
    }
  ],
  "tools": [
    {"name": "TX 8 Torx key", "spec": "Torx T8 L-key"},
    {"name": "2.5 mm Allen key", "spec": "Hex 2.5 mm"},
    {"name": "Cardboard protection box", "spec": "Empty filament box"}
  ],
  "parts": [
    {"name": "New print fan", "qty": "1x"},
    {"name": "Zip tie", "qty": "1x (2.5 x 100 mm)"}
  ],
  "fastener_cheatsheet": [
    {"label": "M3x10b", "diameter_mm": 3.0, "length_mm": 10.0, "head": "Socket cap", "qty": "3x"},
    {"label": "M3x14", "diameter_mm": 3.0, "length_mm": 14.0, "head": "Socket cap", "qty": "2x"},
    {"label": "M3x40", "diameter_mm": 3.0, "length_mm": 40.0, "head": "Socket cap", "qty": "2x"}
  ],
  "display_names": {
    "dwarf_cover_door": "the electronics cover door",
    "base_shell": "the base shell"
  },
  "neutralize_base_visuals": true,
  "include_print_notes_pages": 2,
  "reassembly_note": "",
  "steps": []
}
```

### Field Rules

*   **`archetype`**: One of:
    *   `"assembly"`: First-time build or bring-up (no teardown phase).
    *   `"roundtrip"`: Disassembly → parts preparation → explicit assembly →
        functional check and calibration. Required whenever reassembly has
        torque values, single-use consumables, angle datums, or calibration.
    *   `"teardown"`: Symmetric disassembly that appends the reverse-order
        reassembly note. The linter rejects it when torque specs or single-use
        consumables appear.
*   **`default_dialect`**: `"manual"` (thin accent rule, condensed `STEP N`,
    hexagon bullets, adaptive 1/2/3-up grids) or `"workbench"` (4:3 stage with
    thumbnails, ring bullets). The HTML guide includes a live layout toggle;
    `build --pdf-dialect` picks the layout for the PDF.
*   **`difficulty`**: `"Very Easy"` | `"Easy"` | `"Moderate"` | `"Difficult"` |
    `"Very Difficult"`.
*   **`display_names`** *(optional)*: Maps CAD or model identifiers to the names
    a builder uses. The renderer applies the map to titles, bullets, tables,
    captions, and diagram labels (bare or in backticks), so bullets can keep
    identifiers while output stays readable.
*   **`neutralize_base_visuals`** *(default `true`)*: Desaturates every base
    visual so only markers carry color. Override per image with
    `"neutralize": false` when hue is the datum (for example, wire colors).
*   **`fastener_cheatsheet`** *(optional)*: Renders a `1:1` millimeter fastener
    silhouette card (CSS `mm` units; print at 100% scale).
*   **Copy rule**: `title`, `subtitle`, `variants`, and bullets describe the
    product. Never reference other publishers' guide styles or call the guide
    "print-ready" (`G-META-COPY`, an error).

## 2. Step & Bullet Schema

Each entry in `"steps"` represents one atomic physical or operational objective:

```json
{
  "number": 5,
  "title": "Disconnecting the print fan",
  "section": "Disassembly",
  "milestone": "",
  "images": [
    {
      "caption": "Loosen dwarf-cover-door M3x14 screw",
      "src": "assets/step05_a.png",
      "markers": [
        {"shape": "circle", "color": "red", "x": 46, "y": 41, "r": 5.5}
      ]
    },
    {
      "caption": "Lift cover door upward",
      "src": "assets/step05_b.png",
      "markers": [
        {"shape": "arrow", "color": "cyan", "x1": 54, "y1": 52, "x2": 58, "y2": 28},
        {"shape": "arrow", "color": "cyan", "x1": 62, "y1": 74, "x2": 55, "y2": 66}
      ]
    },
    {
      "caption": "Cut cable zip tie and unlatch fan connector",
      "src": "assets/step05_c.png",
      "markers": [
        {"shape": "arrow", "color": "green", "x1": 64, "y1": 52, "x2": 53, "y2": 57},
        {"shape": "rect", "color": "orange", "x": 48, "y": 60, "w": 10, "h": 9}
      ]
    }
  ],
  "bullets": [
    {
      "type": "action",
      "color": "red",
      "fastener_count": 1,
      "text": "Loosen the **M3x14** screw of the dwarf-cover-door."
    },
    {
      "type": "action",
      "color": "cyan",
      "text": "Lift the dwarf-cover-door to access the electronics board."
    },
    {
      "type": "action",
      "color": "green",
      "text": "Cut the zip tie holding the cable bundle in place, keeping flush cutters angled away from the wire insulation."
    },
    {
      "type": "warning",
      "text": "The connector has a safety latch. **Press the latch before disconnecting.** Pulling on the wires directly can tear the header off the board."
    },
    {
      "type": "action",
      "color": "orange",
      "text": "Disconnect the print fan cable."
    }
  ]
}
```

### Bullet `type` Values

*   `"action"` — Standard step instruction. Uses `"color"` (`"black"`, `"red"`,
    `"orange"`, `"yellow"`, `"green"`, `"cyan"`, `"blue"`, `"magenta"`).
    Supports inline Markdown bold (`**...**`), italic (`*...*`), and inline code
    spans (single backticks). Optional `"fastener_count"` (integer) enables
    automatic check against the number of matching-color `"circle"` markers
    across the step's images.
*   `"subaction"` — Indented secondary bullet (`indent: 1`, `"color": "black"`
    by default), used for variant routing links in Step 1 Introduction.
*   `"warning"` — Red `⚠` triangle alert + red text. Must precede the action
    bullet it guards.
*   `"info"` — Circled `ⓘ` technical note, torque spec, or pass/fail datum. Set
    `"indent": 1` to nest directly beneath the parent action bullet, or
    `"indent": 0` for step-level notes. Do **not** start `"text"` with `"Note:"`
    or `"Info:"`.
*   `"pin"` — Pushpin `📌` for persistent mechanical guardrails, wizard sync
    prompts, or reassembly deltas. Do **not** start `"text"` with `"Reminder:"`.

## 3. Normalized Vector Marker Coordinates (`0-100` Space)

All image frames use a `4:3` coordinate canvas (`x` in `0..100`% width, `y` in
`0..100`% height) so SVG vector overlays stay locked to the exact hardware
feature across responsive desktop, mobile, zoom lightbox, and print PDF views.

*   **Render at `4:3` & project from the 3D camera**: Always render CAD images
    at `4:3` (`800 × 600` or `1200 × 900`) and compute `(x, y)` in `0..100`
    directly from the 3D renderer's camera projection (`WorldToDisplay()` in
    VTK/PyVista or `vector.project(camera)` in Three.js) so rings land
    dead-center on every boss and screw hole.
*   **Unobstructed hole angles & close-up zoom**: For recessed underside bosses,
    use a steep camera elevation (`-70°` to `-90°`) so skirt walls never hide a
    hole. For small PCBs or sub-assemblies inside a larger housing, zoom the
    camera onto the active bay so the target component fills `50–75%` of the
    frame.
*   **`circle`**:
    `{"shape": "circle", "color": "red", "x": 50, "y": 42, "r": 3.8}` (`r` is
    percentage of image width; `2.5`–`4.5` frames single screws cleanly). Never
    place overlapping circles on tightly clustered perspective/exploded screws
    (`G-MARKER-OVERLAP`); use an `arrow` or `rect` instead.
*   **`rect`**:
    `{"shape": "rect", "color": "green", "x": 22, "y": 48, "w": 56, "h": 12, "angle": 0}`
    (`x`, `y` is top-left corner; `w`, `h` are width and height percentages;
    optional `"angle"` rotates the rectangle in degrees around its center).
    When framing an angled connector or header strip in an isometric 3D render
    (such as a 40-pin GPIO header), set `"angle"` (e.g., `30.5`) and tight `w`/`h`
    so the rectangle hugs only the connector rather than covering half the board
    with an axis-aligned box. Keep `rect` boxes clear of right-hand diagram text
    labels.
*   **`arrow`**: `{"shape": "arrow", "color": "cyan", "x1": 30, "y1": 70, "x2":
    48, "y2": 45}` (tail at `x1,y1` pointing to tip at `x2,y2`).
*   **`arc`**: `{"shape": "arc", "color": "green", "x": 62, "y": 48, "r": 14,
    "start_deg": -40, "end_deg": 150, "direction": "ccw"}` (draws a curved
    rotational arrow around center `x,y` with arrowhead at the `"cw"` or `"ccw"`
    end).
*   **`loupe`**: `{"shape": "loupe", "color": "orange", "target_x": 45,
    "target_y": 55, "x": 22, "y": 26, "r": 18, "zoom": 2.4}` (renders a circular
    magnified inset at `x,y` magnifying `target_x,target_y` when `"src"` or
    `"svg"` is present, connected by a leader line).

## 4. Visual Sources When Photos Are Not Provided

Every image object in `"images"` must provide **one** of four visual sources
(never leave empty CSS div placeholders):

1.  **`"src"` (Photo, CAD Render, or Generated Image — Mandatory for 3D Parts &
    Sub-Assemblies)**: Path or URL to a real photograph, CAD/build123d 3D
    render, or generated illustration. Pass `--embed-images` to
    `render_guide.py` to inline local PNG/JPEG/WebP files as base64 `data:` URIs
    for single-file portability.
    *   **3D Part Staging**: Always use 3D renders (`"src"`) when staging or
        assembling 3D-printed and COTS parts (`G-GENERIC-PART-SVG`). Never draw
        flat 2D `<circle>`/`<ellipse>`/`<rect>` shapes to represent 3D parts.
    *   **Multi-Part Sub-Assemblies (`G-SUBASSEMBLY-SINGLE-IMAGE`)**: When a
        step stacks 3+ coaxial parts or routes a belt/gear inside a housing,
        provide 2–3 `"src"` renders: (a) an **Exploded Stack 3D render**
        (`"neutralize": false` when color-coding stack layers, with a coaxial
        alignment line and numbered `1..N` labels naming underside pockets,
        empty holes, and hex key sizes) and (b) an **Assembled In-Context
        (ghosted) 3D render** (surrounding housing/deck rendered
        semi-transparent so internal belt/gear engagement is visible).
2.  **`"tool_lineup"` (Declarative Step-2 Hand-Tool Staging Card)**: Draws a
    neutral, full-width hand-tool silhouette lineup with labels sized to fit
    each slot. Staging steps use black bullets; add at most one neutral `black`
    `rect` around an easily confused size:

    ```json
    {
      "caption": "Required hex and Torx keys",
      "tool_lineup": [
        {"kind": "torx_key", "label": "TX 6", "scale": 0.78},
        {"kind": "torx_key", "label": "TX 8", "scale": 0.86},
        {"kind": "torx_key", "label": "TX 10", "scale": 0.94},
        {"kind": "hex_key", "label": "2.5 mm", "scale": 0.90},
        {"kind": "hex_key", "label": "3.0 mm", "scale": 1.0}
      ],
      "markers": [
        {"shape": "rect", "color": "black", "x": 25.5, "y": 18, "w": 12, "h": 68}
      ]
    }
    ```

    *(For `N` items in `tool_lineup`, item `i` (`0`-indexed) is horizontally
    centered at `x = 10 + 80 * (i + 0.5) / N` in `0-100` space.)*

    Supported `"kind"` silhouettes: `"torx_key"`, `"hex_key"`, `"wrench"`,
    `"universal_wrench"`, `"screwdriver"`, `"soldering_iron"`, `"pliers"`,
    `"spudger"`, `"tweezers"`, `"brass_brush"`, `"mat"`, `"cardboard_box"`,
    `"zip_tie"`, `"fan"`, `"nozzle"`, `"pcb"`, `"cable"`. Unknown kinds trigger
    `G-PLACEHOLDER-SHAPE` (`ERROR`) because generic dashed placeholder boxes are
    prohibited; use a 3D render (`"src"`) for custom or 3D-printed parts.

3.  **`"ui_screen"` (Declarative Device LCD / Firmware / CLI Screen)**: Renders
    an authentic dark-bezel instrument/printer screen or terminal panel with
    selectable rows so `rect` markers highlight the exact menu command:

    ```json
    {
      "caption": "Navigate to Unload Filament",
      "ui_screen": {
        "device_label": "CONTROL PANEL",
        "breadcrumb": "FILAMENT",
        "rows": [
          "Return",
          "Load Filament",
          "Unload Filament",
          "Change Filament",
          "Purge Filament"
        ],
        "active_index": 2,
        "footer": "Nozzle: 215°C   Bed: 60°C"
      },
      "markers": [
        {"shape": "rect", "color": "red", "x": 18, "y": 44, "w": 68, "h": 11}
      ]
    }
    ```

4.  **`"svg"` (Custom 4:3 Orthographic / Isometric Technical Schematic)**:
    Inline SVG inner markup rendered inside `viewBox="0 0 400 300"`. Use crisp
    technical strokes (`#27272A`, `stroke-width="2"`), subtle part fills
    (`#F4F4F5` aluminum/steel, `#27272A` matte polymer, `#F97316` accent printed
    parts, `#15803D` solder-mask PCBs, `#D97706` brass/copper), and let the
    `"markers"` array draw the colored callout rings and arrows cleanly on top.
    Keep internal labels minimal so markers carry the spatial mapping.

## 5. Pure Markdown Output Conventions

When emitting Markdown (`--markdown` or direct chat Markdown without HTML):

*   Render a structured **Guide Logistics** table at the top (`Difficulty`,
    `Time Required`, `Archetype`, `Tools`, `Parts`).
*   Format step headings cleanly without double numbering
    (`## Step 5: Disconnecting the print fan`).
*   Prefix colored bullets with explicit color tags
    (`- **[RED]** Loosen the **M3x14** screw...`,
    `- **[CYAN]** Lift the dwarf-cover-door...`) when paired with annotated
    images, or clean standard bullets when unaccompanied by color-marked
    visuals.
*   Render `warning` items as GitHub `[!WARNING]` or `[!CAUTION]` callouts
    immediately above the guarded bullet, `info` items as indented sub-bullets
    prefixed with `ⓘ`, and `pin` items prefixed with `📌`.
