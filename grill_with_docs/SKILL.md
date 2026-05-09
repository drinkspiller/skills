---
name: grill-with-docs
description: >
  Grilling session that challenges your plan against the existing domain model,
  sharpens terminology, and updates documentation inline as decisions crystallize.
  Use when user wants to stress-test a plan against their project's language
  and documented decisions, or says "grill me with docs".
---

# Grill With Docs

Interview me relentlessly about every aspect of this plan until we reach a
shared understanding. Walk down each branch of the design tree, resolving
dependencies between decisions one-by-one. For each question, provide your
recommended answer.

Ask the questions one at a time, waiting for feedback on each question before
continuing.

If a question can be answered by exploring the codebase, explore the codebase
instead.

## Domain Awareness

During codebase exploration, also look for existing documentation:

### Project Context Sources

Check for Conductor context first, then fall back to other documentation:

```
project/
├── conductor/                    ← Conductor context (preferred)
│   ├── product.md                ← Product spec / domain glossary
│   ├── tech-stack.md             ← Technical decisions
│   ├── guidelines.md             ← Coding standards
│   └── tracks/                   ← Feature track specs
├── CONTEXT.md                    ← Domain glossary (if no conductor/)
└── docs/                         ← Additional documentation
```

Create documentation lazily — only when you have something to write. If no
`conductor/` or `CONTEXT.md` exists, create one when the first term is resolved.

## During the Session

### Challenge against the glossary

When the user uses a term that conflicts with the existing language in
`conductor/product.md` or `CONTEXT.md`, call it out immediately. "Your glossary
defines 'cancellation' as X, but you seem to mean Y — which is it?"

### Sharpen fuzzy language

When the user uses vague or overloaded terms, propose a precise canonical term.
"You're saying 'account' — do you mean the Customer or the User? Those are
different things."

### Discuss concrete scenarios

When domain relationships are being discussed, stress-test them with specific
scenarios. Invent scenarios that probe edge cases and force the user to be
precise about the boundaries between concepts.

### Cross-reference with code

When the user states how something works, check whether the code agrees. If you
find a contradiction, surface it: "Your code cancels entire Orders, but you just
said partial cancellation is possible — which is right?"

### Update documentation inline

When a term is resolved, update the relevant documentation right there. Don't
batch these up — capture them as they happen:

-   **Conductor projects**: Update `conductor/product.md` with new terms
-   **Non-Conductor projects**: Update `CONTEXT.md`

Don't couple domain documentation to implementation details. Only include terms
that are meaningful to domain experts.

### Offer to record decisions sparingly

Only offer to record a decision when all three are true:

1.  **Hard to reverse** — the cost of changing your mind later is meaningful
2.  **Surprising without context** — a future reader will wonder "why did they
    do it this way?"
3.  **The result of a real trade-off** — there were genuine alternatives and you
    picked one for specific reasons

If any of the three is missing, skip the record. For Conductor projects, add the
decision to the relevant track spec or `conductor/guidelines.md`.
