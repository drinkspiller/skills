# PDF Reader Skill - Agent E2E Test Plan

## Prerequisites

**Read `SKILL.md` first** to understand available commands, flags, and expected
behavior.

Build the CLI:

```bash
blaze build //learning/gemini/agents/clis/pdf_reader:read_pdf_cli
```

Set convenience alias:

```bash
PDF=blaze-bin/learning/gemini/agents/clis/pdf_reader/read_pdf
```

---

## Test 1: CLI builds

```bash
blaze build //learning/gemini/agents/clis/pdf_reader:read_pdf
```

**Verify:** Build succeeds (exit code 0).

---

## Test 2: Help output

```bash
$PDF --help
```

**Verify:**

-   Output lists `--url`, `--file`, `--pages`, `--output_dir` flags
-   Usage information is present

---

## Test 3: Read an academic paper

**Prompt:** "Can you read this paper for me and give me a summary?
https://arxiv.org/pdf/2311.07222"

**Verify:**

-   Output contains page-annotated text with `--- PAGE N ---` markers
-   Text includes recognizable content from the paper (e.g. "NeuralGCM")
-   Rendered page image paths are listed under `--- RENDERED PAGES ---`

---

## Test 4: Inspect a specific figure

**Prompt:** "Can you look at Figure 1 on page 3 of the paper?"

**Verify:**

-   Agent uses `view_file` on the page 3 rendered PNG
-   Agent describes the diagram content (model architecture)

---

## Test 5: Extract specific pages only

**Prompt:** "Just give me pages 28 to 30 from that paper, I want to see the
appendix figures."

**Verify:**

-   Only pages 28-30 are extracted (text and rendered images)
-   Output does not include other pages
-   Rendered PNG files exist only for pages 28-30
