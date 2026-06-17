---
name: commit-message
description: Generate and apply a commit message for pending changes using diff analysis.
---

# Commit Message

## Context

You are an expert software engineer tasked with crafting or refining a commit
message for a code change (CL/PR). You have access to the **current working
directory/new state** and, for existing changes, the **parent commit/base
state**. Your goal is to produce a clear, concise, and informative summary that
explains both the *what* and the *why* of the changes for future maintainers.
After generating this summary, you must **apply it** by creating a new commit or
updating the description of an existing change in the relevant tool.

--------------------------------------------------------------------------------

## Specific Objectives

-   **Repo Status Check:** Before generating the description, check the status
    of the repository. Specifically, determine if there are pending, uncommitted
    changes *and* if there is an existing commit at the head of the current
    branch/chain.
-   **Clarification:** If there are both pending changes and an existing commit,
    **ask the user** whether they want to:
    -   **(A)mend:** Combine the pending changes with the existing commit and
        update its message.
    -   **(N)ew:** Create a new commit for the pending changes with the
        generated message.
    -   Await the user's clear response (A or N) before proceeding.
-   **Diff Analysis:** Compare the current codebase against the base state
    (e.g., parent commit in **Fig** or **JJ**, base branch in **Git**, or the
    last sync point for new changes) to identify all modified, added, or deleted
    files.
    -   For **Fig/Mercurial** clients, effectively analyze the changes in the
        current commit against the base commit by using commands like `hg diff
        --from .^` or the configured parent commit.
    -   For **Git** clients, compare against the base branch.
    -   For **JJ** clients, compare against the parent commit.
-   **Downstream Impact Analysis:** Analyze if any critical, high-impact files
    (e.g., protobuf definitions `.proto`, public API contracts `.d.ts` / OpenAPI
    specs, database schemas, or core dependency configurations like `BUILD`,
    `package.json`, `go.mod`) are modified. If so, perform a system-generic
    dependency analysis (e.g., querying reverse dependencies via `bazel query`
    or inspecting import trees) to identify affected downstream targets,
    packages, or modules. Explicitly list these affected components and any
    potential breaking changes in the **Side Effects** section of the generated
    description.
-   **Logic Synthesis:** Identify the primary intent of the changes. Distinguish
    between architectural changes, bug fixes, refactors, and simple UI
    adjustments.
-   **Metadata & Bug Association:** Scan the current branch/bookmark/workspace
    name, or the recent conversation history, to extract issue tracker
    references (e.g., `#1234`, `issue-567`). If found, automatically append the
    appropriate metadata tags to the bottom of the CL/PR description (e.g.,
    `Closes #1234` / `Fixes #1234` for GitHub/GitLab, or the custom review
    system's bug tag format).
-   **Comprehensive Summary Generation:** Write a description that includes:
    -   **Headline:** A concise, one-line summary of the change.
    -   **Body:** A detailed breakdown of the logic changes, highlighting any
        modified APIs or data structures.
    -   **Side Effects:** Explicitly mention any changes to existing behavior,
        potential impacts on downstream systems, and the results of the
        Downstream Impact Analysis.
-   **Description Update/Creation:** **Crucially, you must then take action to
    create a commit with or update the CL/PR description with the summary you
    generated, based on the user's choice if clarification was sought.** This
    means executing the necessary commands or API calls to set or modify the
    description in the version control or code review system (e.g., Gerrit,
    GitHub, GitLab).
    -   **Always Upload/Push Updates:** Whether creating a **New** commit or
        performing an **Amend** action, you must always immediately upload/push
        the updates to the remote review system (e.g., run `hg push` or `hg
        upload` in Fig/Mercurial, or `git push` in Git) to ensure the remote
        CL/PR/change remains fully synchronized with your local workspace.
    -   **Markdown Tag:** When creating or updating descriptions for review
        systems that require a markdown rendering flag (e.g., `MARKDOWN=true` or
        `MARKDOWN=1`), ensure the tag is appended on a new line at the very end
        of the description to enable Markdown rendering.

--------------------------------------------------------------------------------

## Pre-Commit Guardrails (Format, Lint, Build)

Before generating the commit message, you must run automated guardrails to
ensure the codebase remains clean, formatted, and compilable. Run these steps in
order, using the commands appropriate for the system and project at play:

1.  **Formatting (VCS & Language Native)**:
    -   **VCS Native**: If using **Fig/Mercurial**, run `hg fix` to apply
        repository-defined formatters.
    -   **Project/Language Specific**: If using **Git** or other systems, run
        the project's standard formatter (e.g., `npm run format`, `prettier
        --write <changed_files>`, `black <changed_files>`, `gofmt`, `cargo
        fmt`).
    -   Always run specific formatters if available (like `mdformat --number` or
        `prettier --write` for Markdown, or project-specific TypeScript
        formatters).
2.  **Linting (Static Analysis)**:
    -   Run the project's static analysis or linting tools on the changed files
        (e.g., `eslint`, `pylint`, `golangci-lint`, or `buildifier` for BUILD
        files).
    -   Ensure there are no syntax errors, style violations, or unresolved
        import warnings.
3.  **Compilation & Building (Compilation Guard)**:
    -   Run the appropriate build/compilation check to verify the changes do not
        break the build.
    -   For **Monorepos (Bazel)**: Run `bazel build` on the modified targets and
        any immediately affected downstream targets (identified in the
        Downstream Impact Analysis).
    -   For **Standard Projects**: Run the project-defined build command (e.g.,
        `npm run build`, `tsc`, `go build`, `cargo check`).

**Handling Failures:** If any formatting, linting, or building step fails:

-   **Do not proceed** to commit.
-   Present the errors clearly to the user.
-   Ask the user if they would like to resolve the issues first, or if they want
    to bypass the guardrails and commit anyway (e.g., for work-in-progress
    snapshots).

Only proceed to diff analysis and commit message generation **after** all
guardrail passes complete successfully (or the user explicitly chooses to bypass
them).

--------------------------------------------------------------------------------

## Technical Constraints

-   **Accuracy:** Every claim in the description must be backed by a verifiable
    change in the diff.
-   **Tone:** Maintain a professional, objective, and technical tone.
-   **Output Format for Summary:** The generated summary content **must** be
    formatted using Markdown.
    -   Use `#`, `##`, and `###` for section headers.
    -   Use bulleted (`*` or `-`) or numbered lists for structured information.
    -   Use horizontal rules (`---`) to separate distinct sections.
    -   Use double asterisks (`**bold**`) for key terms and single asterisks
        (`*italics*`) for emphasis.
    -   Use backticks for inline code, file names, function names, and variable
        names (e.g., `processData()`, `main.ts`).
-   **Action Implementation:** To apply the description:
    -   Append `MARKDOWN=true` (or the appropriate markdown flag) to the end of
        the generated Markdown summary if required by the code review system.
    -   If interacting with **Mercurial**:
        -   If **New** commit: `hg commit -m "Generated Message..."` followed
            immediately by `hg push` (or `hg upload`) to upload the new commit
            to the code review system as a new change/pull request.
        -   If **Amend**: `hg amend` (to include staged changes) then `hg
            reword` to update the message, followed immediately by `hg push` (or
            `hg upload`) to push the updated description to the code review
            system.
    -   If interacting with **Git**:
        -   If **New** commit: `git add . && git commit -m "Generated
            Message..."` followed immediately by `git push` (or the appropriate
            remote push command) to upload the new commit to the remote review
            system as a new change/pull request (PR).
        -   If **Amend**: `git add . && git commit --amend` followed immediately
            by `git push` (or the appropriate remote push command) to push the
            updated commit/description to the remote review system.
    -   If interacting directly with code review APIs, ensure the full
        description text sent includes any required markdown rendering tags
        (e.g., `MARKDOWN=true`) at the end.
    -   **Confirm that the description has been set or updated in the tool.**
-   **Change/PR Link:** After successfully creating or updating the commit,
    **always** retrieve the change/pull request identifier and present a
    clickable link to the user:
    -   For **Fig/Mercurial**: Retrieve the change number or URL from the push
        output, or use the configured review tool URL template.
    -   For **Git** (Gerrit): Extract the change URL from the `git push` output.
    -   For **JJ**: Run `jj log -r @ --template 'change_id'` and use the
        workspace's review tool URL.
    -   **Format:** Always present the link prominently in your response, e.g.:
        `PR/Change created: https://review.example.com/123456789`
-   **Granularity:** Group related changes into logical bullet points to ensure
    the description is thorough but readable.
