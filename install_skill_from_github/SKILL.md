---
name: install-skill-from-github
description: >
  Install and convert GitHub-hosted AI agent skills (Claude Code, Anthropic,
  community) into Gemini format. Use when the user asks to install a skill
  from GitHub, convert a .claude skill, port a Claude Code skill, or add an
  external skill to their Gemini configuration.
---

# Install Skill from GitHub

Fetches, converts, and installs skills from GitHub repositories into Gemini
format under `configs/users/<username>/_agents/skills/`.

## Quick Reference

```
Target path:  configs/users/<username>/_agents/skills/<skill_name>/SKILL.md
              (configs/ is a SIBLING of google3/, not inside it)
```

## Step 1 — Fetch the Skill

Use the GitHub API or raw URLs to retrieve skill content:

```
# List directory contents
https://api.github.com/repos/{owner}/{repo}/contents/{path}

# Fetch raw file
https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{path}
```

For standalone repos (skill IS the repo), use the root:
`https://api.github.com/repos/{owner}/{repo}/contents/`

## Step 2 — Identify the Source Format

Source Format            | Indicator
------------------------ | -----------------------------------------------------
Claude Code skill        | Has `SKILL.md` with frontmatter, may have `commands/`
Claude project file      | Has `CLAUDE.md` at repo root
Anthropic official skill | Under `anthropics/skills` repo
Community skill          | Standalone repo with `SKILL.md` or `README.md`

## Step 3 — Convert to Gemini Format

### Conversion Rules

| Source Feature             | Gemini Equivalent     | Action                |
| -------------------------- | --------------------- | --------------------- |
| `SKILL.md` with YAML       | **Same**              | Keep as-is; validate  |
: frontmatter (`name`,       :                       : format                :
: `description`)             :                       :                       :
| `README.md` as the skill   | Must be `SKILL.md`    | Rename, add YAML      |
: file                       :                       : frontmatter           :
| `CLAUDE.md` (project       | Not a skill — becomes | Extract relevant      |
: brain)                     : a **rule** or         : instructions          :
:                            : Conductor context     :                       :
| `hooks` / lifecycle events | **Not supported in    | Convert hook logic to |
: (`PreToolUse`,             : Gemini skills**       : explicit instructions :
: `PostToolUse`, etc.)       :                       : in SKILL.md body      :
| Slash commands             | **Not natively        | Convert to trigger    |
: (`/command`)               : supported**           : phrases in the        :
:                            :                       : `description` field   :
| `commands/` directory      | **Not supported**     | Inline command        |
:                            :                       : instructions into     :
:                            :                       : SKILL.md body         :
| `settings.json` / tool     | **Not supported**     | Remove; document as   |
: permissions                :                       : manual config if      :
:                            :                       : critical              :
| `allowed-tools`            | **Not supported**     | Remove                |
: frontmatter field          :                       :                       :
| `disable-model-invocation` | **Not supported**     | Remove                |
: frontmatter                :                       :                       :
| `context: fork`            | **Not supported**     | Remove; note in       |
: frontmatter                :                       : SKILL.md if isolation :
:                            :                       : matters               :
| `!command` dynamic         | **Not supported**     | Replace with explicit |
: injection syntax           :                       : script references     :
| `$1`, `$2` positional      | **Not supported**     | Rewrite as natural    |
: arguments                  :                       : language prompts      :
| ADR references             | Replace with          | Update paths and      |
:                            : **Conductor**         : terminology           :
:                            : references            :                       :
| `scripts/` directory       | **Same**              | Copy over             |
| `references/` directory    | **Same**              | Copy over             |
| `examples/` directory      | **Same**              | Copy over             |
| `resources/` or `assets/`  | **Same**              | Copy over             |
| `templates/` directory     | **Same**              | Copy over             |
| `LICENSE.txt`              | Keep if present       | Copy over             |

### Frontmatter Validation

Every `SKILL.md` MUST have:

```yaml
---
name: kebab-case-name        # Max 64 chars, gerund preferred
description: >               # Max 1024 chars, third-person
  What the skill does and when to use it. Include trigger
  keywords users might say.
---
```

### Directory Structure

```
configs/users/<username>/_agents/skills/
└── my_skill/                 # snake_case directory name
    ├── SKILL.md              # Required — entry point
    ├── scripts/              # Optional — executable helpers
    ├── references/           # Optional — supplemental docs
    ├── templates/            # Optional — file templates
    └── resources/            # Optional — static assets
```

## Step 4 — Adapt Content for Google/Gemini Context

### Conductor Adaptation

When a skill references ADRs (Architecture Decision Records), adapt: - "ADR" →
"Conductor track spec / project guidelines" - "architecture decision records" →
"Conductor context (`conductor/` directory)" - `docs/adr/` paths → `conductor/`
directory references - "decision log" → "Conductor track plan"

### Google3 Adaptation

When a skill references external tools, consider Google equivalents: - `git
bisect` → works in Fig/hg too (adapt syntax) - `npm test` / `jest` → `blaze
test` - `curl` → works as-is - File paths → use google3 conventions when
relevant

### Hook Conversion

When a source skill uses hooks, convert them to explicit instructions:

**Before (Claude hook):** `json {"event": "PreToolUse", "tools":
["write_to_file"], "command": "scripts/lint-check.sh"}`

**After (Gemini instruction in SKILL.md):** ```markdown

## Pre-write Checklist

Before writing any file, run `scripts/lint-check.sh` to validate the change. ```

## Step 5 — Write Files

Create the skill directory and files:

```
configs/users/<username>/_agents/skills/<skill_name>/SKILL.md
configs/users/<username>/_agents/skills/<skill_name>/scripts/...
configs/users/<username>/_agents/skills/<skill_name>/references/...
```

> [!IMPORTANT] `configs/` is a **sibling** of `google3/`, not inside it. The
> full path is: `/google/src/cloud/<user>/<workspace>/configs/users/...`

## Step 6 — Verify

-   [ ] SKILL.md has valid YAML frontmatter with `name` and `description`
-   [ ] Directory name is snake_case
-   [ ] `name` field is kebab-case
-   [ ] `description` is third-person, includes trigger keywords
-   [ ] All referenced scripts/files exist
-   [ ] No Claude-specific features left unconverted (hooks, commands, etc.)
-   [ ] Content adapted for Google/Gemini context where relevant
