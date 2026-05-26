---
name: cli-output-hierarchy
description: >-
  Enforces a systematic color and weight hierarchy in CLI script output.
  Use when creating or editing bash/shell scripts that produce terminal
  output — covers labels, values, status, warnings, errors, progress,
  and interactive prompts. Handles ambiguous cases with a decision tree.
---

# CLI Output Hierarchy

## When to Use

Apply this system whenever you create or edit a shell script that produces
terminal output. Triggers:

- "create a deploy script"
- "add CLI output / logging"
- "make the output clearer"
- "fix the colors in this script"
- editing any `.sh` file that uses `echo -e` with ANSI codes

---

## The System

Six roles, no overlap. Every piece of terminal text gets exactly one:

| Role | Code | ANSI | When to use |
| :--- | :--- | :--- | :---------- |
| **Structure** | `${BOLD}` | `\033[1m` | Labels (`Mode:`, `Branch:`), headings, section dividers, menu option numbers |
| **Secondary** | `${DIM}` | `\033[2m` | Explanatory text, descriptions, step details, config file names, anything the user can skip-read |
| **Actionable** | `${CYAN}` | `\033[0;36m` | URLs, shell commands to copy, version strings, file paths the user might click/paste |
| **Safe** | `${GREEN}` | `\033[0;32m` | Success states (`✅`), positive confirmations, "included", "enabled", "complete" |
| **Caution** | `${YELLOW}` | `\033[0;33m` | Non-destructive warnings, attention-needed, "no change", "stripped", "skipped", "--no-promote" |
| **Danger** | `${RED}${BOLD}` | `\033[0;31m\033[1m` | Errors, emergency gates, destructive confirmations, permission failures. **Never for informational content.** |

### Reset

Always reset after every colored span: `${RESET}` (`\033[0m`).

---

## Boilerplate

Every script that produces colored output must declare the palette at the
top, with the role comment block:

```bash
# ── Color System ────────────────────────────────────────────────────
#   BOLD     = structural labels, headings, emphasis
#   DIM      = secondary/explanatory text
#   CYAN     = actionable values (URLs, commands, version names)
#   GREEN    = safe/positive states (success, enabled, included)
#   YELLOW   = caution, attention-needed (warnings, skipped, stripped)
#   RED BOLD = danger only (errors, emergency gates, destructive actions)
# ────────────────────────────────────────────────────────────────────
BOLD='\033[1m'
DIM='\033[2m'
CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
RESET='\033[0m'
```

**Do not** define one-off color variables like `ORANGE` or `BLUE`. If the
six roles don't cover your case, the output design needs rethinking, not
more colors.

---

## Decision Tree for Ambiguous Cases

When you're unsure which role applies, walk this tree:

```
Is the user expected to COPY or CLICK this text?
  └─ Yes → CYAN (actionable)

Is this an ERROR or could it cause DATA LOSS?
  └─ Yes → RED BOLD (danger)

Does the user need to NOTICE this but it's not an error?
  └─ Yes → Is it positive/safe?
       └─ Yes → GREEN (safe)
       └─ No  → YELLOW (caution)

Is this a LABEL or HEADING that structures the output?
  └─ Yes → BOLD (structure)

Is this EXPLANATORY text the user can skip?
  └─ Yes → DIM (secondary)

None of the above?
  └─ Use RESET (plain text, no color)
```

### Common Ambiguous Cases

| Scenario | Tempting choice | Correct choice | Why |
| :------- | :-------------- | :------------- | :-- |
| Version string in a heading | BOLD | CYAN | It's an actionable value, not structure |
| "STRIPPED" for prod builds | RED | YELLOW | It's expected behavior, not an error |
| "INCLUDED" for staging | CYAN | GREEN | It's a positive state, not something to copy |
| Step counter `[1/5]` | BOLD | DIM | It's secondary structural info, not a label |
| Config filename `app.yaml` | CYAN | DIM | Not actionable — the user won't copy it |
| `--no-promote` in prose | BOLD | BOLD | Correct — it's emphasis within a sentence |
| `--no-promote` in a command | BOLD | CYAN | Part of a copyable command |
| "Type DEPLOY to proceed" | YELLOW | RED BOLD | It gates a destructive/irreversible action |
| "No tests found" | RED | YELLOW | Unexpected but not an error |
| "Build failed" | YELLOW | RED BOLD | It's an error — the script should exit |

---

## Patterns

### Progress Steps

Use `DIM` counters, `CYAN` for the key value, `GREEN` for completion:

```bash
echo -e "${DIM}[1/3]${RESET} Building ${CYAN}staging${RESET} variant..."
# ... work ...
echo -e "${GREEN}✅ Build complete${RESET}"
```

### Interactive Menu

`BOLD` for option numbers, `DIM` for descriptions, `CYAN` for values,
`GREEN`/`YELLOW` for state:

```bash
echo -e "  ${BOLD}1)${RESET} staging"
echo -e "     ${DIM}Gated feature code${RESET} ${GREEN}INCLUDED${RESET}"
echo -e "     ${DIM}Version:${RESET}  ${CYAN}manual-staging-abc1234${RESET}"
echo -e "     ${DIM}Config:${RESET}   ${DIM}app.staging.yaml${RESET}"
```

### Confirmation Plan

`BOLD` labels, `CYAN` values, `YELLOW` for caution callouts, `DIM` for
step details:

```bash
echo -e "  ${BOLD}Mode:${RESET}     ${CYAN}prod${RESET}"
echo -e "  ${BOLD}Version:${RESET}  ${CYAN}manual-prod-abc1234${RESET}"
echo -e "  ${BOLD}WIP code:${RESET} ${YELLOW}STRIPPED${RESET} ${DIM}(production tree-shake)${RESET}"
echo ""
echo -e "  ${YELLOW}Traffic:${RESET} ${YELLOW}NO CHANGE${RESET} — deployed with ${BOLD}--no-promote${RESET}."
echo -e "          ${DIM}The new version will not receive traffic.${RESET}"
```

### Error with Remediation

`RED BOLD` for the error, `DIM` for context, `CYAN` for the fix command:

```bash
echo -e "${RED}${BOLD}ERROR:${RESET} ${RED}Missing service account permission${RESET}"
echo -e "${DIM}You need 'Service Account User' on the GAE SA.${RESET}"
echo ""
echo -e "${DIM}Run this to fix:${RESET}"
echo -e "${CYAN}gcloud iam service-accounts add-iam-policy-binding \\${RESET}"
echo -e "${CYAN}  myapp@appspot.gserviceaccount.com \\${RESET}"
echo -e "${CYAN}  --member=\"user:you@google.com\" \\${RESET}"
echo -e "${CYAN}  --role=\"roles/iam.serviceAccountUser\"${RESET}"
```

### Success Result

`GREEN BOLD` for the header, `BOLD` labels, `CYAN` for actionable URLs:

```bash
echo -e "${GREEN}${BOLD}═══════════════════════════════════════════${RESET}"
echo -e "${GREEN}${BOLD} Deploy Complete${RESET}"
echo -e "${GREEN}${BOLD}═══════════════════════════════════════════${RESET}"
echo ""
echo -e "  ${BOLD}Version:${RESET}  ${CYAN}manual-prod-abc1234${RESET}"
echo -e "  ${BOLD}URL:${RESET}      ${CYAN}https://manual-prod-abc1234-dot-myapp.appspot.com${RESET}"
```

### Danger Gate

`RED BOLD` for the warning block and confirmation prompt:

```bash
echo -e "${RED}${BOLD}⚠  This action cannot be undone.${RESET}"
echo -n "Type DELETE to confirm: "
```

---

## Anti-Patterns

1. **Rainbow output** — Using all six roles in a single line. Each line
   should use 1–2 roles max (label + value).

2. **RED for emphasis** — RED is danger. If you want emphasis, use BOLD.
   If you want attention, use YELLOW.

3. **BOLD everything** — If everything is bold, nothing is. Reserve for
   labels and headings only.

4. **Naked colors without RESET** — Always close the span. Leaking color
   into subsequent lines breaks the hierarchy.

5. **Box-drawing with colors** — `╔═══╗` borders fight with the color
   system. Use simple `═══` dividers with a role color (e.g., `GREEN BOLD`
   for success headers, `BOLD` for section dividers).

6. **Inventing new colors** — Magenta, blue, white-on-red backgrounds.
   Six roles is the maximum. More colors = more cognitive load = less
   hierarchy.
