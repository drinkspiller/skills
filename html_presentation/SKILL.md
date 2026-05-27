---
name: html-presentation
description: |
  Build polished, single-file HTML slide presentations. Handles theme
  selection (or custom theme building), navigation, presenter view with
  speaker notes, local hosting, version management, image best
  practices, Google Slides export via screenshot pipeline, and hosting
  on Google infra (Zipline, x20). Use when someone asks for a slide
  deck, presentation, or HTML slides.
---

# HTML Presentation Skill

You are building a polished, single-file HTML slide presentation. Every
deck you create must include the full feature set described below.

---

## Step 1: Theme Selection

Before writing any HTML, work with the user to establish the visual theme.
This is a collaborative process — do NOT just pick a theme and start building.

### Step 1a: Discover existing themes

Before suggesting anything, scan for existing HTML presentations that the
user has built previously. Look in:

1. **The user's workspace** — search for `.html` files that contain
   `data-idx=` (the signature of a deck built with this skill)
2. **Knowledge items** — check for theme definitions in the user's
   knowledge base (e.g., under `uxr_design_systems/artifacts/`)
3. **The training directory** — look in `uxr_skills/training/` for
   existing decks

For each deck found, extract the `:root` CSS custom properties to
reconstruct the theme. Present them to the user like this:

"I found these themes from your previous presentations:

1. **From 'Jetski Skills for UXRs'** — warm off-white, sage/purple/
   terracotta accents, Inter font (Organic Modern style)
2. **From 'Q4 Research Readout'** — dark navy, coral highlights, Google
   Sans font (Blueprint style)
3. **Build a new theme** — I'll walk you through creating one from scratch

Which would you like to use, or should we create something new?"

If no previous decks are found, skip to Step 1b.

### Step 1b: Build a new theme (or if user wants something fresh)

Walk the user through these decisions conversationally:

1. **Mood**: What feeling should the presentation convey?
   - Suggest options: professional, playful, technical, warm, bold,
     minimal, dark mode, editorial, corporate, academic
   - Ask: "What's the audience and topic? That'll help me suggest
     something that fits."

2. **Color palette**: Based on the mood, suggest 2-3 palettes of 4-5
   harmonious colors. For each palette, always define:
   - Primary accent (used most — buttons, step numbers, borders)
   - Secondary accent (contrast — code elements, alternate sections)
   - Attention/highlight (sparingly — callouts, key data)
   - Background (the canvas — light or dark)
   - Surface (card/panel background)
   - Text hierarchy: primary, secondary, muted
   - Suggest specific hex values, not vague descriptions

3. **Typography**: Suggest 2-3 font pairings from Google Fonts:
   - One display/heading font (bold weight)
   - One body font (readable at small sizes)
   - Optionally a monospace for code
   - Example pairings: Inter + JetBrains Mono, Outfit + Source Sans,
     DM Sans + IBM Plex Mono, Poppins + Work Sans

4. **Background motif**: Subtle radial gradients, geometric SVG patterns,
   topographic lines, or clean/minimal.

5. **Component style**: Card border-radius (8px for sharp, 16px for soft),
   shadow depth, border-left accents vs. full borders.

### Step 1c: Preview the theme

After settling on a theme, **generate a preview** before building the
full deck. Create a single-slide HTML file with:

- The title slide using the chosen colors, fonts, and background motif
- A sample heading ("Your Presentation Title")
- A subtitle and decorative elements that showcase the accent colors
- Cards or badges that demonstrate the component style

Serve it on the HTTP server and ask the user to review:

"Here's a preview of the theme. Open http://localhost:8847/preview.html
and let me know what you think. Want to adjust any colors, fonts, or
the overall feel?"

Iterate on the preview until the user is happy before building slides.

### Step 1d: Document the theme

Record the final theme as CSS custom properties in `:root {}`. This
becomes the single source of truth — all component styling references
these tokens, never hardcoded colors.

```css
:root {
  --bg: #FAF8F4;
  --surface: #FFFFFF;
  --surface-alt: #F0ECE5;
  --border: #E5E0D8;
  --text: #2C2A35;
  --text-secondary: #65636E;
  --text-muted: #9C99A5;
  --primary: #5B8C6E;      /* sage */
  --secondary: #7B6EC4;    /* purple */
  --accent: #C87050;       /* terracotta */
  --highlight: #B89840;    /* gold */
  --shadow-sm: 0 1px 3px rgba(44,42,53,0.06);
  --shadow-md: 0 4px 16px rgba(44,42,53,0.08);
}
```

---

## Step 2: Required Infrastructure

Every presentation MUST include ALL of the following. Do not skip any.

### 2a. Slide structure

```html
<div class="deck">
  <div class="s" data-idx="0" data-notes="Speaker notes here...">
    <!-- slide content -->
  </div>
  <div class="s" data-idx="1" data-notes="...">
    <!-- slide content -->
  </div>
</div>
```

Rules:
- Each slide is a `<div class="s">` with `data-idx` (0-based) and
  `data-notes` for speaker notes.
- Use additional classes for variants: `.divider` (centered section
  breaks), `.screen-share` (demo placeholders), `.title-slide` (hero).
- All slides hidden by default (`display:none`), `.active` shows current.
- Fade-in animation on slide transitions.

### 2b. Navigation controls

```html
<button class="home-btn" onclick="show(0)">⌂</button>
<nav>
  <button onclick="go(-1)">←</button>
  <button onclick="go(1)">→</button>
</nav>
<div class="progress" id="prog"></div>
<div class="counter" id="ctr"></div>
```

- **Home button**: Fixed bottom-left, returns to slide 0.
- **Prev/Next**: Fixed bottom-right, circular buttons with hover effects.
- **Progress bar**: Fixed bottom, full-width, gradient from primary to
  secondary accent color. Width = `(currentSlide + 1) / total * 100%`.
- **Counter**: Shows `"3 / 31"` format, fixed near nav buttons.
- **Keyboard**: ArrowRight and Space = next, ArrowLeft = previous.

### 2c. Speaker notes panel

```html
<div class="notes-panel" id="notes">
  <div class="nh">Speaker Notes · press N to toggle</div>
  <div id="nt"></div>
</div>
```

- Slides up from bottom when toggled with **N** key.
- Dark background (`#2C2A35`), light text, max-height 30vh.
- Reads from `data-notes` attribute of current slide.
- Every slide MUST have speaker notes. Write them in a conversational,
  first-person tone — these are what the presenter would actually say.

### 2d. Presenter view

Pressing **P** opens a separate window with:

- **Current slide counter** (e.g., "12 / 31")
- **Timer** counting up from 00:00
- **Speaker notes** for the current slide (large, readable text)
- **Next slide preview** (title of the upcoming slide)
- **Navigation controls** (Home, Prev, Next buttons)
- **BroadcastChannel sync**: Main window and presenter window stay in
  sync. Navigating in either window updates the other.

Implementation: Use `window.open()` to create the presenter window and
`document.write()` to inject a complete HTML document. Use
`BroadcastChannel('deck-name')` for two-way sync.

The presenter view uses its own dark theme (background `#1a1a2e`) with
Inter font, regardless of the main deck theme.

### 2e. Auto-hosting

After creating or updating the deck, automatically:

1. Save the HTML file to a working directory (e.g., `/tmp/deck/` or the
   user's preferred location).
2. Copy any image assets to the same directory.
3. Start a Python HTTP server:
   ```bash
   cd /tmp/deck && python3 -m http.server 8847 &
   ```
4. Tell the user to open `http://localhost:8847` in Chrome.
5. If the port is already in use, kill the existing server first:
   ```bash
   lsof -ti:8847 | xargs kill -9 2>/dev/null
   ```

### 2f. Version management

Before making significant changes to an existing deck:

1. **Ask the user**: "Want me to save the current version before editing?"
2. If yes, save a copy with a descriptive name:
   ```
   versions/YYYY.MM.DD Description.html
   ```
3. Keep a `versions/` directory alongside the working file.
4. When creating a new deck variant (e.g., shorter version), save as a
   separate file, not overwrite the original.

Always maintain at least two files:
- The **working copy** (e.g., `index.html`) — actively edited
- The **frozen version** in `versions/` — never modified after saving

---

## Step 3: Slide Content Patterns

### Images

- **Always make images large**: Use `max-height: 65vh` or `max-height: 70vh`
  with `object-fit: contain` so images fill the available vertical space
  without distortion.
- **Use actual image files**, not placeholders. Generate images with the
  image generation tool if needed.
- For screenshots, use `border-radius: 10px` and `box-shadow: var(--shadow-md)`.
- When showing two columns (text + image), use a `grid` with
  `grid-template-columns: 1fr 1fr` and center the image with flexbox.
- Background images on title slides: Use `background-size: 45%` and
  position `bottom right` so the image complements rather than competes
  with the text.

### Typography scale

| Element | Size | Weight | Use |
|---------|------|--------|-----|
| `h1` | 3.6em | 800 | Title slide only |
| `h2` | 2.4em | 700 | Slide headings |
| `h3` | 1.2em | 600 | Card titles, subheadings |
| `.sub` | 1.2em | 400 | Subtitle text |
| Body | 0.92-1.05em | 400 | Lists, descriptions |
| `.small` | 0.9em | 400 | Captions, footnotes |

Use `letter-spacing: -0.03em` on h1, `-0.02em` on h2 for tighter display
type.

### Common slide types

**Section divider**: Centered heading with label. Use `.divider` class.
Keep to 2-3 lines max.

**Content slide**: Label + heading + body content. Padding `40px 70px`.

**Two-column**: `grid-template-columns: 1fr 1fr` with `gap: 20px`.
Text on left, visual on right.

**Card grid**: 2-column (`grid4`) or 3-column (`grid3`) cards with
consistent border-left accents matching theme colors.

**Code example**: Dark code box (`background: #2C2A35`, monospace font,
`border-radius: 10px`, horizontal scroll).

**Quote block**: Left-bordered, light background, italic text.

**Steps / numbered list**: Custom counter with numbered circles (accent
color background, white text, 24px diameter).

**Screen share / demo**: Centered layout with dashed border, emoji icon,
and subtitle. Use for "this is where you share your screen" placeholders.

**Data table**: Full-width, collapsed borders, uppercase header labels,
alternating row emphasis via border-radius on first/last cells.

### Slide count guidance

| Duration | Slides | Pace |
|----------|--------|------|
| 15 min | 12-15 | ~1 min/slide |
| 30 min | 25-32 | ~1 min/slide |
| 45 min | 30-40 | ~1-1.5 min/slide |
| 60 min | 35-45 | ~1.5 min/slide |

---

## Step 4: Assembly

### File structure

```
deck_name/
├── index.html          ← working copy
├── assets/             ← images, generated visuals
└── versions/
    └── YYYY.MM.DD Description.html
```

### Single-file requirement

The entire presentation — HTML, CSS, JavaScript — must be in ONE file.
The only external dependencies allowed are:

- Google Fonts CDN (`fonts.googleapis.com`)
- Image files in the same directory (referenced by filename, no paths)

### CSS organization

Put all CSS in a single `<style>` block in `<head>`:

1. `:root` custom properties (theme tokens)
2. Reset and body styles
3. Background motifs (`body::before`, `body::after`)
4. Slide container and transition styles
5. Typography scale
6. Component classes (cards, labels, badges, quotes, code, tables)
7. Slide variant classes (divider, screen-share, title)
8. Navigation and progress bar
9. Notes panel
10. Responsive overrides (`@media`)

### JavaScript organization

Put all JS in a single `<script>` block before `</body>`:

1. Slide navigation functions (`show()`, `go()`)
2. BroadcastChannel setup
3. Presenter view function (`openPresenter()`)
4. Keyboard event listener
5. Initial `show(0)` call

---

## Step 5: Iteration workflow

When the user asks to modify the deck:

1. Before making changes, offer to save the current version.
2. Make the requested changes to the working copy.
3. If the server is running, the user just refreshes the browser to see
   changes. If not, restart the server.
4. After significant milestones, proactively suggest: "Want me to save
   this version before we continue?"

### Common iteration requests and how to handle them

| Request | Action |
|---------|--------|
| "Make text/images bigger" | Increase font sizes, increase `max-height` on images |
| "Swap slides X and Y" | Move the `<div class="s">` blocks, renumber `data-idx` |
| "Add a new slide after X" | Insert new slide, renumber all subsequent `data-idx` |
| "Change the theme" | Update `:root` custom properties and component colors |
| "Export to Google Slides" | Take screenshots with `xvfb-run` + headless Chrome at 2x resolution, crop bottom strip, use `gslides` CLI to create presentation with correct EMU sizing |

### Google Slides export (detailed)

Converting an HTML deck to Google Slides involves screenshotting each
slide at retina resolution and inserting them as full-bleed images. This
produces a pixel-perfect Google Slides deck that preserves all the visual
design from the HTML version.

#### Step A: Prepare the HTML for screenshotting

Create temporary per-slide HTML files in the **same directory as the
original deck** (so image paths resolve). For each slide:

1. Inject CSS to hide all UI chrome:
   ```css
   nav,.progress,.counter,.notes-panel,.home-btn {
     display:none!important;height:0!important;
     width:0!important;overflow:hidden!important
   }
   body::before,body::after{display:none!important}
   ```
2. Change the `show(0)` call to `show(N)` (where N = slide index).
3. Save as a temporary file (delete after screenshotting).

#### Step B: Take retina screenshots

Use headless Chrome via `xvfb-run` at 2× device scale:

```bash
xvfb-run --auto-servernum \
  --server-args="-screen 0 2560x1440x24" \
  google-chrome-stable \
    --headless=new --no-sandbox --disable-gpu \
    --window-size=1280,720 \
    --force-device-scale-factor=2 \
    --force-color-profile=srgb \
    --screenshot=slide_00.png \
    --hide-scrollbars \
    --run-all-compositor-stages-before-draw \
    --virtual-time-budget=5000 \
    "file:///path/to/temp.html"
```

Key settings:
- **Viewport `1280×720`** with **`--force-device-scale-factor=2`**
  produces a 2560×1440 image (exactly 16:9). Text appears proportionally
  large and readable.
- **`--force-color-profile=srgb`** ensures colors match the browser.
- **`--virtual-time-budget=5000`** gives JavaScript 5 seconds of
  simulated time to render (important for animations/transitions).
- **`--run-all-compositor-stages-before-draw`** forces a complete render
  before screenshotting.

> **Why 1280×720 and not 1920×1080?** At 1920×1080 with 2× scaling, the
> output is 3840×2160 — but text appears very small relative to the
> slide. The 1280×720 viewport makes text fill more of the frame, which
> looks better when projected on a large screen in Google Slides.

#### Step C: Crop the bottom strip

The progress bar and navigation area leave a thin strip at the bottom of
each screenshot, even when hidden via CSS (the fixed elements still
reserve layout space). Remove it by cropping:

```bash
convert slide_raw.png \
  -gravity South -chop 0x40 \
  -resize 2560x1440! \
  slide_final.png
```

This crops 40 pixels from the bottom and resizes back to exact 2560×1440
(16:9). The slight vertical stretch is imperceptible and eliminates the
strip cleanly.

#### Step D: Create the Google Slides presentation

Use the `gslides` CLI (see the gslides skill for full reference):

```bash
GSLIDES=/google/bin/releases/gemini-agents-gslides/gslides

# Create presentation
$GSLIDES create --title "Your Deck Title"

# Add blank slides (N-1 since the first slide already exists)
for i in $(seq 1 $((SLIDE_COUNT - 1))); do
  $GSLIDES add-slide "$PRES_ID"
done

# Get slide IDs
$GSLIDES list-slides "$PRES_ID" --json
```

#### Step E: Populate each slide with the screenshot

For each slide, the process is:

1. **Delete all default elements** (title/body placeholders):
   ```bash
   $GSLIDES get-page "$PRES_ID" "$SLIDE_ID" --json
   # For each element: $GSLIDES delete-element "$PRES_ID" "$ELEMENT_ID"
   ```

2. **Insert the screenshot image**:
   ```bash
   $GSLIDES insert-image-from-file "$PRES_ID" \
     --slide "$SLIDE_ID" --file slide_00.png
   ```

3. **Move to origin and resize to fill the slide**:

   The `gslides` `resize-element` command uses **scale factors**, not
   absolute dimensions. The image inserts at a tiny base size (typically
   32000×18000 EMU). You must calculate scale factors to reach the full
   slide dimensions:

   ```
   Slide width  = 9,144,000 EMU  (10 inches × 914,400 EMU/inch)
   Slide height = 5,143,500 EMU  (5.625 inches × 914,400 EMU/inch)
   ```

   ```python
   # Get the element's base size from get-page JSON
   base_w = element["size"]["width"]["magnitude"]   # e.g., 32000
   base_h = element["size"]["height"]["magnitude"]  # e.g., 18000
   scale_x = 9144000 / base_w  # e.g., 285.75
   scale_y = 5143500 / base_h  # e.g., 285.75
   ```

   ```bash
   $GSLIDES move-element "$PRES_ID" "$ELEM_ID" --x 0 --y 0
   $GSLIDES resize-element "$PRES_ID" "$ELEM_ID" \
     --width "$SCALE_X" --height "$SCALE_Y"
   ```

   > **Critical**: Do NOT pass absolute pixel or point dimensions to
   > `resize-element`. The values are **multiplied** against the base
   > size. Passing `720` and `405` would make the image 720× larger
   > than its base — massively oversized and cropped.

4. **Set speaker notes**:
   ```bash
   $GSLIDES set-notes "$PRES_ID" \
     --slide "$SLIDE_ID" --text "Speaker notes here..."
   ```

#### Step F: Handle transient API failures

The Google Slides API frequently returns `Error 400: There was a problem
retrieving the image` for `createImage` calls. These are **transient**
— the same call usually succeeds on retry.

Build retry logic into your pipeline:
- Track which slide indices failed.
- After completing the first pass through all slides, wait 2 seconds,
  then retry all failures.
- If any still fail after the first retry, retry again.
- In practice, 1-2 retries resolves all failures.

#### Complete pipeline summary

```
Screenshot → Crop → Create Deck → Add Slides → For Each Slide:
  Delete Elements → Insert Image → Move(0,0) → Resize(scale) → Set Notes
  → Retry failures
```

A 30-slide deck takes approximately 15-20 minutes end-to-end
(~3 seconds per screenshot + ~30 seconds per slide API calls).

---

## Step 6: Hosting HTML Decks

Once the deck is ready for sharing with other Googlers (e.g., during a
live presentation or for async review), you can host the HTML file on
Google infrastructure.

### Option 1: Zipline (Recommended for presentations)

Zipline (`go/zipline-user-guide`) is designed for hosting zipped static
web content (HTML/CSS/JS). It's ideal for slide decks because:

- Upload a zip of your deck directory (HTML + images) and get a unique URL
- Supports sharing with **external users** for research purposes
- No ongoing maintenance — just upload and share

Steps:
1. Zip the deck directory containing the HTML file and all image assets
2. Upload to Zipline via the web UI
3. Share the generated URL with attendees

### Option 2: x20 (Classic static hosting)

x20 (`go/x20`) is Google's internal versioned filesystem for static
file hosting:

- URL format: `https://<username>.users.x20web.corp.google.com/path/`
- Deploy by copying files to `/google/data/rw` on gLinux or via the
  x20 web UI
- Set permissions to "Public for Google FTEs" for internal access
- Use a `/teams` directory for shared content (recommended over
  personal `/users` directory)
- See: `go/host-static-internal-website` for detailed setup

### Option 3: Source-based hosting

Since decks are typically checked into
`google3/experimental/users/<ldap>/`, they can also be referenced via
Code Search links — though this shows source code, not a rendered page.

### Recommendation

For presenting live to an audience, **Zipline** is the fastest path:
zip your `training/` directory (or wherever the deck lives), upload,
and share the link in the meeting chat. Attendees can follow along on
their own screens.

---

## Do not forget

- [ ] Every slide has `data-notes` with conversational speaker notes
- [ ] Navigation: home button, prev/next, progress bar, counter
- [ ] Keyboard: arrows, space, N (notes), P (presenter)
- [ ] Presenter view with timer, notes, next slide preview, sync
- [ ] HTTP server started and URL provided to user
- [ ] Images are large (65-70vh), high quality, not placeholders
- [ ] Theme tokens defined in `:root`, not hardcoded colors
- [ ] Single HTML file (except images)
- [ ] Version saved before significant edits
- [ ] Google Slides export: use 1280×720 viewport + 2× scale, crop 40px
  from bottom, resize with EMU scale factors (not absolute sizes)
