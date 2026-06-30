---
name: novel-ideation
description: >-
  Generate genuinely novel ideas by structurally defeating LLM mode collapse
  and output homogenization. Applies research-backed anti-convergence
  techniques: explicit average purging, bisociative domain collision,
  constraint inversion, adversarial stress testing, and divergent-before-
  convergent phase decoupling. Use when conventional brainstorming produces
  predictable results, when differentiation from obvious solutions is
  required, or when the user needs ideas that would not appear in the first
  page of results from ten different LLMs given the same prompt. Do not use
  for deterministic lookups, standard boilerplate, or tasks where the
  "average" answer is the correct answer.
---

# Novel Ideation: Anti-Convergence Ideation

## Why This Module Exists

LLMs trained on next-token prediction default to the most probable response —
the centroid of their training distribution. RLHF alignment amplifies this
tendency by penalizing outputs that deviate from safe, consensus patterns.
The result is what researchers call **generative monoculture**: individually
plausible ideas that are collectively indistinguishable across models,
sessions, and users.

Doshi & Hauser (2024, *Science Advances*) demonstrated the paradox directly:
writers using LLMs produced individually higher-quality stories but
collectively less diverse output than writers working alone. The Stanford
ICLR 2025 study (Si, Yang, & Hashimoto) showed that LLMs *can* generate
ideas rated more novel than human experts' ideas — but only when the ideation
process is deliberately structured to prevent convergence.

Temperature is not a solution. Raising temperature adds token-level randomness
(gibberish, incoherence) without producing conceptual novelty. The
interventions that work operate at the prompt architecture level: forcing the
model off its high-probability path through structural constraints, phase
separation, and explicit probability inversion.

## Operating Constraints

- **No premature convergence.** Do not apply the user's practical constraints
  (budget, feasibility, technical stack) during divergent phases. Constraints
  enter only in Phase 5.
- **Externalize before expanding.** The model's high-probability defaults must
  be made visible and excluded before ideation begins. Unexposed defaults
  silently shape every subsequent idea.
- **Concrete over abstract.** Every idea must specify a mechanism, not a label.
  "Intelligent caching" is not an idea — it's a nomination waiting for someone
  else to define it. "An LRU cache keyed on user-session hash that
  pre-populates the three most-accessed resources on login" is an idea.
- **No self-validation.** Do not praise or affirm ideas during generation.
  RLHF-trained tendencies to validate the model's own output are a convergence
  mechanism — affirming an idea increases the probability of generating similar
  ideas in subsequent steps. The model is a critic during ideation, not a fan.
- **Warmup pruning.** Within any generation step that produces multiple ideas,
  the first 2–3 are statistically conventional (the serial order effect,
  documented in creativity research since Guilford). Bias toward ideas
  generated later in each step.

---

## The Process

Five phases, executed in strict order. The divergent phases (1–3) are
intentionally oversized — they generate far more material than needed.
Filtering weak ideas is cheap; generating strong outliers is expensive.

### Phase 1: Seed Divergence

Before generating any ideas, establish the problem space, purge the obvious,
and then shatter the space into unrelated conceptual territories.

#### Step 1: The Average Purge

Generate the five most obvious, standard responses a typical AI or industry
professional would give to the user's prompt. For each, write one sentence
explaining why it's obvious — what makes it the default answer.

These five responses define the **forbidden zone**. Their core premises,
mechanisms, and semantic neighborhoods are excluded from all subsequent
phases. This step exists because research on verbalized sampling shows that
externalizing high-probability defaults relieves the model's pressure to
produce "typical" answers, opening access to lower-probability but
conceptually valid alternatives.

> Do not assign fake probability percentages. The model has no access to its
> own token probabilities during generation. The purge works by making
> defaults *visible and named*, not by quantifying them.

#### Step 2: Problem Decomposition

Restate the user's problem in three forms:

1. **The literal request** — what the user said
2. **The underlying need** — what the user is actually trying to achieve
3. **The inversion** — what would happen if the opposite were true

The inversion surfaces boundary-condition ideas that the literal framing
would never reach. "How do I make onboarding faster?" inverted becomes "What
if onboarding were deliberately slow?" — which surfaces guided-mastery
approaches where slow onboarding produces more competent, longer-retained
users.

#### Step 3: Bisociative Domain Collision

Arthur Koestler's bisociation theory: creative insight emerges from the
collision of two previously unrelated "matrices of thought." LLMs produce
*associations* (A relates to B); bisociation demands *collisions* (A crashes
into C, where C has no obvious relationship to A).

Select three domains with no obvious relationship to the problem:

- One from a different industry or discipline
- One from nature, history, or art
- One from a technical field unrelated to the problem domain

For each domain, identify one operating principle or structural pattern. Then
force a collision: describe how that principle would solve the user's problem
if applied literally.

A product-onboarding problem collided with mycorrhizal networks (fungi that
connect tree root systems to share nutrients) produces "resource bridging" —
new users paired with experienced users through a shared task where the
experienced user's workflow naturally exposes the new user to features. That
idea would never emerge from "list ten onboarding improvements."

#### Step 4: Temporal Retrieval ("What Changed?")

Identify approaches to the user's problem that were previously dismissed,
abandoned, or considered impractical. For each, name the assumption that led
to its rejection and check whether that assumption still holds. Changes in
compute cost, data availability, tooling, regulation, user behavior, or
adjacent technology can invalidate prior rejections.

A real-time translation feature dismissed in 2020 because on-device models
were too large and too slow becomes viable in 2025 because quantized models
run on commodity hardware at acceptable latency. The idea isn't new — the
conditions are.

This step targets a specific LLM blind spot: models surface the current
consensus about an approach without checking whether the reasons for that
consensus remain valid.

### Phase 2: Structured Expansion

Apply **both** of the following techniques to the most promising raw material
from Phase 1. These are forcing functions — they mechanically push ideas into
regions the model wouldn't reach through free generation.

#### Constraint Inversion

Identify three unstated foundational assumptions of the problem space and
deliberately invert each one.

- If the system assumes continuous connectivity → design for 24-hour
  asynchronous batching
- If the interface assumes visual rendering → design for tactile or acoustic
  feedback
- If the architecture assumes centralized consistency → design for
  eventual-consistency gossip protocols
- If the process assumes human initiation → design for autonomous triggering

Each inversion produces at least one candidate idea that operates on
orthogonal principles to the forbidden zone from Phase 1.

#### SCAMPER Mutation

Take the two strongest candidates from Phase 1 and apply the SCAMPER
operators to mutate them beyond their original form:

- **Substitute**: Replace a core component with something from one of the
  collision domains
- **Combine**: Merge two unrelated Phase 1 outputs into a single mechanism
- **Adapt**: Borrow a mechanism from a collision domain and transplant it
- **Modify**: Scale one parameter to an extreme (10× larger, 1000× faster,
  zero cost)
- **Put to another use**: Repurpose the idea for a completely different
  audience or context
- **Eliminate**: Remove the component that seems most essential — what
  survives?
- **Reverse**: Invert the flow, the user role, or the core assumption

Not every operator will produce something useful. The goal is volume — at
least three mutations that feel genuinely unfamiliar.

### Phase 3: Associative Synthesis

Research on creative reasoning (Zheng et al., 2024) demonstrated that
non-sequential, associative reasoning — finding hidden parallels between
seemingly unrelated concepts — outperforms step-by-step Chain-of-Thought for
creative tasks. Linear deduction keeps the model in its familiar inference
path; associative leaps allow conceptual jumps.

For the top candidates from Phase 2:

1. Identify the **emotional core** of the idea — what human need does it
   serve at the most basic level?
2. Find an analog in a completely unrelated domain that serves the same
   emotional core through a different mechanism.
3. Transplant the *mechanism*, not the surface. Steal *how* the analog works
   and apply it to the original problem space.

A notification system's emotional core is "reducing anxiety about missing
something important." An analog: a dog's ears rotating toward a sound before
the dog consciously registers it — passive, ambient awareness without active
monitoring. Transplanted mechanism: ambient environmental cues (a subtle
color shift in the UI chrome) instead of interruptive notifications.

### Phase 4: Adversarial Stress Test

Research on multi-agent debate (Liang et al., 2024, *EMNLP*) showed that
structured argumentation produces more robust outcomes than single-agent
reflection, which actually *degrades* creative quality through a phenomenon
called Degeneration-of-Thought — repeated self-reflection converging toward
safe, consensus outputs.

For each candidate that survived Phase 3:

1. **Attack**: Adopt the perspective of a skeptic who believes this idea will
   fail. Name the *specific* failure mode — not "it might not work" but "it
   fails when user volume exceeds X because the pairing algorithm is O(n²)."
2. **Defend**: Modify the idea to address the attack. The modified version
   replaces the original — the stress test is a refinement step, not just a
   filter.
3. **Triage**: Ideas that became *stronger* through modification are the
   winners. Ideas that required fundamental redesign to survive are discarded
   — they were too fragile to be genuinely novel.

### Phase 5: Convergent Selection

Only now — after divergence, expansion, synthesis, and stress-testing —
re-introduce the user's original constraints (budget, timeline, technical
stack, organizational reality) and filter.

Before presenting, apply the **Specificity Check**: replace the user's
product, system, or context with its closest competitor or generic
alternative. If an idea works identically without modification, it lacks
differentiating specificity — it's a generic industry practice wearing the
user's branding. Rework it to exploit something unique to the user's
situation, or discard it.

Present the final set in two categories:

#### The Frontier

3–5 ideas that are genuinely novel — ideas that would not appear in the first
page of results from ten different LLMs given the same prompt. Each idea
requires:

- **One-line pitch**: The idea in its most compressed form.
- **Collision source**: Which domains, frameworks, or inversions generated
  this — traceability back to the divergent phases.
- **Concrete mechanism**: How it actually works. Not a label, not a
  nomination — a specific operational description. Replace every abstract
  nominalization ("intelligent routing," "dynamic optimization") with the
  named data structure, algorithm, or process it refers to.
- **Causal rationale**: Why this mechanism produces the claimed outcome.
  "X achieves Y because Z" — the "because" clause is mandatory.
- **Failure mode**: The specific physical, computational, or human boundary
  where the idea breaks down. An idea without a known failure mode is
  insufficiently defined.

#### The Unexpected

1–2 ideas that reframe the problem itself rather than answering it. These
challenge whether the user is asking the right question. They may not be
immediately actionable, but they expand the solution space for future
thinking. Flag these explicitly as reframings, not solutions.

---

## Anti-Patterns

### The Listicle Trap

Never generate a flat numbered list of ideas in a single pass. Each idea in a
single-pass list is conditioned on the previous ones, creating a gravity well
around the first idea's semantic neighborhood. The five-phase structure
exists to prevent this — follow it.

### The Synonym Problem

Five ideas that are structurally identical but use different vocabulary are
one idea. "Gamify the experience," "add rewards and badges," "create
achievement milestones," "introduce a points system," and "build a progress
tracker" are the same idea in different outfits. Before presenting final
output, ruthlessly collapse synonyms: strip the vocabulary from each idea and
compare the underlying mechanisms.

### The Safety Bias

RLHF-trained models are tuned to produce helpful, harmless, and honest
responses, which creates systematic bias toward safe, consensus ideas. The
multi-phase structure circumvents this by generating raw material through
structural forcing functions before the model's safety-trained tendencies can
prune the idea space. Do not self-censor during Phases 1–3.

### The Coherence Compulsion

LLMs are rewarded for coherent, well-structured output. Genuinely novel ideas
often feel incoherent at first because they violate the reader's existing
mental model. Do not prematurely polish ideas into smooth,
reasonable-sounding paragraphs during divergent phases — that smoothing
process is itself a form of convergence toward the mean. Polish happens only
in Phase 5.

### The Decoration Trap

Wrapping a conventional idea in unusual vocabulary ("quantum-inspired
onboarding," "neural mesh architecture") does not make it novel. The
mechanism must be different, not just the label. If you strip the adjectives
and the idea is indistinguishable from one in the forbidden zone, it belongs
in the forbidden zone.

---

## Research Foundations

This module synthesizes findings from:

- Doshi, A.R. & Hauser, O.P. (2024). "Generative AI enhances individual
  creativity but reduces the collective diversity of novel content." *Science
  Advances*. Demonstrated the individual-benefit / collective-homogenization
  paradox.
- Si, C., Yang, D., & Hashimoto, T. (2025). "Can LLMs Generate Novel
  Research Ideas?" *ICLR 2025*. LLM-generated ideas rated more novel than
  human experts' ideas under structured conditions.
- Liang, T., He, Z., Jiao, W., et al. (2024). "Encouraging Divergent
  Thinking in Large Language Models through Multi-Agent Debate." *EMNLP
  2024*. Multi-Agent Debate framework countering Degeneration-of-Thought.
- Koestler, A. (1964). *The Act of Creation*. Bisociation theory — creativity
  as the collision of independent matrices of thought.
- Research on verbalized sampling and probability externalization for
  relieving typicality bias in aligned language models.
- Research on divergent-convergent decoupling (CreativeDC) demonstrating that
  simultaneous generation and evaluation causes premature convergence.
- SCAMPER (Eberle, 1971) and TRIZ (Altshuller, 1946–1985) as systematic
  creativity frameworks adapted for LLM prompt architecture.
