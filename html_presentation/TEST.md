# HTML Presentation — Test Plan

## Trigger Tests

### T1: Create a deck
**Prompt:** "Create a slide deck about our Q1 research findings"
**Expected:** Skill activates. Asks about theme preference before generating slides. Includes all infrastructure (nav, notes, presenter view, hosting).

### T2: Theme selection
**Prompt:** "I want to make a presentation. Help me pick a visual style."
**Expected:** Presents Organic Modern and Blueprint as options, offers to build a custom theme.

### T3: Update existing deck
**Prompt:** "Add three more slides to the deck about methodology"
**Expected:** Offers to save current version before editing. Adds slides with correct `data-idx` numbering.

## Output Quality Tests

### Q1: Required infrastructure
**Check:** Output includes: keyboard navigation (arrows, N, P), home button, progress bar, counter, notes panel, presenter view with BroadcastChannel, HTTP server started.

### Q2: Theme tokens
**Check:** All colors defined as CSS custom properties in `:root`, not hardcoded throughout.

### Q3: Speaker notes
**Check:** Every slide has a `data-notes` attribute with conversational notes.

### Q4: Image sizing
**Check:** Images use `max-height: 65vh` or larger with `object-fit: contain`.

### Q5: Single file
**Check:** All HTML, CSS, and JS in one file. Only external deps are Google Fonts and local images.

### Q6: Version management
**Check:** When modifying an existing deck, asks about saving current version first.

## Non-Trigger Tests

### N1: Writing a document
**Prompt:** "Write a research plan for a usability study"
**Expected:** This skill should NOT activate.

### N2: Creating a survey
**Prompt:** "Build a Qualtrics survey"
**Expected:** This skill should NOT activate.
