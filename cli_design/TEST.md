# CLI Design Skill - Agent E2E Test Plan

## Prerequisites

**Read `SKILL.md` first** to understand the CLI design principles, patterns, and
Google-specific conventions covered by this skill.

This is a knowledge/best-practices skill with no CLI binary. Tests validate
that the agent can apply the design guidance correctly.

Verify the references directory exists:

```bash
ls learning/gemini/agents/skills/cli_design/references/
```

---

## Test 1: Reference files exist

```bash
ls learning/gemini/agents/skills/cli_design/references/
```

**Verify:** Directory exists and contains `google_cli_patterns.md`.

---

## Test 2: SKILL.md structure

```bash
head -10 learning/gemini/agents/skills/cli_design/SKILL.md
```

**Verify:**

-   File starts with valid YAML frontmatter
-   Description mentions CLI design best practices

---

## Test 3: Review a CLI for design issues

**Prompt:** "I have a CLI tool that takes two positional arguments for source
and destination paths, all output goes to stdout including errors, and there's
no `--help` flag. What design improvements should I make?"

**Verify:**

-   Agent recommends using flags instead of positional args
-   Agent recommends separating stdout and stderr
-   Agent recommends adding `--help` / `-h` support

---

## Test 4: Design a new CLI command structure

**Prompt:** "I'm building a tool to manage Borg jobs. It needs to list jobs,
get job details, restart a job, and show logs. How should I structure the
commands and flags?"

**Verify:**

-   Agent suggests a subcommand structure (noun-verb or verb-noun)
-   Agent recommends consistent flag naming
-   Agent suggests `--help`, `--json`, and `--verbose` flags

---

## Test 5: Apply Google-specific CLI conventions

**Prompt:** "I'm about to deploy a new internal CLI tool. What Google-specific
best practices should I follow for deployment, documentation, and defaults?"

**Verify:**

-   Agent mentions BinFS / `go/binfs` for deployment
-   Agent mentions creating a `go/<tool-name>` link
-   Agent recommends sensible defaults and inferring google3 root
