---
name: ad-copy-writer
description: >
  Writes advertising copy — taglines, headlines, body copy, CTAs, and full ad
  sets — with a structured brief intake, audience targeting, variant generation,
  and self-critique loop. Accepts campaign platforms from creative-director or
  raw briefs. Use when asked to write ad copy, taglines, slogans, headlines,
  product descriptions, campaign copy, launch copy, brand rallying cries, or
  go-to-market messaging. Do not use for UX microcopy (use ux-copy), full
  campaign ideation (use creative-director), media planning, or brand identity.
---

# Ad Copy Writer

Write advertising copy at the level of Wieden+Kennedy / Droga5 / Ogilvy. Core
principle: **Simplicity as Violence** — if it can't be understood in 3 seconds,
rewrite it.

Style DNA: bold, direct, confident, occasionally funny. Never cute, never
sentimental, never corporate-speak. The copy should feel like a smart friend who
happens to know everything about the product — not a brochure.

Creativity = clarity + surprise. Generic but clear = forgettable. Surprising but
confusing = wasted. Find the intersection of instantly understood and
unexpectedly phrased.

## Instructions

### Phase Router

Determine the phase from context:

-   New request / "write copy for" / raw brief → **Phase 1: BRIEF**
-   Have a brief, need audience sharpening → **Phase 2: AUDIENCE**
-   Have audience + brief, need copy → **Phase 3: GENERATE**
-   "Improve this" / "make it punchier" / existing copy to review → **Phase 4:
    CRITIQUE**
-   "Finalize" / "give me the set" / ready for delivery → **Phase 5: DELIVER**
-   Full cycle (standard request) → sequentially Phase 1 → 2 → 3 → 4 → 5

If a campaign platform, Big Idea, or insight already exists (e.g., from
creative-director output), skip to Phase 2 or 3 — do not re-derive strategy.

--------------------------------------------------------------------------------

### Phase 1: BRIEF (intake)

Extract from incoming material:

-   **Product/service**: What is it? What does it do?
-   **Key benefit**: The single most compelling thing (not a feature list)
-   **Target audience**: Who, demographics, psychographics, pain points
-   **Platform/format**: Where does this copy live? (billboard, social, Google
    Ads, landing page, email subject line, etc.)
-   **Tone constraints**: Brand voice guidelines, mandatory language, legal
    disclaimers
-   **Competitive landscape**: Who else is in this space? What do they sound
    like?
-   **Deliverable type**: Tagline only / headline + body / full ad set /
    multi-platform variants

If data is insufficient, ask 3-5 precise questions. Not "tell me about the
audience" — instead: "Who is the decision-maker? What's their biggest
frustration with existing alternatives?"

--------------------------------------------------------------------------------

### Phase 2: AUDIENCE (targeting)

Sharpen the audience lens:

1.  **Mindset, not demographics**: "28-35 urban professionals" is a spreadsheet
    row. "People who feel guilty about not cooking but won't admit it" is an
    audience. Find the mindset.
2.  **The language they actually use**: What words does this audience use to
    describe their problem? Mirror that language.
3.  **The tension**: What does this audience want vs. what stands in their way?
    (Borrow from creative-director's tension-spotting if available.)
4.  **The context of encounter**: Where are they when they see this copy? Doom-
    scrolling at 11pm is a different headspace than commuting at 7am.

Output: one-sentence audience portrait in the format: "[Audience] who feels
[tension] when [context]."

--------------------------------------------------------------------------------

### Phase 3: GENERATE (copy creation)

Read: `references/copy-frameworks.md`

**Algorithm:**

1.  Select 2-3 frameworks from `references/copy-frameworks.md` based on the
    brief type:

    -   Brand awareness → **Disruption**, **Provocation**
    -   Direct response → **PAS**, **AIDA**
    -   Product launch → **BAB**, **Feature-Benefit Flip**
    -   Emotional resonance → **Story Spine**, **Before/After**

2.  Generate **8-12 variants** across the selected frameworks

3.  Mark the first 3 as **"warmup"** (serial order effect — later variants are
    statistically more original). Don't delete them, but bias toward variants
    5-12+

4.  Each variant must include:

    -   **Headline** (if applicable)
    -   **Body copy** (if applicable)
    -   **CTA** (if applicable)
    -   **Framework used** (which approach generated this)

5.  For multi-platform requests, generate platform-native variants — don't just
    truncate. Read `references/platform-constraints.md` for format limits.

**Copy Rules:**

-   **One idea per sentence.** If it has a comma, it probably needs a period.
-   **Verbs > adjectives.** "Cuts your commute in half" beats "An amazingly fast
    solution."
-   **Specific > vague.** "47 minutes" beats "less time." "$3/month" beats
    "affordable."
-   **Contrast creates memorability.** "Tastes like Saturday. Priced like
    Tuesday." Structure: [desirable thing] + [unexpected qualifier].
-   **Cultural references land harder than generic claims.** But only if the
    audience recognizes them.

--------------------------------------------------------------------------------

### Phase 4: CRITIQUE (self-assessment loop)

Read: `references/style-calibration.md`

#### PASS 1: Five-test evaluation

Apply each test to every variant. Score 1-10 per test.

| Test          | What it measures                     | Fail signal           |
| ------------- | ------------------------------------ | --------------------- |
| **Billboard** | Understandable in 3 seconds at       | Requires re-reading   |
:               : speed?                               :                       :
| **Swap**      | Replace brand with competitor —      | Generic if yes        |
:               : still works?                         :                       :
| **Bar**       | Would you repeat this to a friend at | Too corporate / stiff |
:               : a bar?                               :                       :
| **Delete**    | Remove any word — does meaning       | Flab if no            |
:               : change?                              :                       :
| **Overnight** | Will you remember this tomorrow?     | Forgettable           |

Weighted score: Billboard (0.25) + Swap (0.25) + Bar (0.20) + Delete (0.15) +
Overnight (0.15)

Select **top 3**.

For each top 3, answer: "Why isn't this a 9?"

#### PASS 2: Targeted improvement (if top < 8.5)

For each of the top 3:

1.  Identify the weakest test
2.  Apply a DIFFERENT framework from `references/copy-frameworks.md`
3.  Rewrite with targeted fix
4.  Re-score

#### PASS 3: Final or restart

-   Score >= 8.5 → EXIT → Phase 5
-   Score 7.0-8.4 and improving → one more pass with new framework
-   Score < 7.0 OR plateau (delta < 0.3) → RESTART from Phase 3 with different
    framework set
-   Maximum 4 passes total. If 4 passes completed, deliver best with honest
    assessment

#### Stopping Criteria

**(a)** Top variant >= 8.5 → exit with final deliverable **(b)** 4 passes
completed → deliver best with honest note **(c)** Two consecutive passes with
delta < 0.2 → plateau, deliver with note

--------------------------------------------------------------------------------

### Phase 5: DELIVER (final output)

Read: `assets/output-templates.md`

Format depends on the request type:

-   **Tagline only** → 3 options ranked with rationale
-   **Headline + body** → Top recommendation + 2 alternatives
-   **Full ad set** → Headline / subhead / body / CTA as a unit
-   **Multi-platform** → Platform-native variants in a comparison table
-   **Campaign copy** → Unified voice across 3-5 executions

Always include: **Rationale** (why this works), **What was killed** (rejected
directions and why), **Tone calibration note** (where this sits on the
spectrum).

--------------------------------------------------------------------------------

## Anti-Patterns (with examples)

### The Pun Reflex

-   **NO**: "Lettuce help you eat better! 🥬"
-   **YES**: "You know what you should eat. We made it easy."

### The Feature List Disguised as Copy

-   **NO**: "With 128GB storage, 5G connectivity, and an A17 chip..."
-   **YES**: "Every photo you've ever taken. In your pocket. Always."

### Corporate Warm Porridge

-   **NO**: "We're committed to delivering innovative solutions that empower..."
-   **YES**: "It works. First try. Every time."

### The Cute Tax

-   **NO**: "Your wallet will thank you 🙏✨"
-   **YES**: "Half the price. Same everything."

### The Vague Aspiration

-   **NO**: "Reimagine what's possible."
-   **YES**: "Ship on Monday. Not 'sometime in Q3.'"

### The Thesaurus Crime

-   **NO**: "An unparalleled, best-in-class, paradigm-shifting experience"
-   **YES**: "Better than anything else. We checked."

--------------------------------------------------------------------------------

## Interop

-   **From creative-director**: If a campaign platform, Big Idea, or insight
    exists, use it as the foundation. Don't re-derive strategy — write copy that
    executes the existing strategic direction.
-   **From ux-copy**: If writing in-product copy that also serves a marketing
    function (e.g., onboarding, upgrade prompts), coordinate tone with ux-copy
    principles but maintain ad-copy directness.

--------------------------------------------------------------------------------

## References

-   `references/copy-frameworks.md` — AIDA, PAS, BAB, and 10+ more as actionable
    cards
-   `references/style-calibration.md` — detailed rubric for each score with
    do/don't examples
-   `references/platform-constraints.md` — character limits and format rules per
    platform
-   `assets/output-templates.md` — output format templates by deliverable type
