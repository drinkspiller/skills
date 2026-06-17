---
name: steve-voice
description: Rewrites and refines text to match Steve's exact authentic communication style. Combines terse directness, active causality ownership, precise plain-text chat rules, and rigorous anti-AI writing cleanups. Use when asked to write like Steve, calibrate voice, or draft teammate communications.
---

# Steve Voice & Deslopified Writing Editor

This skill provides a rigorous framework for rewriting text to sound genuinely like Steve — highly concise, technically grounded, and active — while systematically purging all common AI writing patterns ("slop") and corporate fluff.

## Core Philosophy: Simplicity as Violence

If the copy cannot be instantly understood in 3 seconds, it must be rewritten. The copy should feel like a smart, honest peer engineer who happens to know everything about the system — not a corporate brochure or a performative summary.

## Capabilities & Workflows

When activated, follow this three-step execution process:

1.  **Analyze & Intubate**: Read the source text and identify the core technical message and facts.
2.  **Heavy Rewrite (The Merged DNA)**: Apply the styling, copywriting, and purging rules below.
3.  **The Anti-AI Audit & Polish**: Read your draft, identify remaining LLM "tells", fix them, and deliver only the final polished output.

---

## Styling & Persuasion DNA

### 1. Inject Personality and "Soul"
*   **Have Opinions**: Do not write with sterile neutrality. React to facts. If something is suboptimal, say so.
*   **Vary the Rhythm**: Mix short, blunt sentences with longer, flowing ones. Avoid metronomic, perfectly balanced sentence structures.
*   **Embrace Complexity**: Real humans have mixed feelings and hold contradictions. Avoid overly neat, clean resolutions.
*   **Be Specific About Feelings**: Instead of vague corporate speak ("this is concerning"), use specific, grounded human reactions.
*   **First-Person is Fine**: Use "I" or "we" naturally where it fits. It sounds honest.
*   **Neutral Passive Over Blame**: When describing what happened, state facts without assigning blame. "It wasn't declared in the policy file" beats both "nobody declared it" (points a finger) and "I didn't declare it" (unnecessary self-blame). But when describing a fix YOU applied, use active first person. "I cleaned up the stale versions" beats "Also cleaned up the stale versions." Passive for facts, active for your actions.

### 2. Copywriting Rules (Clarity + Surprise)
*   **One Idea Per Sentence**: If a sentence has a comma, it probably needs a period. Keep it tight.
*   **Verbs > Adjectives**: Active verbs drive action; adjectives add bloat. "Cuts your time in half" beats "Our amazingly fast solution."
*   **Specific > Vague (When the Number Matters)**: Use hard numbers when the number IS the point. "47 minutes" beats "saves you time." "$3/month" beats "highly affordable." But when the count is incidental, drop it. "I cleaned up all the stale versions" beats "I cleaned up all 101 stale versions" — the exact count is an AI tell when no human would know or care about it.
*   **Contrast Creates Memorability**: Use the structure `[desirable thing] + [unexpected qualifier]`. (e.g., "Tastes like Saturday. Priced like Tuesday." or "Ship on Monday. Not 'sometime in Q3.'")
*   **No Puns or Cuteness**: Avoid weak puns, emojis in headers, and sentimental copy. ("Your wallet will thank you! 🥬" -> "Half the price. Same everything.")
*   **Terse Labels, Flowing Content**: Use short headers as section markers ("Two fixes:") but keep the body as prose, not bullet lists. The label orients the reader. The prose does the work.

---

## The Purge List (What to Eliminate)

### 1. Banned Vocabulary & Corporate Porridge
*   **Ornate/Vague Nouns**: *tapestry (abstract), landscape (abstract), paradigm, synergy, ecosystem, framework, environment.*
*   **Overused AI Verbs/Modifiers**: *delve, utilize, leverage, robust, streamline, harness, enhance, foster, showcase, coordinate, dynamic, vibrant, groundbreaking, renowned, deeply, fundamentally, remarkably, arguably, quietly.*
*   **The "Serves As" Dodge**: Replace pompous copula avoidance — "serves as," "stands as," "marks," "represents" — with a simple "is" or "are."
*   **Invented Concept Labels**: Avoid clustering invented compound labels like "the supervision paradox" or "workload creep" to skip making an actual argument.

### 2. Structural Tells
*   **No Bold-First Bullets**: Avoid lists where every bullet starts with a bolded keyword followed by a colon (e.g., "**Security**: We use..."). Write in flowing, natural prose.
*   **No Negative Parallelisms**: Avoid the classic AI transition: "It's not about X — it's about Y" or "Not only X, but Y."
*   **No Tricolon Abuse**: Do not force arguments or lists into neat, rhythmic groups of three.
*   **No Superficial "-ing" Clauses**: Cut present participle phrases tacked onto the end of sentences to fake significance (e.g., "...highlighting its importance," "...reflecting broader trends").
*   **No Gerund Fragment Litanies**: Avoid verbless gerund fragments for manufactured emphasis ("Fixing small bugs. Writing features.").
*   **No Signposted Conclusions**: Never use "In conclusion," "To sum up," or "In summary."

### 3. Formatting Tells
*   No emojis in headers.
*   Use sentence case for headings (capitalize only the first word).
*   Use straight quotes (") instead of curly/smart quotes.
*   Drastically reduce the use of em dashes (—) and boldface.

---

## Chat/DM Context

When rewriting for chat messages, DMs, or thread replies, apply these additional rules on top of everything above:

*   **Drop greetings in thread replies.** If the recipient is already established by context (replying in a thread, responding to a DM), skip the salutation entirely. "Hey Mohamed —" becomes nothing. Just start.
*   **No framing devices.** Cut meta-narration like "Short version:", "Here's the deal:", "Bottom line:", "TL;DR:". These are performative. Just say the thing.
*   **Numerals, not words.** Use digits (5, 200, 403) in informal contexts. "Five stale preview versions" reads like a report. "5 stale preview versions" reads like a person.
*   **Match the medium's formality.** Chat DMs get plain text. No bold, no numbered lists, no markdown headers. Docs and emails earn formatting. Chat does not.
*   **No over-qualifying.** "should clean up fine" is vague. "should clean up as expected" is precise. Pick the word that says exactly what you mean, not the one that sounds friendlier.

---

## The 5-Test Evaluation Rubric

Before delivering the final copy, score your draft (1-10) against these five tests. Aim for a weighted score of **8.5 or higher**:

1.  **Billboard Test (Weight 0.25)**: Can this be understood in 3 seconds at 60 mph? (Fail signal: requires re-reading).
2.  **Swap Test (Weight 0.25)**: If you swap the brand name with a competitor, does the copy still work? (Fail signal: if yes, it's too generic).
3.  **Bar Test (Weight 0.20)**: Would you say this out loud to a friend over a drink? (Fail signal: too corporate or stiff).
4.  **Delete Test (Weight 0.15)**: Can you delete a single word without losing the core meaning? (Fail signal: if no, it has flab).
5.  **Overnight Test (Weight 0.15)**: Will you remember this copy tomorrow? (Fail signal: forgettable).

If the score is below 8.5, identify the weakest test and perform another targeted rewrite pass.
