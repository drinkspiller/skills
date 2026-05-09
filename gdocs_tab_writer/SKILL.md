---
name: gdocs-tab-writer
description: >-
  Write structured content to a specific tab in a Google Doc using the gdocs
  batch CLI. Use when asked to write, append, or update content in a Google Doc
  tab, paste content into a doc, or populate an empty doc tab with
  formatted content.
---

# gdocs-tab-writer

Write structured, formatted content to a **specific tab** in a Google Doc.

## Why This Skill Exists

Most `gdocs` write commands (`write`, `import-md --update`) do NOT support the
`--tab` flag. The only reliable way to write to a specific tab is:

```bash
GDOCS=/google/bin/releases/gemini-agents-gdocs/gdocs
$GDOCS batch DOC_ID -f batch.json --tab TAB_ID
```

## Quick Reference

### Step 1: Find the tab ID

```bash
$GDOCS list-tabs DOC_ID
```

### Step 2: Build a batch JSON file

Every object MUST have an `"op"` field. The `"level"` field on headings MUST be
a **string**, not a number.

```json
[
  {"op": "heading", "text": "My Title", "level": "1"},
  {"op": "append", "text": "\nSome body text.\n"},
  {"op": "heading", "text": "Section", "level": "2"},
  {"op": "append", "text": "\nMore content here.\n"},
  {"op": "bullet-list", "text": "First point"},
  {"op": "bullet-list", "text": "Second point"},
  {"op": "numbered-list", "text": "Step one"},
  {"op": "numbered-list", "text": "Step two"},
  {"op": "insert-table", "table_data": [["Col A", "Col B"], ["val1", "val2"]], "table_header_bg_color": "#e8f0fe", "table_header_bold": true}
]
```

### Step 3: Execute the batch

```bash
$GDOCS batch DOC_ID -f /path/to/batch.json --tab TAB_ID
```

To replace all existing content in the tab:

```bash
$GDOCS batch DOC_ID -f /path/to/batch.json --tab TAB_ID --replace-all
```

## Gotchas (Things That Do NOT Work)

| Approach                            | Why It Fails                          |
| ----------------------------------- | ------------------------------------- |
| `import-md --update DOC_ID --tab    | `--tab` flag not supported            |
: TAB_ID`                             :                                       :
| `write DOC_ID --file f.md --tab     | `--tab` flag not supported            |
: TAB_ID`                             :                                       :
| `append DOC_ID "text" --tab TAB_ID` | Works but text is an inline arg — too |
:                                     : short for large content               :
| `codemind replace_paragraph` MCP    | Can't find markdown comment markers   |
: tool                                : (invisible in Docs)                   :
| Batch JSON with `"level": 1`        | Parser error — must be `"level": "1"` |
: (number)                            : (string)                              :
| Batch JSON without `"op"` field     | `unknown batch op ""` error           |

## Available Ops

| Op                | Required Fields | Description                      |
| ----------------- | --------------- | -------------------------------- |
| `heading`         | `text`, `level` | Heading (level "1"-"6", "TITLE", |
:                   :                 : "SUBTITLE")                      :
| `append`          | `text`          | Append styled text paragraph     |
| `bullet-list`     | `text`          | Bullet list item                 |
| `numbered-list`   | `text`          | Numbered list item               |
| `insert-table`    | `table_data`    | Table with optional styling      |
| `horizontal-rule` | —               | Visual separator                 |
| `rich-text`       | `runs`          | Multi-style paragraph            |
| `link`            | `text`, `url`   | Hyperlinked text                 |

All ops support optional styling: `bold`, `italic`, `font_family`, `font_size`,
`text_color`, `alignment`, `paragraph_bg_color`.

## Full Workflow Example

```bash
GDOCS=/google/bin/releases/gemini-agents-gdocs/gdocs
DOC_ID="1GwoW3rTCg0_tuW5VWK7bKUJ0o3s5M7pqYWF7Yb4flZw"

# 1. List tabs to find the target
$GDOCS list-tabs $DOC_ID

# 2. Save batch JSON to a scratch file
# (use write_to_file to create /path/to/batch.json)

# 3. Write to the tab
$GDOCS batch $DOC_ID -f /path/to/batch.json --tab t.8mtzp4dajt86

# 4. Verify
$GDOCS read $DOC_ID --tab t.8mtzp4dajt86
```
