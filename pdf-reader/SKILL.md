---
name: pdf-reader
description: >
  Read PDF documents from URLs or local paths. Use when asked to
  read, summarize, or analyze a PDF, paper, or document link.
  Extracts page-annotated text and renders pages as images for
  visual understanding of diagrams, figures, and equations.
---

# PDF Reader

Read PDFs with full text extraction and page rendering for diagrams/figures.

## CLI

Prefer using the pre-built binary (available on all gLinux machines):

```bash
PDF_READER=/google/bin/releases/gemini-agents-pdf-reader/read_pdf_cli.par
```

Alternatively, install via apt (the `read_pdf_cli.par` binary will be available directly on PATH):

```bash
sudo glinux-add-repo -b gemini-agents-pdf-reader stable
sudo apt update && sudo apt install -y gemini-agents-pdf-reader
```

Use `--version` to check the build date. To verify the exact
build CL: `binfs ls /google/bin/releases/gemini-agents-pdf-reader`.

If you modify the CLI source code, build from source:

```bash
blaze build //learning/gemini/agents/clis/pdf_reader:read_pdf_cli
PDF_READER=blaze-bin/learning/gemini/agents/clis/pdf_reader/read_pdf_cli
```

```bash
$PDF_READER \
  --url=URL \
  --output_dir=DIR \
  --output_file=FILE
```

The script outputs page-annotated text and renders each page as a PNG image.
After running, use `view_file` on the rendered page images to inspect diagrams.

## Library

```python
from google3.learning.gemini.agents.clis.pdf_reader import read_pdf_lib

text = read_pdf_lib.extract_text('/path/to/doc.pdf')
pages = read_pdf_lib.render_pages('/path/to/doc.pdf', '/tmp/output')
output = read_pdf_lib.read_pdf('/path/to/doc.pdf', output_dir='/tmp/output')
```

## Workflow

1. Run `read_pdf_cli` with `--url` or `--file` and `--output_dir` for page images
2. Read the text output for content understanding
3. Use `view_file` on specific page PNGs listed under `RENDERED PAGES` for
   diagrams, figures, or equations

## Flags

| Flag | Description |
|------|-------------|
| `--url` | URL to download PDF from |
| `--file` | Local path to PDF file |
| `--pages` | Page range (e.g. `1-5,10,15-20`). Default: all |
| `--output_dir` | Directory for rendered page PNGs |
| `--output_file` | Write text output to file instead of stdout |
| `--dpi` | Render resolution (default: 200) |
| `--text_only` | Skip page rendering |
| `--render_only` | Skip text extraction |

## Reporting Issues

Report bugs or improvements for this skill at [Agent Skill: pdf-reader](http://b/hotlists/8078599).
See the `skill_issue` skill for instructions on filing and triaging skill bugs.
