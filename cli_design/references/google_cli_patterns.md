# Google CLI Patterns

Google-specific CLI conventions and tooling, derived from go/cli-best-practices,
the gcloud CLI style guide, Chromite CLI guidelines, and Fuchsia CLI guidelines.

## CLI Frameworks by Language

| Language | Recommended Framework | Notes |
|----------|----------------------|-------|
| **Go** | Cobra (`//third_party/golang/cobra`) | See go/go-style/best-practices#complex-clis. Use subcommands (go/goocli) for simpler tools |
| **Python** | absl-py (`from absl import flags, app`) | Standard at Google. Use `argparse` only for open-source-bound code |
| **C++** | absl flags + zhu (`go/zhu`) | zhu provides subcommand support on top of absl |
| **Java** | picocli (`go/java-flags/faq#open-source`) | Annotation-driven, supports subcommands |
| **Kotlin** | clikt | Similar to picocli but Kotlin-idiomatic |
| **Bash** | GBash (`go/gbash`) | Provides flag parsing (go/bash-flags), short aliases, and easy defaults |

## Deployment

- **BinFS** (`go/binfs`): Deploy via Rapid to `/google/bin/releases`. Users
  add an alias to their shell profile instead of running `blaze build`.
- **Shell wrappers**: Consider a GBash wrapper around your binary for easy
  short aliases and default flags (see diffle.sh as an example).

## Command Design

### Working Directory

Don't assume the CWD is the google3 root. If a google3 path is needed:
1. Infer it from the current working directory.
2. Fall back to `/google/src/head/depot/google3`.

### Vocabulary

Minimize the vocabulary size. Don't create separate flags for submitted vs
pending CLs — accept both through one flag and resolve internally.

### Readable Invocations

```
# Good: reads like a sentence
diffle -c cl/123456 --for textnorm_server --against textnorm_embedded

# Bad: opaque positional args
diffle 123456 textnorm_server textnorm_embedded
```

### Dangerous Commands

For tools that modify state (Spanner writes, deletions, etc.):

- Default to `--dry_run=true` for destructive operations.
- Force explicit target specification — no defaults for flags like
  `--spanner_database` or `--target_environment`.
- Require confirmation for irreversible actions.

## Flag Conventions

### Consistency with Ecosystem

Reuse flag names from peer tools in the same domain:
- `--detach` for detached execution (guitar, tap_presubmit)
- `-c` for CL number (birdnest, diffle)

### Boolean Flags

Follow Chromite conventions for maximum clarity:
- Provide both `--flag` and `--no-flag` forms.
- Use `--no-` prefix (not `--skip-`, `--disable-`).
- Support stacking: `--wipe --no-wipe` → last wins.

### Long Options

- Use **kebab-case**: `--my-flag` not `--my_flag`.
- Always provide a long-form for every short flag.

## Documentation

- Create a **go/ link**: `go/${TOOL_NAME}` → canonical documentation page.
- Include a `--help` that shows usage, common examples, and flag descriptions.
- Reference go/ links in error messages for detailed troubleshooting.

## Subcommand Structure

Following gcloud and IE CLI patterns:

```
# noun-verb pattern
ie app init
ie app config get_status
ie dataset count

# Organize around domain concepts
gcloud compute instances list
gcloud storage buckets create
```

- Keep nesting to **≤ 2 levels of concepts** to avoid verbosity.
- Separate CLI framework code from business logic — business logic should be
  testable independently via library calls or stubby endpoints.

## Testing

- Unit test business logic in libraries, separate from CLI framework glue.
- Add shell script integration tests to verify commands are wired correctly.
- Test flag parsing and validation, especially when flags interact.

## References

- go/cli-best-practices — Google TTS CLI best practices
- go/cli-principles — clig.dev (external)
- go/gcloud-cli-develop — gcloud contributor development
- go/go-style/best-practices#complex-clis — Go CLI framework guidance
- go/zhu — C++ subcommand library
- go/goocli — Go subcommand library
- go/gbash — Bash CLI framework
- go/binfs — Binary deployment via Rapid
