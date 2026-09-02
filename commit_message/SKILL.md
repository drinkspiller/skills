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
-   **Downstream Impact Analysis:** Analyze downstream impact only when
    modifying critical, high-impact contract files (e.g., protobuf definitions
    `.proto`, public API contracts `.d.ts` / OpenAPI specs, database schemas, or
    breaking dependency upgrades). If genuine breaking changes, schema
    migrations, deprecations, or service risks exist, prepare them for the
    conditional **Side Effects** section.
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
    -   **Structural Ordering Hierarchy:** Enforce the following layout
        sequence for all generated commit messages and PR descriptions:
        1.  **Headline / Subject**: Intent-focused summary with domain/type tag.
        2.  **Brief Overview (`TL;DR:`)**: 1–2 sentence context and guarantees.
        3.  **Demo / Screencast Link (Conditional)**: Placed directly between
            overview and bullets (`Demo: https://...`).
        4.  **Body Bullets**: 3–5 punchy, capability-anchored bullets.
        5.  **Side Effects (Conditional)**: Breaking changes/migrations only.
        6.  **TESTED / Verification**: Automated tests and static UI screenshots.
        7.  **Issue Links & Footers**: Tracker tags (`Closes #123`) and flags.
    -   **Headline Formatting:** A concise, one-line summary of the change.
        -   Prefix the headline with the project or domain tag in square brackets
            (e.g., `[Auth]`, `[Billing]`, `[API]`, `[UI]`).
        -   Start summary with an imperative, present-tense verb (e.g., `Release`,
            `Refactor`, `Add`, `Fix`, `Implement`).
        -   Model high-level architectural intent or user-visible capability
            rather than low-level implementation mechanics or specific file
            names (e.g., `[Auth] Add pre-creation agent onboarding introduction flow`).
        -   Wrap referenced public API methods or service names in backticks
            only when referencing formal external interfaces.
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
    -   **Demo & Screencast Links (Conditional — High-Visibility Placement):**
        -   When a demo link, screen recording, Loom, asciinema, or video
            attachment URL is provided, it **MUST ALWAYS** appear directly
            between the brief overview paragraph (`TL;DR:`) and the bullet list,
            separated by single blank lines:
            ```markdown
            [Headline / Subject]

            [Brief Overview Paragraph]

            Demo: https://...

            - [Bullet 1]
            - [Bullet 2]
            ```
        -   **Prohibit Buried Demos (Anti-Pattern)**: Never bury demo, video, or
            screencast links inside the `Verification` / `TESTED` section, after
            the bullet points, or at the bottom among metadata footers. Visual
            proof must be immediately visible to reviewers before reading
            granular bullets.
    -   **Thematic Capability Bullets (`What's New:` / `Changes:` / `Fixes:`):**
        -   Synthesize changes into 3–5 punchy bullets focused on architectural
            intent and user-visible behavior.
        -   **Forbid Diff Accounting**: Never inventory modified files, internal
            helper functions, styling pixel adjustments, or internal
            state/signal names (e.g., avoid listing CSS margin changes, boolean
            flag additions, or helper function signatures).
        -   **Prohibit Bare Code Leads**: Never start a bullet with a raw file
            name, class name, or mechanical code edit.
        -   **Mandatory Thematic Anchors**: Every bullet MUST lead with a bold,
            capability-oriented anchor or architectural invariant:
            -   `* **Guided Workspace Onboarding**: ...`
            -   `* **Proactive Session Validation**: ...`
            -   `* **Immersive Overlay Presentation**: ...`
            -   `* **Automated Fixture Preparation (Smart Gate)**: ...`
        -   **Voice & Tone**:
            -   Active, present-tense verbs (`Reads...`, `Runs...`,
                `Provides...`, `Evaluates...`).
            -   Focus on the *what* and *why* (user capability, invariant
                guarantees, developer commands) rather than internal signal
                mechanics, local variables, or pixel measurements.
            -   Mention concrete developer-facing commands (e.g., `./run.sh`,
                `npm run dev`, CLI flags) or URLs where applicable to provide
                operational clarity.
    -   **Side Effects Section (`### Side Effects` - Strictly Conditional):**
        -   Include this section **only** when a change introduces genuine
            breaking API contract changes, database schema migrations,
            deprecations, or service downtime risks.
        -   **Omit the section entirely** for standard additive features,
            internal refactors, UI updates, or bug fixes.
        -   Never output placeholder text like `None` or `N/A`, and never
            re-list internal routes, helper wiring, or file touchpoints as side
            effects.
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
    -   **Intent vs. Accounting Contrast (Few-Shot Reference):**

        ```markdown
        <!-- BAD: Mechanical Diff Accounting & Buried Demo (Anti-Pattern) -->
        [UI] Update modal styling and session state

        TL;DR: Modified modal_view.tsx and auth_helper.ts to fix styling and token handling.

        Changes:
        * **modal_view.tsx**: Changed margin-top from 12px to 16px and updated opacity to 0.95.
        * **auth_helper.ts**: Updated refreshTokenHandler() to check isExpired boolean before dispatching.
        * **styles/theme.css**: Added `.modal-backdrop-blur` class with 4px Gaussian blur.
        * **types/session.ts**: Added optional `lastRefreshedAt` timestamp field.

        ### Side Effects
        None.

        ### TESTED
        npm test (12 passed)
        Demo: https://asciinema.org/a/demo12345

        Closes #402
        ```

        ```markdown
        <!-- GOOD: High-Level Intent, Architecture & Prominent Demo -->
        [UI] Add pre-creation agent onboarding introduction flow

        TL;DR: The onboarding modal now guides first-time users through agent workspace configuration with automatic session validation and refined responsive overlay presentation.

        Demo: https://asciinema.org/a/demo12345

        What's New:
        * **Guided Workspace Onboarding**: Introduces interactive setup steps explaining workspace isolation and default tool privileges.
        * **Proactive Session Validation**: Refreshes expiring authentication tokens prior to workflow submission without interrupting form state.
        * **Immersive Overlay Presentation**: Applies consistent backdrop blur and adjusted viewport padding across compact desktop layouts.

        ### TESTED
        * Unit Tests: `npm test -- --filter=onboarding` (18 passed, 0 failed).
        * Manual verification on 1280px and 1920px viewports.

        Closes #402
        ```
-   **Description Update/Creation:** **Crucially, you must then take action to
    create a commit with or update the CL/PR description with the summary you
    generated, based on the user's choice if clarification was sought.** This
    means executing the necessary commands or API calls to set or modify the
    description in the version control or code review system (e.g.,
    GitHub, GitLab).
    -   **Preserve External Anchors on Amend**: When performing an **Amend**
        action or updating an existing PR description, preserve issue/ticket tags
        (`Closes #123`), review links, and durable architectural context.
        Discard earlier drafts' mechanical file-by-file accounting or stale
        bullet lists, replacing them with freshly synthesized high-level intent
        bullets reflecting the overall cumulative diff.
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
-   **Strict Structural Sequence:** Ensure every generated summary strictly
    adheres to the defined ordering hierarchy: Headline -> Brief Overview
    (`TL;DR:`) -> Demo / Screencast Link (conditional; directly below overview)
    -> Body Bullets (`What's New:`) -> Side Effects (conditional; breaking only)
    -> TESTED / Verification (automated test runs, static screenshot URLs) ->
    Issue Links / Footers (`Closes #123`, metadata tags). Never bury demo video
    links inside TESTED or footer sections.
-   **Granularity:** Synthesize cumulative changes into 3–5 high-signal bullets
    focused on architectural intent and user-visible behavior. Do not map every
    touched file or internal helper to an individual bullet.
