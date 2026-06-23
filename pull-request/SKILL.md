---
name: pull-request
description: >
  Create or update a GitHub Pull Request for any Git repository. Auto-discovers
  the repo, base branch, and pre-flight commands from the working directory.
  Prompts the user only when ambiguous.
---

# Pull Request

All commands run from the root of the current Git repository.

## Environment Discovery

Before anything else, detect the repository context:

1.  **Locate the repo root:**

    ```shell
    git rev-parse --show-toplevel
    ```

    If this fails, the current directory is not a Git repo. Stop and ask the
    user to navigate to a Git repository or specify one.

2.  **Detect the remote repo identifier** (for `gh pr create --repo`):

    ```shell
    git remote get-url origin
    ```

    Parse the `owner/repo` from the URL (handles both SSH
    `git@github.com:owner/repo.git` and HTTPS
    `https://github.com/owner/repo.git` formats). If the remote is not
    GitHub-hosted (e.g., GoB, GitLab, Bitbucket), stop and inform the user that
    this skill targets GitHub PRs via `gh`.

3.  **Detect the default base branch:**

    ```shell
    gh repo view --json defaultBranchRef --jq '.defaultBranchRef.name'
    ```

    Fall back to `main` if `gh` is unavailable or the query fails. Store as
    `$BASE`.

## Pre-flight Checks

Auto-discover and run the project's quality gates. Check for the presence of
these files in the repo root, in order:

| Indicator file       | Test command              | Lint command               | Build command              |
| :------------------- | :------------------------ | :------------------------- | :------------------------- |
| `package.json`       | `npm test` or `pnpm test` | `npm run lint` or `pnpm lint` | `npm run build` or `pnpm build` |
| `Makefile`           | `make test`               | `make lint`                | `make build`               |
| `Cargo.toml`         | `cargo test`              | `cargo clippy`             | `cargo build`              |
| `go.mod`             | `go test ./...`           | `golangci-lint run`        | `go build ./...`           |
| `BUILD` / `BUILD.bazel` | *(skip — use blaze/bazel test)* | `buildifier -lint=warn` | `blaze build` or `bazel build` |
| `pyproject.toml` / `setup.py` | `pytest`         | `ruff check .`             | *(skip)*                   |

**Rules:**

-   Prefer `pnpm` over `npm` if a `pnpm-lock.yaml` exists.
-   Only run commands for which the indicator file exists. If none are found,
    skip pre-flight and inform the user.
-   Check `package.json` `scripts` keys before running — if `test`, `lint`, or
    `build` scripts are absent, skip that step.

If any step fails, stop and present the errors. Ask the user whether to fix the
issues or bypass and continue.

## Verify Prerequisites

1.  **Verify GitHub CLI:**

    ```shell
    gh auth status
    ```

    If not authenticated, ask the user to run `gh auth login`.

## Uncommitted Changes

1.  **Check for uncommitted changes:**

    ```shell
    git status --porcelain
    ```

    If there are uncommitted changes, ask the user:

    > You have uncommitted changes. Commit them before creating the PR?

    If yes, invoke the **commit-message** skill or help generate a commit
    message.

## Commit Selection

1.  **Fetch latest remote and list commits unique to this branch:**

    ```shell
    git fetch origin "$BASE" 2>/dev/null; git cherry -v "origin/$BASE" HEAD
    ```

    Parse the output. Lines starting with `+` are commits unique to this
    branch. Present the list to the user and ask:

    > These commits will be included in the PR. Include all, or select a subset?

    Wait for their response.

    If a subset is selected, create a new branch from `origin/$BASE` and
    cherry-pick the selected commits:

    ```shell
    git checkout -b <new-branch-name> "origin/$BASE"
    git cherry-pick <hash1> <hash2> ...
    ```

## Check for Existing PR

1.  **Get the current branch:**

    ```shell
    git branch --show-current
    ```

2.  **Check for an open PR on this branch:**

    ```shell
    gh pr list --head "<branch>" --json url,number,title,body,headRefOid --state open
    ```

    If an existing PR is found, present it and ask:

    > A PR already exists for this branch: \<url>
    >
    > 1. Push & Update (add new commits)
    > 2. Update Title & Description only
    > 3. View in Browser
    > 4. Exit

    Wait for their response.

    -   **Push**: Run `git push -u origin "<branch>"` and stop.
    -   **Update**: Continue to the title/description steps below, then use
        `gh pr edit`.
    -   **View**: Run `gh pr view "<branch>" --web` and stop.
    -   **Exit**: Stop.

## Generate PR Content

1.  **Generate title and description.** Get the commit log and diff:

    ```shell
    git log "origin/$BASE..HEAD" --oneline
    git diff "origin/$BASE...HEAD"
    ```

    Use the commit log and diff (truncate diff to 20k chars) to generate a
    concise PR title and a detailed PR description in markdown with sections:

    -   `## Summary` — what changed and why.
    -   `## Key Changes` — file-by-file or logical grouping of modifications.
    -   `## Security Considerations` — any auth, input validation, or data
        handling changes.
    -   `## Verification Results` — output of pre-flight checks.

2.  **Present the generated title and description to the user.** Ask:

    > Here is the proposed PR:
    >
    > **Title:** \<title>
    >
    > **Description:** \<description preview>
    >
    > Accept, suggest improvements, or edit manually?

    Wait for their response. Iterate until accepted.

## Create or Update PR

1.  **Push the branch:**

    ```shell
    git push -u origin "<branch>"
    ```

2.  **Create or update the PR:**

    For a new PR:

    ```shell
    gh pr create --repo "<owner>/<repo>" --title "<title>" --body "<body>" --base "$BASE"
    ```

    For updating an existing PR:

    ```shell
    gh pr edit <number> --title "<title>" --body "<body>"
    ```

3.  **Present the PR link** prominently in the response:

    ```
    PR created: https://github.com/<owner>/<repo>/pull/<number>
    ```
