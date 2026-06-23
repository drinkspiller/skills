---
name: merge-latest
description: >
  Merge the latest upstream changes into the current branch, resolve conflicts,
  and verify builds, tests, and lint. Auto-discovers the VCS (Git, Fig/Hg, JJ)
  and project toolchain from the working directory.
---

# Merge Latest Upstream Changes

// turbo-all

Merge upstream changes into the current branch, resolve any conflicts, then
verify the result builds, tests, and passes lint. End by listing any assumptions
or follow-up items.

## Environment Discovery

1.  **Detect VCS** by checking for `.git/`, `.hg/`, or `.jj/` in the current
    directory or its parents.
    -   If **Git**: proceed with Git steps.
    -   If **Fig/Mercurial**: proceed with Fig steps.
    -   If **JJ (Jujutsu)**: proceed with JJ steps.
    -   If none found, stop and ask the user to navigate to a repository.

2.  **Detect the base branch / upstream target:**
    -   **Git**: Run `gh repo view --json defaultBranchRef --jq
        '.defaultBranchRef.name'` and fall back to `main`. Store as `$BASE`.
    -   **Fig/Hg**: The upstream is the sync target (typically `default` or the
        CitC baseline). No explicit base branch needed — `hg sync` handles it.
    -   **JJ**: The upstream is the trunk bookmark (typically `main@origin`).

3.  **Detect the project toolchain** for verification by checking indicator
    files at the repo root:

    | Indicator file              | Test                    | Lint                     | Build                      |
    | :-------------------------- | :---------------------- | :----------------------- | :------------------------- |
    | `package.json`              | `npm test` / `pnpm test` | `npm run lint` / `pnpm lint` | `npm run build` / `pnpm build` |
    | `Makefile`                  | `make test`             | `make lint`              | `make build`               |
    | `Cargo.toml`                | `cargo test`            | `cargo clippy`           | `cargo build`              |
    | `go.mod`                    | `go test ./...`         | `golangci-lint run`      | `go build ./...`           |
    | `BUILD` / `BUILD.bazel`     | `blaze test` / `bazel test` | `buildifier -lint=warn` | `blaze build` / `bazel build` |
    | `pyproject.toml` / `setup.py` | `pytest`              | `ruff check .`           | *(skip)*                   |

    Prefer `pnpm` over `npm` if `pnpm-lock.yaml` exists. Only run commands
    whose indicator files are present. If none are found, skip verification and
    inform the user.

--------------------------------------------------------------------------------

## Part A — Merge Upstream

### Git

1.  **Fetch origin:**

    ```bash
    git fetch origin "$BASE"
    ```

2.  **Merge into the current branch:**

    ```bash
    git merge "origin/$BASE" --no-edit
    ```

3.  **If merge conflicts occur:**

    -   List conflicted files with `git diff --name-only --diff-filter=U`.
    -   For each conflict, open the file, read the diff markers (`<<<<<<<`,
        `=======`, `>>>>>>>`), and resolve by keeping the intent of both sides.
        Prefer the local (HEAD/ours) side for feature work; prefer upstream
        (theirs) for dependency bumps, lockfile regeneration, and CI config.
    -   After resolving all files, stage and commit:
        `git add -A && git commit --no-edit`.

4.  **Install dependencies (if lockfile changed):**

    Run the appropriate install command from the toolchain table (e.g.,
    `pnpm install`, `cargo fetch`, `go mod download`). Skip if no lockfile was
    modified.

### Fig / Mercurial

1.  **Sync the workspace:**

    ```bash
    hg sync
    ```

2.  **If rebase conflicts occur:**

    -   List conflicted files with `hg resolve --list`.
    -   Open each unresolved file (`U`-marked), read the conflict markers, and
        resolve the same way as the Git conflict strategy.
    -   Mark resolved: `hg resolve --mark <file>`.
    -   Continue the rebase: `hg rebase --continue`.

### JJ (Jujutsu)

1.  **Fetch and rebase:**

    ```bash
    jj git fetch
    jj rebase -d "main@origin"
    ```

2.  **If rebase conflicts occur:**

    -   List conflicts with `jj status`.
    -   Resolve each conflict, then `jj squash` or `jj resolve` as appropriate.

--------------------------------------------------------------------------------

## Part B — Verification

Run each applicable step from the detected toolchain. Pipe output through
`tail -40` to keep logs manageable.

1.  **Tests:** Run the test command for the detected toolchain.
2.  **Lint (with auto-fix):** Run the lint command. For Fig, use `hg lint`.
3.  **Build:** Run the build command.

**If any step fails:** Present the errors clearly and ask whether to fix now or
continue.

**For Fig/Google3 workspaces** with modified files under packages that have test
targets: identify changed files with `hg diff --stat -r .^`, discover test
targets with `blaze query 'tests(//path/to:all)'`, and run `blaze test` on
affected targets.

--------------------------------------------------------------------------------

## Part C — Summary

1.  **Report results.** Present a concise table (omit rows for steps that don't
    apply to the detected VCS/toolchain):

    | Area            | Step                             | Status         |
    | :-------------- | :------------------------------- | :------------- |
    | Upstream merge  | `origin/$BASE` → `<branch>`     | ✅ / ⚠️ / ⏭️    |
    | Dependency sync | lockfile install                 | ✅ / ⏭️         |
    | Tests           | `<test command>`                 | ✅ / ❌ / ⏭️    |
    | Lint (fix)      | `<lint command>`                 | ✅ / ❌ / ⏭️    |
    | Build           | `<build command>`                | ✅ / ❌ / ⏭️    |

    Use ⏭️ for steps that were skipped (no toolchain detected, no lockfile
    change, etc.).

2.  **List assumptions and follow-ups.** Note every conflict resolution choice,
    any skipped or auto-resolved files, lockfile regeneration decisions, and
    anything else that warrants the user's attention. Ask any questions that
    require follow-up input.
