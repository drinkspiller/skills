---
name: pull-request
description: Create or update a GitHub Pull Request generically for any repository, dynamically detecting settings, validating documentation sync, and rendering highly clear, direct descriptions.
---

# Generic Pull Request Skill

This skill guides the creation or update of a GitHub Pull Request for any
repository. It dynamically detects repository settings, runs project-specific
pre-flight checks, verifies documentation synchronization, and generates
high-value, direct descriptions optimized for reviewer speed.

## 1. Verify Prerequisites

1.  **Verify GitHub CLI Authentication:**

    ```shell
    gh auth status
    ```

    If not authenticated, ask the user to run `gh auth login` before proceeding.

2.  **Check Git Status:**

    ```shell
    git status --porcelain
    ```

    If there are uncommitted changes, ask the user if they want to commit them
    first. Assist them in generating a commit message if needed.

## 2. Repository & Base Branch Detection

1.  **Check for Local Configuration:** Look for `.agents/config.json` or
    `.github/pr-config.json` in the workspace root. If present, read the target
    repository (e.g., `owner/repo`), target remote (e.g., `origin`), and base
    branch from it.

2.  **Dynamic Detection:** If no local configuration is found:

    *   **Remote Detection:** Run `git remote`. If only one remote exists, use
        it. If multiple exist (e.g., `origin` and `upstream`), default to
        `origin` but check if `upstream` is the main upstream repo. Allow user
        override, or default to `origin` with a warning.
    *   **Repo & Branch Detection:**

        ```shell
        # Detect repository name
        gh repo view --json nameWithOwner --jq .nameWithOwner

        # Detect default base branch
        gh repo view --json defaultBranchRef --jq .defaultBranchRef.name
        ```

        If the `gh` commands fail, fallback to:

        ```shell
        git config --get remote.origin.url
        ```

        Parse the URL to extract the `owner/repo` path. If the base branch
        cannot be detected, default to `main`.

3.  **Detached HEAD Safety Check:** Verify if the current HEAD is detached:

    ```shell
    git symbolic-ref -q HEAD
    ```

    If this command exits with a non-zero status, the HEAD is detached. Halt
    execution immediately and instruct the user:

    > **Safety Alert:** You are currently in a detached HEAD state. Please
    > checkout or create a branch (e.g., `git checkout -b feature-branch`)
    > before creating a pull request.

## 3. Documentation Sync Verification

To maintain repository health and prevent documentation rot, verify that
documentation is kept in sync with configuration or API changes.

1.  **Identify Config/API Changes:** Check the diff to see if files modifying
    public APIs, configuration definitions (e.g., `.toml`, `.yaml`, `.json`
    configuration files, `BUILD` rules, or environment templates), or database
    schemas are touched.
2.  **Identify Documentation Updates:** Check if any files ending in `.md`,
    `.mdx`, or located under a `docs/` or `documentation/` directory are
    modified in the same diff.
3.  **Evaluate & Warn:** If configuration/API changes are present in the diff,
    but **no** documentation updates are present:
    *   Stop and present this warning to the user: > **Documentation Sync
        Warning:** I detected changes to project configurations, schemas, or
        APIs, but no corresponding updates to documentation files (e.g., `.md`,
        `.mdx`, or under `docs/`). Would you like to update the documentation
        first before opening the PR?
    *   If the user wishes to update the documentation first, pause the skill
        and allow them to make and commit the edits. Once committed, re-run the
        verification.
    *   If they choose to proceed anyway, continue.

## 4. Project Detection & Pre-flight Checks

Detect the project type by checking for the existence of specific files in the
workspace root, and run the corresponding validation commands. If the local
configuration overrides these commands, use the overrides instead.

*   **Node.js (pnpm):** If `pnpm-lock.yaml` exists: `pnpm test` && `pnpm lint`
    && `pnpm build`
*   **Node.js (npm):** If `package-lock.json` exists: `npm test` && `npm run
    lint` && `npm run build`
*   **Node.js (yarn):** If `yarn.lock` exists: `yarn test` && `yarn lint` &&
    `yarn build`
*   **Rust:** If `Cargo.toml` exists: `cargo test` && `cargo clippy` && `cargo
    build`
*   **Go:** If `go.mod` exists: `go test ./...` && `go vet ./...` && `go build
    ./...`
*   **Python:** If `requirements.txt` or `pyproject.toml` exists: Run `pytest`
    or standard linting if configured.

*Note: If multiple project types are detected or if any pre-flight command
fails, present the issue to the user and ask if they want to skip the checks or
provide custom commands.*

## 5. Commit Selection & Branch Verification

1.  **Identify Unique Commits:** Fetch the latest remote state and list commits
    unique to the current branch compared to the target base branch:

    ```shell
    git fetch <remote> <base-branch> 2>/dev/null
    git cherry -v <remote>/<base-branch> HEAD
    ```

    Lines starting with `+` represent commits unique to this branch.

2.  **Confirm Commits:** Present the list of unique commits to the user. If they
    want to cherry-pick a subset, handle the creation of a temporary clean
    branch, cherry-pick the selected commits, and use that temporary branch for
    the PR.

3.  **Up-to-Date Remote Check:** Fetch the remote branch and compare hashes:

    ```shell
    git fetch <remote> <current-branch> 2>/dev/null
    git rev-parse HEAD
    git rev-parse <remote>/<current-branch>
    ```

    If the hashes are identical, skip `git push` and inform the user:

    > **Info:** Remote branch is already up-to-date. Skipping git push.

## 6. Check for Existing PR

Check if a PR is already open for the current branch:

```shell
gh pr list --head "<current-branch>" --json url,number,title,body --state open
```

If an existing PR is found, present it and ask the user to choose:

1.  **Push & Update:** Push new commits to the remote branch (`git push <remote>
    <current-branch>`) and exit.
2.  **Update Metadata:** Update the PR title and description only (continue to
    Step 7, then use `gh pr edit`).
3.  **View in Browser:** Open the PR in the browser (`gh pr view --web`) and
    exit.
4.  **Cancel:** Abort the operation.

## 7. Generate PR Content

1.  **Gather Context:** Get the commit log and the diff compared to the base
    branch (excluding lockfiles, binary assets, and generated code to conserve
    token limits):

    ```shell
    git log <remote>/<base-branch>..HEAD --oneline
    git diff <remote>/<base-branch>...HEAD -- . ":!*lock*" ":!*.min.*" ":!*.map" ":!*.png" ":!*.jpg"
    ```

    *If the diff exceeds 20,000 characters, compress it using a tiered strategy:
    run `git diff --stat`, gather full diffs only for source code files, or
    truncate with a notice.*

2.  **Auto-Detect GitHub Templates:** Check for existing templates in the
    workspace (e.g., `.github/pull_request_template.md`). If found, use the
    template as the structural base, replacing placeholders with generated
    content.

3.  **PR Description Formatting & Prose Rules:** Optimize the description for
    maximum clarity and speed. Adhere strictly to these writing guidelines:

    *   **Direct Prose Style:** Use the active voice and present tense (e.g.,
        "Add authentication middleware" instead of "Added authentication
        middleware" or "This PR adds...").
    *   **Omit Needless Words:** Strip out hedges ("rather", "quite"), fillers
        ("in order to", "the fact that"), and defensive disclaimers ("this is a
        first pass", "not sure if this is correct").
    *   **Front-load Keywords:** Place the most important technical terms in the
        first two words of each paragraph and list item.
    *   **Concrete > Abstract:** Use concrete numbers, error codes, or paths
        rather than vague descriptions.
    *   **No File-by-File Narration:** Do not write paragraphs explaining what
        changed file-by-file in the body. Focus on the overarching architectural
        design or pattern.
    *   **Above-the-Fold Files Table:** If the PR modifies more than 2 files,
        generate a compact table at the very top of the description: | File |
        Why | | --- | --- | | `path/to/core_file.py` *(start here)* | 1-sentence
        explanation of why this file changed and its role. | |
        `path/to/helper.py` | 1-sentence explanation of the helper's changes. |
        *(Identify the logical entry-point file and explicitly suffix it with
        `*(start here)*`)*

4.  **Proposed Structured Template (Default):** If no local GitHub template
    exists, use the following default structure:

    ```markdown
    ## TL;DR
    [Two sentences. First names the problem with a concrete number, error, or example. Second names what the PR does about it.]

    **Files to review (N, +X / -Y):**
    [Insert Above-the-Fold Files Table here]

    ## Why
    [Why the PR exists. Show the problem. Skip if the TL;DR covers the "why" completely.]

    ## How
    [The change, top-down. Focus on design decisions, not line-by-line narration.]

    ## Security Considerations
    [Document any security implications or trust boundaries touched. State "None" if not applicable.]

    ## Verification Results
    [Detail the automated tests run and any manual verification performed.]
    ```

5.  **Review with User:** Present the generated title and description to the
    user for feedback. Iterate until approved.

## 8. Create or Update PR

Provide a **Dry-Run Simulation** option at startup. If running in Dry-Run mode,
output a complete **Simulation Report** showing target remotes, target branches,
the exact git push command, and the complete generated PR title and description.
Do not execute any write operations.

If executing normally:

1.  **Write Body to Temp File:** Write the approved markdown description to
    `/tmp/pr_body.md`.
2.  **Execute CLI Command:**

    *   **For a New PR:**

        ```shell
        gh pr create --repo <repo> --title "<title>" --body-file /tmp/pr_body.md --base <base-branch>
        ```

    *   **For an Existing PR:**

        ```shell
        gh pr edit <pr-number> --title "<title>" --body-file /tmp/pr_body.md
        ```

3.  **Clean Up:** Remove the temporary file: `rm /tmp/pr_body.md`
