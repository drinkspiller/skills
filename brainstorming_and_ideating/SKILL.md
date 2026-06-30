---
name: brainstorming-and-ideating
description: >-
  Explores requirements, mines user insights, and designs architectural or creative concepts before implementation. Synthesizes structured ideation (SIT, TRIZ, bisociation), tension spotting, project-native architectural trade-offs, and multi-axis evaluation. Use when initiating creative work, designing features, brainstorming research ideas, developing product specs, or exploring technical alternatives. Don't use for deterministic linear workflows, one-off scripts, final copywriting polish, or general coding edits.
---

# Brainstorming & Ideating Concepts Into Designs

This skill orchestrates requirements exploration, consumer tension mining,
structural ideation, and multi-axis evaluation before implementation.

--------------------------------------------------------------------------------

## 1. Phase Router

Determine the active phase from conversation context:

*   **Phase 1: INTAKE**: New brief, feature request, "come up with", or
    initiating conceptual design.
*   **Phase 2: INSIGHT**: "Find an insight", tension discovery, or possessing
    raw requirements without underlying rationale.
*   **Phase 3: IDEATION**: "Generate ideas", exploring alternatives, or
    possessing an insight needing concrete concepts.
*   **Phase 4: EVALUATE & REFINE**: "Critique", "improve the concept",
    "stress-test", or scoring proposals against rubrics.
*   **Phase 5: ARTICULATE**: "Finalize design doc", structuring specifications,
    or preparing persistence artifacts.
*   **Full Cycle (Standard Workflow)**: Execute sequentially: Phase 1 → Phase 2
    → Phase 3 → Phase 4 → Phase 5.
    *   *Dynamic Bypass Rule*: For straightforward engineering implementation
        tasks (e.g., adding a caching layer or retry flag), dynamically bypass
        Phase 2 insight discovery and advance directly from Phase 1 to Phase 3
        (proposing 2 to 3 architectural trade-offs).

--------------------------------------------------------------------------------

## 2. Non-Negotiable Core Constraints

### 2.1 Single-Question Refinement

Never overwhelm the user or developer with multiple questions in a single
response. Ask clarifying questions strictly one at a time during refinement.

### 2.2 Incremental Validation Blocks

Deliver architectural or creative proposals in bite-sized blocks (200 to 300
words). Pause and request explicit user validation after each block. Do not
advance to subsequent design sections until the preceding block is approved.

### 2.3 Simplicity as Violence & YAGNI

Actively recommend pruning speculative features, configurability, or
over-engineering. Enforce the clarity check: *if a concept cannot be explained
completely in one sentence, it is not an idea—it is a plan*.

### 2.4 Warmup Pruning (Serial Order Effect)

Statistically, early ideas generated during an ideation cycle represent
conventional warmup (obvious approaches accessible to anyone in the domain).
Treat ideas 1 through 3 as conventional warmup. Deprioritize these early
concepts and focus refinement on deeper directions (ideas 5 through 12+).

### 2.5 Competitor Swap Verification

Replace the primary product, brand, or architecture component in a proposal with
a direct competitor or generic alternative. If the concept still functions
identically without modification, it lacks differentiating specificity
(`Originality <= 5.0`). Re-anchor the design in unique core capabilities.

### 2.6 Verifiable Falsifiability

Every proposed architectural or research alternative must include concrete,
falsifiable verification criteria (e.g., runnable validation checks via native
test runners, explicit test assertions, or quantitative empirical thresholds).

### 2.7 Plan Persistence

Write finalized, validated designs to a markdown artifact in the session's plans
directory using the format `YYYY-MM-DD-<topic>-design.md`.

--------------------------------------------------------------------------------

## 3. Phase Execution Modules

For comprehensive methodologies, mining prompts, and scoring rubrics, consult
the L2 reference modules on demand:

*   **For Phase 2 (Insight Discovery & Tensions)**: Read
    `references/insight-and-tensions.md` (covers Mark Pollard's Four Points,
    Jobs-to-be-Done analysis, Cultural/Category/Human tension spotting,
    How-Might-We laddering, and canonical insight formulas).
*   **For Phase 3 (Ideation & Triplet Generation)**: Read
    `references/ideation-methods.md` (covers triplet method selection across
    Structural, Collision, and Perturbation categories, warmup pruning, and
    system architecture idioms). When ideas must be genuinely novel rather than
    competent variations, also read `references/novel-ideation.md` (covers
    anti-convergence techniques: average purge, bisociative domain collision,
    constraint inversion, temporal retrieval, adversarial stress testing, and
    specificity checks to defeat LLM mode collapse).
*   **For Phase 4 (Evaluation & Stress-Testing Rubrics)**: Read
    `references/evaluation-rubric.md` (covers Brief Compliance pass/fail gates,
    6-Criteria multi-axis scoring, Competitor Swap verification, and Kill Your
    Darlings stress-testing).

--------------------------------------------------------------------------------

## 4. Upstream Attribution & Documentation

For complete upstream attribution, cognitive provenance, and links to all source
repositories, read `README.md`.
