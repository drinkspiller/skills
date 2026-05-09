---
name: improve-codebase-architecture
description: >
  Find deepening opportunities in a codebase, informed by the domain language
  and documented decisions. Use when the user wants to improve architecture,
  find refactoring opportunities, consolidate tightly-coupled modules, or make
  a codebase more testable and AI-navigable.
---

# Improve Codebase Architecture

Surface architectural friction and propose **deepening opportunities** —
refactors that turn shallow modules into deep ones. The aim is testability and
AI-navigability.

## Glossary

Use these terms exactly in every suggestion. Consistent language is the point —
don't drift into "component," "service," "API," or "boundary."

-   **Module** — anything with an interface and an implementation (function,
    class, package, slice).
-   **Interface** — everything a caller must know to use the module: types,
    invariants, error modes, ordering, config. Not just the type signature.
-   **Implementation** — the code inside.
-   **Depth** — leverage at the interface: a lot of behaviour behind a small
    interface. **Deep** = high leverage. **Shallow** = interface nearly as
    complex as the implementation.
-   **Seam** — where an interface lives; a place behaviour can be altered
    without editing in place.
-   **Adapter** — a concrete thing satisfying an interface at a seam.
-   **Leverage** — what callers get from depth.
-   **Locality** — what maintainers get from depth: change, bugs, knowledge
    concentrated in one place.

Key principles:

-   **Deletion test**: imagine deleting the module. If complexity vanishes, it
    was a pass-through. If complexity reappears across N callers, it was earning
    its keep.
-   **The interface is the test surface.**
-   **One adapter = hypothetical seam. Two adapters = real seam.**

This skill is *informed* by the project's domain model. The domain language
gives names to good seams; documented decisions record choices this skill should
not re-litigate.

## Process

### 1. Explore

Read the project's domain glossary and any documented decisions in the area
you're touching first. Check for:

-   `conductor/product.md` — domain glossary (Conductor projects)
-   `conductor/guidelines.md` — recorded technical decisions
-   `CONTEXT.md` — domain glossary (non-Conductor projects)

Then walk the codebase organically and note where you experience friction:

-   Where does understanding one concept require bouncing between many small
    modules?
-   Where are modules **shallow** — interface nearly as complex as the
    implementation?
-   Where have pure functions been extracted just for testability, but the real
    bugs hide in how they're called (no **locality**)?
-   Where do tightly-coupled modules leak across their seams?
-   Which parts of the codebase are untested, or hard to test through their
    current interface?

Apply the **deletion test** to anything you suspect is shallow: would deleting
it concentrate complexity, or just move it? A "yes, concentrates" is the signal
you want.

### 2. Present candidates

Present a numbered list of deepening opportunities. For each candidate:

-   **Files** — which files/modules are involved
-   **Problem** — why the current architecture is causing friction
-   **Solution** — plain English description of what would change
-   **Benefits** — explained in terms of locality and leverage, and also in how
    tests would improve

**Use domain vocabulary for the domain, and this skill's glossary for the
architecture.** If the project's domain glossary defines "Order," talk about
"the Order intake module" — not "the FooBarHandler."

**Decision conflicts**: if a candidate contradicts an existing documented
decision, only surface it when the friction is real enough to warrant revisiting
the decision. Mark it clearly. Don't list every theoretical refactor a past
decision forbids.

Do NOT propose interfaces yet. Ask the user: "Which of these would you like to
explore?"

### 3. Grilling loop

Once the user picks a candidate, drop into a grilling conversation. Walk the
design tree with them — constraints, dependencies, the shape of the deepened
module, what sits behind the seam, what tests survive.

Side effects happen inline as decisions crystallize:

-   **Naming a deepened module after a concept not in the domain glossary?** Add
    the term — same discipline as the `grill-with-docs` skill.
-   **Sharpening a fuzzy term during the conversation?** Update the glossary
    right there.
-   **User rejects the candidate with a load-bearing reason?** Offer to record
    the decision so future architecture reviews don't re-suggest it. Only offer
    when the reason would actually be needed by a future explorer.
