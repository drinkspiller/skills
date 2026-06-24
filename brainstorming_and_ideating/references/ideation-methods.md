# Ideation Frameworks & Triplet Generation

Generating exceptional concepts requires systematic exploration across distinct
cognitive vectors rather than relying on ad-hoc brainstorming. This document
details the triplet ideation protocol, warmup pruning rules, and empirical
verification standards.

--------------------------------------------------------------------------------

## 1. Method Triplet Selection

To prevent cognitive tunneling, never rely on a single ideation technique. For
every Phase 3 (`IDEATION`) cycle, select exactly three methodologies—one from
each of the following complementary categories:

### 1.1 Structural Methods

Dissects and reorganizes existing system boundaries or product attributes.

*   **Systematic Inventive Thinking (SIT)**: Applies subtraction,
    multiplication, division, task unification, or attribute dependency change.
*   **TRIZ**: Resolves system contradictions using established inventive
    principles.
*   **SCAMPER**: Substitute, Combine, Adapt, Modify, Put to another use,
    Eliminate, or Reverse component interactions.

### 1.2 Collision Methods

Forces unexpected associations between unrelated concepts or domains.

*   **Bisociation**: Intersects two completely independent planes of thought or
    knowledge matrices.
*   **Forced Connections**: Merges canonical system architecture patterns with
    unrelated user experiences or external paradigms.
*   **Synectics**: Uses direct, personal, symbolic, or fantasy analogies to
    solve technical bottlenecks.

### 1.3 Perturbation Methods

Disrupts conventional assumptions through inversion or oblique constraints.

*   **Inversion (Reverse Brainstorming)**: Solves how to guarantee system
    failure or maximize user friction, then reverses the mechanics.
*   **Provocation (PO)**: Establishes deliberately impossible constraints to
    step out of established mental models.
*   **Oblique Constraints**: Applies unexpected philosophical perturbations to
    force creative re-routing.

--------------------------------------------------------------------------------

## 2. Generation & Warmup Pruning

1.  **Generate Broadly**: Develop 8 to 12 distinct conceptual directions using
    the selected triplet methodologies.
2.  **Warmup Pruning (Serial Order Effect)**: Statistically, early ideas
    generated during an ideation cycle represent conventional warmup (obvious
    solutions accessible to anyone in the domain). Mark ideas 1 through 3 as
    **Conventional Warmup**. Deprioritize these early concepts and focus
    refinement efforts on deeper, non-obvious directions (ideas 5 through 12+).
3.  **Insight Grounding**: Every candidate idea must trace directly back to a
    mined tension or JTBD insight from Phase 2 (`INSIGHT`).

--------------------------------------------------------------------------------

## 3. System Architecture Idioms

When proposing architectural or technical alternatives, explicitly ground each
candidate approach in standard software engineering conventions:

*   Align dependency management with standard repository packaging and
    dependency trees.
*   Structure compilation and test targets using native build systems.
*   Evaluate data persistence requirements against standard distributed database
    architectures and query patterns.

--------------------------------------------------------------------------------

## 4. Falsifiable Verification Criteria

Unfalsifiable concepts introduce operational risk. Every proposed design
alternative must include explicit criteria for empirical verification:

*   **For Software Architecture**: Provide concrete test assertions, runnable
    CLI verification flags, or reproducible benchmark workflows via native test
    runners.
*   **For Product & Research Concepts**: Define unambiguous user success
    metrics, empirical falsifiability thresholds, and quantitative validation
    targets.
