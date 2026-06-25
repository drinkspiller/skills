---
name: pm-brainstorming
description: >
  Brainstorming and structured ideation for Product Management (PM). Use when turning rough product ideas into well-defined specifications, exploring problem spaces, or clarifying vague requirements and success criteria.
---

# PM Brainstorming

## Overview

Help turn rough product ideas into well-defined specs through collaborative dialogue. Don't jump to solutions — explore the problem space first.

**Core principle:** Understand what to build BEFORE defining how to build it.

## The Iron Law

```
NO SPEC WITHOUT UNDERSTANDING PURPOSE AND CONSTRAINTS
```

If you can't articulate why users need this and what success looks like, you're not ready to spec.

## When to Use

**ALWAYS before writing a spec when:**
- Requirements feel vague (3+ unknowns)
- Multiple approaches seem valid
- Success criteria unclear
- User problem not well-defined
- Stakeholder alignment uncertain

## The Process

### Phase 1: Check Existing Context

Before asking questions:
1. Check PM memory (activeContext.md, insights.md)
2. Look for existing specs or research on the topic
3. Review prior decisions that might constrain this feature

### Phase 2: Explore the Idea (One Question at a Time)

**Use AskUserQuestion tool** — multiple choice options provide better UX than open-ended questions.

**Ask questions sequentially, not all at once.**

**Question 1: Problem**
"What user problem does this solve?"
Options:
- A. [Inferred problem from context]
- B. [Alternative problem framing]
- C. Something else (describe)

**Question 2: Users**
"Who are the primary users?"
Options based on context (e.g., existing user types, personas from insights.md)

**Question 3: Success**
"How will we know this works well?"
Options:
- A. Measurable metric (e.g., "adoption rate > 50%")
- B. User behavior change (e.g., "users complete task faster")
- C. Business outcome (e.g., "reduces churn by X%")
- D. Let me define custom criteria

**Question 4: Constraints**
"What constraints should we know about?"
Options:
- A. Timeline (must ship by date)
- B. Technical (platform limitations, dependencies)
- C. Resource (team capacity)
- D. Business (budget, partnerships, compliance)
- E. No major constraints

**Question 5: Scope**
"What's explicitly OUT of scope?"
Options:
- A. [Adjacent feature that might seem related]
- B. [Enhancement that can wait for v2]
- C. Let me list exclusions
- D. Nothing specific yet

### Phase 3: Explore Approaches

**Always present 2-3 product approaches with trade-offs:**

```markdown
## Approaches

### Option A: [Name] (Recommended)
**Approach**: [Brief description]
**Pros**: [Benefits]
**Cons**: [Drawbacks]
**Effort**: [Rough size: Small/Medium/Large]
**Why recommended**: [Reasoning]

### Option B: [Name]
**Approach**: [Brief description]
**Pros**: [Benefits]
**Cons**: [Drawbacks]
**Effort**: [Rough size]

### Option C: [Name]
**Approach**: [Brief description]
**Pros**: [Benefits]
**Cons**: [Drawbacks]
**Effort**: [Rough size]

Which direction feels right?
```

### Phase 4: Present Incrementally

Once approach chosen, present the spec skeleton section by section:

1. **Problem Statement** — "Does this capture the problem accurately?"
2. **User Stories** — "Do these stories cover the key use cases?"
3. **Requirements** — "Are the P0/P1/P2 priorities right?"
4. **Success Metrics** — "Are these the right things to measure?"

**After each section, validate before continuing.**

## Key Principles

### One Question at a Time
```
YES: "What problem does this solve?"
     [Wait for answer]
     "Who are the target users?"
     [Wait for answer]

NO:  "What problem does this solve, who will use it,
      what are the constraints, and success criteria?"
```

### Multiple Choice Preferred
```
YES: "Which approach fits better?
      A. Minimal MVP — ship in 2 weeks
      B. Full solution — ship in 6 weeks
      C. Phased rollout — MVP then expand"

NO:  "How do you want to approach this?"
```

### YAGNI for PMs
```
YES: "You mentioned analytics — is that needed for v1
      or can we defer it?"

NO:  Adding analytics, admin tools, and API access
     because "we might need them later"
```

### Explore Before Committing
```
YES: Presenting 3 approaches with trade-offs
     before asking which to pursue

NO:  Jumping to the first solution that comes to mind
```

## Red Flags — STOP and Ask More Questions

If you find yourself:
- Speccing without knowing the problem
- Jumping to solutions (features, UI) before understanding needs
- Presenting one approach without alternatives
- Asking multiple questions at once
- Assuming you know what the user wants
- Not validating incrementally

**STOP. Go back to Phase 2.**

## Rationalization Prevention

| Excuse | Reality |
|--------|---------|
| "I know what they need" | Ask. You might be wrong. |
| "Multiple questions is faster" | Overwhelms. One at a time. |
| "One approach is obvious" | Present options. Let them choose. |
| "They'll say if it's wrong" | Validate incrementally. Don't assume. |
| "Details can wait" | Get details now. Assumptions cause rework. |

## Output: Spec Skeleton

After brainstorming, produce a spec skeleton ready for the spec-writer to expand:

```markdown
# [Feature Name] — Spec Skeleton

## Problem
[What problem this solves, for whom]

## Users
[Who will use this]

## Success Criteria
- [ ] [Criterion 1 — measurable]
- [ ] [Criterion 2 — measurable]

## Constraints
- [Constraint 1]
- [Constraint 2]

## Out of Scope
- [Explicitly excluded 1]
- [Explicitly excluded 2]

## Chosen Approach
[Which option and why]

## Key User Stories
- As a [user], I want [capability] so that [benefit]

## Open Questions
- [Remaining unknowns]
```

## After Brainstorming

**Continue to spec writing:** The spec-writer agent uses this skeleton to produce the full PRD.
