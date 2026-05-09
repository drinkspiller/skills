---
name: cli-design
description: >
  Best practices for designing command-line interfaces (CLIs). Use when
  creating, reviewing, or improving CLI tools — covers command structure,
  naming, flags, help text, output formatting, error handling, robustness,
  configuration, and Google-specific CLI conventions.
---

# CLI Design Guide

Principles and patterns for building well-designed CLI tools, synthesized from
industry best practices and Google-internal conventions.

## Philosophy

- **Human-first design.** If a command is used primarily by humans, design for
  humans first. Composability with scripts is secondary.
- **Simple parts that work together.** Use stdout/stderr/exit codes correctly
  so programs compose via pipes. Support `--json` for structured output.
- **Consistency across programs.** Follow existing conventions — don't invent
  new flag names when standard ones exist.
- **Say just enough.** Don't hang silently. Don't dump pages of debug output.
  Show progress, confirm state changes, and keep noise low.
- **Ease of discovery.** Comprehensive help, examples, and "next step"
  suggestions make CLIs learnable without external docs.

## Command Structure

### Naming

- Command and subcommand names should be **lowercase, single words** where
  possible. Use kebab-case (`my-command`) if multiple words are unavoidable.
- **Topics are plural nouns, commands are verbs**: `apps create`,
  `containers list`, `config set`.
- Prefer **noun-verb** ordering for multi-level subcommands:
  `docker container create`, `gcloud compute instances list`.

### Subcommands

- Use subcommands to reduce complexity of tools with many operations.
- Be consistent across subcommands — same flag names, similar output formats.
- **Don't have ambiguous commands** like "update" and "upgrade".
- **Don't allow arbitrary abbreviations** — they prevent adding new commands.
- **Don't have a catch-all subcommand** — it blocks future expansion.

## Arguments & Flags

### Prefer Flags to Args

Flags are self-documenting and order-independent. Positional args are OK only
for simple, unambiguous primary actions (e.g., `rm file.txt`, `cd dir`).

```
# Bad — which is source, which is destination?
mycli deploy production jira

# Good — self-documenting
mycli deploy --environment=production --product=jira
```

### Flag Conventions

- **Always provide long-form flags** (`--help`, not just `-h`).
- **Reserve short flags** for the most common options only.
- Use **standard flag names** when they exist:

| Flag | Meaning |
|------|---------|
| `-h`, `--help` | Show help (never overload) |
| `--version` | Show version |
| `-q`, `--quiet` | Suppress non-essential output |
| `-v`, `--verbose` | Increase output detail |
| `-f`, `--force` | Skip confirmations |
| `-n`, `--dry-run` | Preview without executing |
| `-o`, `--output` | Output file or format |
| `--json` | Output as formatted JSON |
| `--no-color` | Disable color output |
| `--no-input` | Disable interactive prompts |

- Use `--no-` prefix for boolean negations (`--reboot` / `--no-reboot`).
- **Never read secrets from flags** — use `--password-file` or stdin instead.

## Help & Documentation

### Help Text

- Display help for `-h`, `--help`, and (for git-like tools) `help` subcommand.
- When run without required arguments, show **concise** help: description,
  one–two examples, common flags, and a pointer to `--help`.
- Show **full help** with all flags when `--help` is passed.
- Lead with **examples** — users prefer them over prose.
- Show **most common commands first**, then group the rest.

### Suggesting Next Steps

After each command completes, suggest what the user might do next:

```
✓ App created successfully.
  Next: deploy with `mycli deploy --app=myapp`
```

## Output Design

### Stdout vs Stderr

- **stdout**: Primary output and machine-readable data.
- **stderr**: Log messages, progress, errors, and diagnostics.

### Human-Readable First

- Detect TTY to decide output format: rich for terminals, plain for pipes.
- Support `--plain` for grep/awk-compatible tabular output.
- Support `--json` for structured, parseable output.
- If state changes, **tell the user** what happened and what the new state is.

### Color

Use color to aid scanning, not as decoration:

- **Red**: errors. **Yellow**: warnings. Other colors: structure/emphasis.
- Disable color when: not a TTY, `NO_COLOR` is set, `TERM=dumb`, or
  `--no-color` is passed.
- Don't overuse — if everything is colored, nothing stands out.

### Progress

- Print something within **100ms** so the user knows it's working.
- Use spinners or progress bars for long operations.
- Break long tasks into **visible steps** with status for each.

## Error Handling

- **Rewrite errors for humans.** Don't dump raw stack traces or internal codes.
- Explain **what went wrong** and **how to fix it**:
  `Can't write to file.txt. Try: chmod +w file.txt`
- Put the most important information **at the end** — that's where eyes go.
- Use **non-zero exit codes** for failures. Map codes to distinct failure modes.
- For unexpected errors, offer a way to **submit a bug report** with
  pre-populated context.

## Robustness

- **Validate input early** and fail with clear messages before side effects.
- **Make operations idempotent** — rerunning should be safe.
- **Set network timeouts** with sensible defaults.
- **Make it recoverable** — pressing ↑ Enter should pick up where it left off.
- **Handle Ctrl-C gracefully** — clean up or exit immediately.
- **Make it crash-only** — if you can defer cleanup to the next run, do so.

## Configuration Hierarchy

Configuration should layer, with more specific sources overriding general ones:

| Priority | Source | Use For |
|----------|--------|---------|
| 1 (highest) | Flags | Per-invocation settings |
| 2 | Environment variables | Per-session or machine-specific settings |
| 3 | Project config file | Shared, version-controlled project settings |
| 4 | User config file | Personal defaults (`~/.config/myapp/`) |

- Follow the **XDG Base Directory spec** (`~/.config`, `~/.cache`, etc.).
- Read from `.env` files where appropriate, but don't use them as a substitute
  for proper config files.
- **Never read secrets from environment variables** — they leak into logs,
  `ps` output, and child processes.
- Check standard env vars: `NO_COLOR`, `DEBUG`, `EDITOR`, `PAGER`, `TMPDIR`,
  `HTTP_PROXY`, `HOME`, `TERM`.

## Future-proofing

- **Keep changes additive.** Add new flags rather than changing existing ones.
- **Warn before breaking changes.** Deprecate flags with in-tool warnings and
  migration instructions before removing them.
- **Don't create time bombs.** Avoid hard dependencies on external services
  that may disappear.
- Changing human-readable output is OK — encourage `--json` in scripts for
  stability.

## Google-Specific Patterns

For deeper Google-internal guidance, see
[references/google_cli_patterns.md](references/google_cli_patterns.md).

Key highlights:

- **Deployment**: Use BinFS (`go/binfs`) for automated deployment to
  `/google/bin/releases`. Don't require users to `blaze build` manually.
- **Documentation**: Create a `go/${TOOL_NAME}` link pointing to your docs.
- **Defaults**: Make the tool work with minimal flags. Don't assume the
  current working directory is the google3 root — infer it.
- **Flag consistency**: Use the same flag names as peer tools in your
  ecosystem (e.g., `--detach`, `-c` for CL number).
- **Dangerous operations**: Default to `--dry_run=true` for destructive
  commands. Force explicit specification of targets like
  `--spanner_database`.
- **Readable invocations**: Make commands read like sentences:
  `diffle -c cl/123 --for server --against embedded`.
- **CLI frameworks**: Use absl.flags (C++/Python), Cobra (Go), picocli
  (Java), or clikt (Kotlin). See `go/go-style/best-practices#complex-clis`.

## Reporting Issues

Report bugs or improvements for this skill at [Agent Skill: cli_design](http://b/hotlists/8078276).
See the `skill_issue` skill for instructions on filing and triaging skill bugs.
