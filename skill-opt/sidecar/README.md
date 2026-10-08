# SkillOpt Sleep Sidecar

Automated nightly skill optimization daemon for [Antigravity](https://antigravity.google) and AI agent environments.

## Overview

SkillOpt Sleep runs silently overnight (default: `0 2 * * *` / 2:00 AM) to keep your agent skills continuously aligned with real developer habits:

1. **Friction Harvesting**: Scans recent session logs (Antigravity, Claude Code, Cursor) for tool execution errors and developer pushback/corrections.
2. **`/zoom-out` Problem Synthesis**: Summarizes failure modes into plain-English bullets paired with concrete example sub-bullets using `gemini-flash-latest`.
3. **Validation-Gated Optimization (With Feedback Boundary)**: Evaluates candidate skill edits concurrently (`ThreadPoolExecutor(max_workers=5)`) with top-level `system_instruction` separation, sanitized `optimizer_feedback` (preventing literal test string leakage), and whitespace-normalized token diff clipping ($\le 35\%$).
4. **Adaptive Delivery**:
   - If the skill lives in a Git repository: creates a dedicated branch (`skillopt/<skill>-<date>`) and opens a draft GitHub Pull Request (`gh pr create --draft`) with a `<350`-word `/zoom-out` summary and scorecard table.
   - If outside Git: stages the optimized files and report in `~/.skillopt/staging/<skill>/`.

---

## Installation & Setup

### 1. Link Sidecar to Antigravity

Copy or symlink this directory to your global Antigravity sidecars directory:

```bash
mkdir -p ~/.gemini/config/sidecars
ln -s "$(pwd)" ~/.gemini/config/sidecars/skillopt_sleep
```

### 2. Enable in Antigravity Configuration

Add the sidecar to your `~/.gemini/config/config.json`:

```json
{
  "sidecars": {
    "skillopt_sleep": {
      "enabled": true
    }
  }
}
```

### 3. Environment Variables

Ensure your API key is available in your environment (`~/.bashrc` or `~/.zshrc`):

```bash
export GEMINI_API_KEY="your-gemini-api-key"
# Optional alternatives:
# export ANTHROPIC_API_KEY="your-anthropic-key"
# export OPENAI_API_KEY="your-openai-key"
```

If you use GitHub Pull Request creation, ensure `gh auth status` is authenticated.

---

## Manual Execution (Standalone)

Run the optimizer directly at any time using `run`, `dry-run`, or `harvest` sub-modes and optional `--preferences`:

```bash
python3 runner.py --top_k 3 --lookback_hours 48 --mode run --preferences "Keep under 200 lines"
python3 runner.py --mode dry-run
python3 runner.py --mode harvest
```
