---
name: zoom-out
description: Step back from granular details to provide a high-level, plain-language overview of code architecture, technical systems, previous explanations, strategies, or conceptual topics. Use when asked to zoom out, step back, explain simply, give the 10,000-foot view, summarize the big picture, or unpack dense reasoning.
disable-model-invocation: false
disable-slash-command: false
---

# Zoom Out (High-Level & Plain-Language Overview)

Step back from low-level mechanics, dense jargon, and cognitive overload to
deliver an altitude-calibrated, plain-language mental model of the subject under
discussion.

## 1. Target & Scope Resolution

Determine what the user wants to zoom out from:

-   **Target Specified** (e.g., `/zoom-out auth interceptor`, *"zoom out on
    Option B in your last response"*): Focus strictly on that subsystem,
    decision, or concept.
-   **Target Omitted** (e.g., `/zoom-out`, *"zoom out"*, *"give me the
    high-level view"*):
    -   **Trajectory Back-Traversal**: Inspect conversation history to locate
        the most recent *substantive domain deliverable* (a code proposal,
        architecture plan, error diagnosis, or design debate).
    -   **Skip Operational Noise**: Never zoom out on intermediate progress
        updates, tool execution notices (e.g., `task finished with exit code
        0`), `ask_question` option lists, or raw command status.
-   **Cold-Start Fallback (Turn 0 / Empty Context)**: If invoked in a fresh
    session with no target and no preceding discussion, do not hallucinate a
    topic. Ask a single concise sentence offering 2–3 common scopes: *"What
    would you like to zoom out on? (e.g., current repository architecture, a
    specific design doc, or an active CL)*".

--------------------------------------------------------------------------------

## 2. Elevation Lenses & Frameworks

Select the appropriate lens based on the subject (or apply **Hybrid** if
technical design and strategy are coupled):

### Mode A: Code & Technical Systems (Architectural Topology)

Strip away syntax details, loop mechanics, local variables, and boilerplate.
Deliver:

1.  **The 10,000-Foot Purpose**: State in 1–2 plain sentences what this
    component exists to do and what breaks if it disappears.
2.  **System Boundaries & Call Topology**: Render a compact ASCII flow diagram
    ($\le 5$ nodes, $\le 4$ vertical lines) showing how control or data moves
    across boundaries:

    ```text
    [Upstream Callers / Triggers] ──► [Target Component] ──► [Downstream State / Storage]
    ```
3.  **Domain Vocabulary Alignment**: Map internal identifiers to ubiquitous
    domain terms (`terms.md` or domain glossary) so code names connect to
    real-world concepts.
4.  **What You Can Safely Ignore Right Now**: Explicitly list 2–3 noisy
    implementation details (e.g., serialization quirks, retry backoff math,
    wrapper boilerplate) that do not affect the big-picture mental model.

### Mode B: Strategy, Concepts & Discourse (Plain-Language Synthesis)

Strip away domain jargon, acronyms, and multi-layered caveats. Deliver:

1.  **Bottom Line Up Front (Plain English)**: A direct, 1–2 sentence translation
    of the concept, strategy, or previous response section—written so a
    colleague stepping into the room immediately grasps the core point.
2.  **Mental Model Flow**: Render a compact ASCII flow showing the logical
    progression:

    ```text
    [Problem Trigger / Friction] ──► [Core Decision / Lever] ──► [Desired Outcome]
    ```
3.  **The 3-Pillar Breakdown**:

    -   **The Problem / Goal**: What friction, risk, or objective is driving
        this?
    -   **The Mechanism**: What is the actual lever being pulled or decision
        being made, in plain conversational language?
    -   **The Real-World Trade-Off**: What gets better as a result, and what
        cost, constraint, or risk is accepted?

### Mode C: Hybrid (Strategy-Coupled Architecture)

Use when technical mechanics are inextricably tied to an operational or business
strategy (e.g., database migrations, auth policy refactors). Deliver:

1.  **Combined BLUF**: 1–2 sentences explaining how the technical refactor
    serves the overarching strategy.
2.  **Dual-Track ASCII**: A compact 2-line diagram linking technical boundaries
    to business flow:

    ```text
    Technical: [Legacy Client] ──► [Adapter / Boundary] ──► [Modern Backend]
    Strategic: [Friction Point] ──► [Migration Lever]   ──► [Target State]
    ```
3.  **The 3-Pillars + Ignorable Details**: The 3 strategic pillars followed by 2
    implementation details that can be ignored for now.

--------------------------------------------------------------------------------

## 3. Universal Anchor: Current Coordinates ("Where We Are Now")

Conclude every zoom-out response by anchoring the elevated view back to the
active task:

-   **Situate Context**: State where the current discussion, active file, or
    pending decision sits inside the broader map.
-   **Immediate Next Step**: Identify the single most logical next action from
    this elevated perspective.
-   **Altitude Adjusters**: Conclude with a lightweight one-line handle for
    changing altitude: *(e.g., "Reply 'zoom in on [Component]' to drill into
    mechanics, or 'zoom out to 30k ft' for an executive summary.")*

--------------------------------------------------------------------------------

## 4. Tone & Behavioral Guardrails

-   **Adult Plain Language, Zero "ELI5" Fluff**: Write for an intelligent
    engineer who wants altitude and clarity, not condescending analogies (avoid
    *"Imagine a database is like a busy restaurant kitchen..."*). Describe real
    causality in concrete everyday words.
-   **Zero Circular Jargon**: Never define or explain a complex term using the
    exact same technical terms that prompted the user to zoom out.
-   **Strict Bounding & Scannability**:
    -   Total response text must remain under **350 words**.
    -   ASCII diagrams must remain under **6 lines** and **5 nodes**.
    -   Use bold lead-ins for every section so the entire response can be
        scanned in under 15 seconds.
