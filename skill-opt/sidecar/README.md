# SkillOpt Sleep Sidecar

Automated nightly skill optimization daemon for [Antigravity](https://antigravity.google) and AI agent environments.

## Overview

SkillOpt Sleep runs silently overnight (default: `0 2 * * *` / 2:00 AM) to keep your agent skills continuously aligned with real developer habits:

1. **Friction Harvesting**: Scans recent session logs (Antigravity, Claude Code, Cursor) for tool execution errors and developer pushback/corrections.
2. **Intelligent Problem Synthesis**: Summarizes failure modes into clear, high-level bullets paired with concrete example sub-bullets using an LLM.
3. **Validation-Gated Optimization**: Evaluates candidate skill edits against train and held-out validation tasks with edit-distance clipping ($\le 35\%$) and semantic checks.
4. **Adaptive Delivery**:
   - If the skill lives in a Git repository: creates a dedicated branch (`skillopt/<skill>-<date>`) and opens a draft GitHub Pull Request (`gh pr create --draft`).
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

You can run the optimizer directly at any time without waiting for the nightly cron:

```bash
python3 runner.py --top_k 3 --lookback_hours 48
```
