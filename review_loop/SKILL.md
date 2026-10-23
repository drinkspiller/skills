---
name: review-loop
description: >-
  Performs multi-expert code review and iterative automated repair loops on
  workspace changes, commits, or pull requests. Evaluates code against
  correctness, architecture, security, readability, and code taste, formatting
  findings as outcome-first plain-English leads (<= 2 code pills) with
  collapsible <details> blocks for symbol/code traces. Supports both
  single-pass report-only review (for PRs and branches) and iterative
  fix-and-verify loops with full CDD/SDD context awareness. Use when asked to
  "review my changes", "do a code review", "review and fix issues", "check code
  quality", or "make changes review-ready".
---

# Review Loop

## Overview

This skill executes a multi-perspective review and verification pipeline over local workspace changes, branch commits, or pull requests.

It operates in two modes:
1. **Mode A: Report-Only Review (`--report-only` / `MAX_ITERATIONS = 1`)**: Evaluates changes, filters false positives against project specs/ADRs, and formats humanized review feedback without modifying workspace source files (for PRs or teammates' branches).
2. **Mode B: Fix-and-Verify Loop (`MAX_ITERATIONS = 3`)**: Evaluates changes, applies valid fixes in priority order (`P0`–`P3`), verifies each fix against test suites and linters, rolls back any regressions, and repeats until clean.

Findings use **two-layer progressive disclosure**: a 3-second plain-English summary on top, backed by a collapsible `<details>` disclosure block containing exact symbol paths and suggested code replacements.

---

## Workflow

### 1. Prime Project Context (CDD / SDD & Invariants)

Before inspecting diffs, scan the repository root and `docs/` for intentional architectural context:
- **Agent Rules & Entry Points**: `AGENTS.md`, `CLAUDE.md`, `.cursorrules`, `.cursor/rules/*.mdc`, `.github/copilot-instructions.md`.
- **CDD / SDD Frameworks**:
  - `armature/` or `_armature/`: Silently load foundation docs (`product.md`, `tech-stack.md`, `guidelines.md`, `workflow.md`), active track specs (`armature/tracks/<id>/spec.md`), and ADRs. Invoke `/arm-chat armature/` if supported by the host.
  - `conductor/`: Load `conductor/product.md`, `conductor/tech-stack.md`, and active tracks in `conductor/tracks/`.
  - `specs/`, `docs/specs/`, `rfcs/`, `docs/rfcs/`: Scan active feature specs and RFCs.
- **Architecture Decision Records (ADRs)**: `docs/adr/*.md`, `adr/`, or `architecture/decisions/`.
- **Core Architecture & Invariants**: `ARCHITECTURE.md` or architecture sections in `README.md`.

**Extracted Baseline**: Identify system boundaries, active feature intent, accepted trade-offs/ADRs, and testing conventions before reviewing lines.

---

### 2. Resolve Mode & Diff Scope

1. **Select Mode**:
   - Default to **Mode B (Fix-and-Verify)** for "review and fix", "clean up", or "prepare code for review".
   - Default to **Mode A (Report-Only)** for "review only", "report only", PR reviews, or when passed `--report-only`.
2. **Resolve Diff Scope**:
   - **Dirty working tree** (`git status --porcelain` is non-empty): Review staged and unstaged changes against `HEAD` (`git diff HEAD`) plus untracked files.
   - **Feature branch**: Review commits against the base branch (`git diff $(git merge-base HEAD main)..HEAD` or `git diff HEAD~1..HEAD`).
   - **Pull request**: Inspect diff via `gh pr diff` and fetch open review threads via `gh pr view --comments` to avoid duplicating feedback.

---

### 3. Run Review & Verification Pipeline

In each iteration, run both static analysis and specialist review passes over the modified files:

#### A. Deterministic Linters & Type Checkers
Run configured repository tools on modified files:
- **Python**: `ruff check`, `ruff format --check`, `mypy` / `pyright`
- **TypeScript / JavaScript**: `eslint`, `tsc --noEmit`, `prettier --check`
- **Rust**: `cargo clippy --all-targets`, `cargo fmt --check`
- **Go**: `golangci-lint run`, `go vet ./...`
- **C / C++**: `clang-tidy`, `clang-format --dry-run -Werror`

#### B. Multi-Perspective Review Pass
When subagent dispatch is supported in the host harness, spawn an independent reviewer subagent with a fresh context window to evaluate the diff without author bias. Otherwise, perform a structured self-review evaluating four dimensions:
1. **Correctness & Edge Cases**: Bounds checking, nullability, error propagation, resource leaks, race conditions, and state transitions.
2. **Architecture & Invariants**: Boundary separation, API consistency, avoidance of unnecessary abstractions, and alignment with loaded specs/ADRs.
3. **Security & Trust Boundaries**: Input sanitation, injection protection, authentication/authorization checks, secrets/tokens, and sensitive logging.
4. **Readability & Craft**: Idiomatic conventions, clear naming, and targeted test coverage for newly introduced branches.

---

### 4. Filter Findings & Enforce Spec Precedence

Consolidate all linter outputs and review findings into a single deduplicated list.

#### Filtering Guardrails
1. **Spec / ADR Precedence Rule (MANDATORY)**:
   - Treat confirmed project specs, track plans, and ADRs as authoritative ground truth.
   - If a finding flags a pattern, dependency, or trade-off that was explicitly decided in a loaded spec or ADR, drop it immediately (`status: skipped_spec_adr_precedence`).
   - Conversely, flag code changes that violate explicit boundary rules or tech-stack constraints defined in project documentation.
2. **Drop Noise & Existing Feedback**: Omit pre-existing unchanged-code issues, trivial nitpick bloat, and items already raised in open PR comments.
3. **Strict Single-Finding Purity**: Enforce **strictly one finding per comment**. Never staple secondary style comments or description nits onto an unrelated inline issue. Anchor distinct findings to their own files and lines.
4. **Exit on Zero Findings**: If 0 actionable comments remain, exit the loop and report a clean review.

#### Ranking & Metadata Schema
Each finding records:
- `priority`: `P0` (critical/security/data-loss/broken build), `P1` (high — probable bug or structural flaw), `P2` (medium — edge case, test gap, maintainability), `P3` (low — minor idiomatic polish)
- `severity`: `S0` (critical), `S1` (major), `S2` (moderate), `S3` (minor)
- `path`: File path relative to repository root
- `line`: 1-based target line number or range
- `reviewer_identifier`: Tool or lens (`CorrectnessReviewer`, `SecurityReviewer`, `RuffLinter`, `TypeScriptCompiler`)
- `category`: Short category label (`Error Handling`, `Resource Leak`, `Type Safety`)
- `plain_lead`: Outcome-first human lead sentence + friendly suggestion
- `details_body`: Precise symbol trace, doc citation (if applicable), and 2–5 line fenced code replacement
- `verification_command`: Linter or test command validating the resolution

Sort findings strictly by:
1. **Priority**: `P0 > P1 > P2 > P3`
2. **Severity**: `S0 > S1 > S2 > S3`

Count iteration comments strictly via `len(comments)`.

---

### 5. Format Comments via Progressive Disclosure

Structure every finding for two audiences: **a 3-second human scan** on top and **complete symbol/code precision** inside a collapsible `<details>` block.

#### Layer 1 — Visible Plain-English Lead (Human Scan)
- **Outcome-first**: Sentence 1 states what fails or behaves unexpectedly in direct product or domain terms. Never start with bottom-up call stacks (*"In `parseData()` (line 42), when `input` is..."*).
- **Warm, collegial tone**: Sentence 2 asks or suggests the fix naturally (*"Worth also checking that `status` isn't reset here so retry isn't skipped?"*).
- **Inline code cap**: At most 2 inline code spans (`<= 2` backtick pills). Refer to routes, flags, and concepts in plain English.
- **Humanizer pass**:
  - **NO** template headers (`**Problem:**`, `**Proposed Solution:**`, `**Rationale:**`).
  - **NO** AI clichés (*crucial, pivotal, underscores, delve, robust, seamless, additionally*).
  - **NO** negative parallelisms (*Not only... but...*), forced rule-of-three lists, or robotic sign-offs.

#### Layer 2 — Collapsible `<details>` Block (Deep Inspection & Agents)
- Standard GFM/CommonMark blank-line syntax:
  1. `<details>` on its own line preceded by a blank line.
  2. A blank line, followed by `<summary>Code path and suggested fix</summary>` on its own line using **plain ASCII letters only** (strictly no `<`, `>`, `&`, or backticks inside `<summary>`).
  3. A blank line, followed by symbol/line traces, architectural citations, and a 2–5 line fenced code block.
  4. A blank line, followed by `</details>` on its own line.

```markdown
When the connection drops during sync, the error boundary clears the cached profile before the retry timer fires, leaving the UI in an unrecoverable blank state. Worth preserving the previous profile cache until a retry succeeds?

<details>

<summary>Code path and suggested fix</summary>

`SyncManager.handleDisconnect()` (lines 88-102) resets `this.activeProfile` to `null` before scheduling `scheduleRetry()`.

```typescript
if (!this.activeProfile) {
  this.activeProfile = this.lastKnownProfile;
}
this.scheduleRetry();
```

</details>
```

---

### 6. Execution: Mode A vs. Mode B

#### If Operating in Mode A (Report-Only)
1. Do **not** edit any workspace source files.
2. If reviewing a PR and requested to post comments, format each thread using the two-layer structure above.
3. Write `review_loop_details.md` and present the findings summary table in chat.

#### If Operating in Mode B (Fix-and-Verify)
1. **Process Findings in Sorted Order**: Address `P0` and `P1` issues before `P2` and `P3`.
2. **Apply High-Confidence Fixes**: Apply code edits for valid findings; skip and document reasons for findings that are out-of-scope or conflict with ADRs.
3. **Verify Each Fix**: Run the corresponding `verification_command` and project test suites (`pytest`, `pnpm test`, `cargo test`, `go test ./...`).
   - If tests fail, diagnose and fix.
   - If a fix causes an unresolvable regression, **revert that specific change** (`git checkout -- <file>`) and record it under **Unapplied Comments**.
4. **Loop Decision**:
   - If `iteration < MAX_ITERATIONS` and at least one fix was applied, increment `iteration = iteration + 1` and return to **Step 3**.
   - If `iteration == MAX_ITERATIONS` or no fixes were applied (all findings were skipped or clean), proceed to **Step 7**.

---

### 7. Write Review Loop Report & Summarize

Write a markdown report (`review_loop_details.md`) in the workspace or scratch directory using the template below, and output a concise summary in chat.

#### Report Template (`review_loop_details.md`)

```markdown
# Review Loop Execution Details

## Execution Metadata
- **Workspace**: `/path/to/repo`
- **Mode**: `{Report-Only | Fix-and-Verify}`
- **Diff Scope**: `HEAD` (or `<base>..<head>`)
- **Total Iterations**: {total_iterations}
- **Final Status**: `{PASS | PASS_WITH_UNAPPLIED_COMMENTS | NEEDS_ATTENTION}`

## Review Loop Iteration Breakdown

| Iteration | Total Comments | Applied | Unapplied | P0 | P1 | P2 | P3 | S0 | S1 | S2 | S3 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | {total} | {applied} | {unapplied} | {p0} | {p1} | {p2} | {p3} | {s0} | {s1} | {s2} | {s3} |

> Note: For every row, `Total Comments` must exactly equal `Applied + Unapplied`, `P0 + P1 + P2 + P3`, and `S0 + S1 + S2 + S3`.

---

## Findings & Actions

### Iteration 1

#### 1. [{priority} / {severity}] `{path}:{line}` — {category}
{plain_lead}

<details>

<summary>Code path and suggested fix</summary>

{details_body}

</details>

- **Reviewer**: `{reviewer_identifier}`
- **Status**: `{Applied | Unapplied}`
- **Resolution**: {explanation of applied fix and test verification, or specific rationale why skipped/reverted}
```
