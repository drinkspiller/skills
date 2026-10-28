# Route-Flow Design System

These are the visual and editorial decisions that the route-flow page uses. Apply
all of them unless the user overrides one. `assets/template.html` already
implements them; this file says why, so new nodes stay consistent.

## 1. Format

-   One static HTML file, inline CSS, hand-authored inline `<svg>`. **No
    JavaScript, no Mermaid, no external fonts or CDNs.** The page has to render
    identically from a static file host with no build step.
-   Max content width `1180px`. Each SVG uses `width:100%; min-width:900px`
    inside a card with `overflow-x:auto`, so it scrolls on narrow screens instead
    of shrinking text.
-   Page order: header + legend → pending-changes callout (only if any content
    is unmerged) → **1. Page routing** SVG → route table → **2. Request
    perimeter** SVG (if the changes touch server-side checks) → source-changes
    grid → footer.

## 2. Color = meaning (fixed palette)

| Role | Fill | Stroke | Title text | Use for |
| --- | --- | --- | --- | --- |
| Entry / route | `#eff6ff` | `#2563eb` | `#1e3a8a` | `/`, generic request nodes, "Yes" branches |
| Auth / terms gate | `#fffbeb` | `#d97706` | `#92400e` | Signed-in decision, sign-in step, terms modal/guard |
| Access / deny gate | `#fff1f2` | `#e11d48` | `#9f1239` | Allowlist/permission decisions, 404/denied results |
| Public surface | `#ecfdf5` | `#059669` | `#065f46` | Unauthenticated pages, "accept" branches |
| Authenticated app | `#f5f3ff` | `#7c3aed` | `#4c1d95` | App home and leaf routes |
| New in change set | `#f0fdfa` | `#0d9488` dashed | `#115e59` | Nodes/edges introduced by the changes being diagrammed |
| Neutral | `#f8fafc` | `#64748b` | `#334155` | External services you don't own |

-   Body text in nodes: `#475569`; secondary/footnote text: `#64748b`.
-   An arrow takes the color of the **outcome** it leads to (blue = proceed,
    green = public/accept, rose = deny, teal = new path, slate = neutral fan-out).
    Each color has its own `<marker>` arrowhead.
-   Keep the legend in the header in sync with every color actually used.

## 3. Node vocabulary

| Shape | Meaning | Geometry |
| --- | --- | --- |
| Rounded rect, solid 2px | Route or page | `rx=10`, width 220–280, height 64–118 |
| Diamond | Decision | half-width 74–110, half-height 44–48; **≤2 text lines** (title 12–13px bold + 9.5–11px guard name) |
| Rounded rect, dashed `5,3`, 1.5px | Transient step (sign-in, redirect hop) | `rx=8`, ~132×56 |
| Rounded rect, dashed `6,3`, 2px | New node, or deny/error terminal | color by role |
| Pill `NEW` | Marks a new decision diamond | 38×16, `rx=8`, teal, placed above the diamond's right shoulder |

-   Route title 14–16px bold; component name 11–12px in the role color; behavior
    lines 10–11px. Nothing below 9px.
-   Branch labels sit on a small filled rect (`rx=4`) in the branch's light
    fill so they stay legible where they cross lines; short labels (`Yes`, `No`)
    can float beside a vertical edge without a rect.
-   Deny edges and "decline" edges are dashed (`5,4`). Happy-path edges are solid.

## 4. Layout grid

-   Main happy path runs **straight down one column** (`x=680`): signed-in →
    access gate → terms gate → app home.
-   Public surfaces go **left** (`x≈190`). Deny / gated branches go **right**
    (`x≈900`). Terminal error boxes (404) go up-right so they don't collide with
    the gated route below the second decision.
-   Leaf routes share one row (`y≈690`) under the app home with elbow
    connectors (`down 28 → across → down`).
-   Edges are orthogonal (horizontal/vertical segments only). Leave ≥4px between
    an arrowhead and the node it points to.
-   Grow the `viewBox` height instead of compressing rows when adding nodes.

## 5. Route table

-   One row per route, including the wildcard. Columns: Route · Access badge ·
    one column **per user state that the gates distinguish** (e.g. Signed-out /
    Signed-in denied / Signed-in allowed). Add a state column when a new gate
    creates a new state, rather than cramming conditions into one cell.
-   Access badges: `badge-public` (green), `badge-auth` (blue), `badge-redirect`
    (amber), `badge-gate` (rose). New routes get `badge-new` after the path and
    the `is-new` row class (teal left rule).
-   Cells name the exact mechanism in `<code>`: status code, guard name, server
    action, RPC name.

## 6. Request-perimeter diagram

-   Horizontal lanes, one per group of endpoints that share the same ordered
    checks. Lane header: UPPERCASE 12px bold, then a 10.5px line listing the
    endpoints separated by ` · `.
-   Stages left→right in **actual execution order** read from code. Each check
    stage drops a dashed arrow to its failure code (bold 10.5px in the stage
    color) below it.
-   Exempt endpoints get their own lane showing what they check instead.
-   Long prose (e.g. what gets stripped for non-owners) goes in a text-only lane
    split across lines ≤ ~130 characters each, never one overflowing line.

## 7. Editorial rules

-   Every label must come from the code or the change itself. If something is
    plausible but unverified, leave it off the diagram and mention it in the
    reply instead.
-   Prefer exact identifiers (guard names, flags, status codes) over prose.
-   Callout banner states: which content is unmerged, which environment
    enforces each gate, any dev override, and the controlling flag.
-   Source-changes grid: one card per change with ID link, short title, and the
    routes/gates/services it adds. Say explicitly which changes don't affect
    routing.
-   Footer: `Updated YYYY-MM-DD · previous version (date)` linking the backup.
-   No first-person plural in page copy.

## 8. Common render defects (check the screenshot for these)

-   Third text line inside a diamond spills past its edges → drop it; put the
    detail in the section lede or table.
-   Floating annotation text overlapping an edge or diamond.
-   Text wider than its rect (often the last line of a pipeline stage) →
    shorten wording, don't shrink below 9px.
-   Single long text line running past the SVG's right edge.
-   Arrowhead hidden under a node because the line ends inside the shape.
