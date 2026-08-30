---
name: commit-message
description: >
  Generate and apply a commit message for pending changes using diff analysis.
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
    (e.g., base branch in **Git**, parent commit, or the last sync point for new
    changes) to identify all modified, added, or deleted files.
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
-   **Comprehensive Summary Generation (Engineering Broadcast Standard):** Write a
    description that balances high-density executive clarity with technical
    depth, following high-signal engineering communication standards:
    -   **Headline Formatting:** A concise, one-line summary of the change.
        -   Prefix the headline with the project/domain tag in square brackets based on
            modified file paths (e.g., `[Auth]`, `[Billing]`, `[API]`, `[UI]`).
        -   Start summary with an imperative, present-tense verb (e.g., `Release`,
            `Refactor`, `Add`, `Fix`, `Implement`).
        -   Wrap all code symbols, service names, and API methods in backticks
            (e.g., ``[Auth] Implement token refresh interceptor in `auth_client.go` ``).
        -   Keep to 72 characters or fewer without trailing punctuation.
    -   **The Executive `TL;DR:` (Mandatory):**
        -   Immediately below the headline, insert a single 1–2 sentence
            `TL;DR:` paragraph.
        -   **Voice & Tone**: Calm, direct, authoritative, and outcome-oriented.
            State the *human capability* and *system guarantee* unlocked by this
            change before diving into specifics. Avoid corporate jargon,
            performative hype, or raw file names.
        -   **Formula**: `TL;DR: [Project/System] now [core capability /
            behavioral outcome]—[mechanism 1], [mechanism 2], and
            [developer/system guarantee].`
        -   Must be completely understandable by any engineer in under 5 seconds
            without reading the code diff.
    -   **Thematic Capability Bullets (`What's New:` / `Changes:` / `Fixes:`):**
        -   Structure bullets as capability-oriented features, not dry file
            diffs or mechanical nuts-and-bolts.
        -   **Prohibit Bare Code Leads**: Never start a bullet with a raw file
            name, class name, or mechanical code edit (e.g., avoid `* Updated
            session_store.go to...`).
        -   **Mandatory Thematic Anchors**: Every bullet MUST lead with a bold,
            user-visible capability or architectural invariant:
            -   `* **Interactive Verification Walkthroughs**: ...`
            -   `* **Automated Fixture Preparation (Smart Gate)**: ...`
            -   `* **Zero-Guesswork Navigation**: ...`
            -   `* **In-Flight Discrepancy Triage**: ...`
        -   **Voice & Tone**:
            -   Active, present-tense verbs (`Reads...`, `Runs...`,
                `Provides...`, `Evaluates...`).
            -   Focus on the *what* and *why* rather than internal signal
                mechanics, local variables, or pixel measurements.
            -   Mention concrete developer-facing commands (e.g., `./run.sh`,
                `npm run dev`, CLI flags) or URLs where applicable to provide operational
                clarity.
            -   Keep bullet lists concise (3–6 punchy items).
    -   **Side Effects Section (`### Side Effects`):**
        -   Explicitly document behavioral shifts, operational changes, breaking
            contracts, downstream impacts, and migration considerations (or
            state `None`).
    -   **TESTED / Verification Section (`### TESTED`):**
        -   Dedicated verification section documenting:
            -   Automated unit and integration test pass counts (e.g., `pytest`,
                `npm test`, `cargo test`).
            -   Benchmark metrics, empirical pass rates, and confidence
                intervals.
            -   UI screenshot URLs (e.g., PR attachments, image links) or
                test artifact links.
            -   Local installation or deployment test commands (`install.sh
                --target=global` or `npm test`).
-   **Description Update/Creation:** **Crucially, you must then take action to
    create a commit with or update the CL/PR description with the summary you
    generated, based on the user's choice if clarification was sought.** This
    means executing the necessary commands or API calls to set or modify the
    description in the version control or code review system (e.g.,
    GitHub, GitLab).
    -   **Always Upload/Push Updates:** Whether creating a **New** commit or
        performing an **Amend** action, you must always immediately upload/push
        the updates to the remote repository (e.g., run `git push`) to ensure
        the remote PR/branch remains fully synchronized with your workspace.
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
    -   **Project/Language Specific**: Run the project's standard formatter
        (e.g., `npm run format`, `prettier --write <changed_files>`, `black
        <changed_files>`, `gofmt`, `cargo fmt`).
    -   Always run specific formatters if available (like `mdformat --in_place`
        or `prettier --write` for Markdown, or project-specific TypeScript
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
        -   **Confirm description update:** Verify the description is set in
            the tool.
-   **Change/PR Link:** After successfully creating or updating the commit,
    **always** retrieve the change/pull request identifier and present a
    clickable link to the user:
    -   For **Git**: Extract the change URL or commit hash from the `git push`
        output.
    -   **Format:** Always present the link prominently in your response, e.g.:
        `PR/Change created: https://github.com/org/repo/pull/123`
-   **Granularity:** Group related changes into logical bullet points to ensure
    the description is thorough but readable.
