---
name: systematic-debugging
description: >
  Systematic 4-phase debugging methodology: Investigation → Pattern Analysis
  → Hypothesis → Implementation. Use when encountering any bug, test failure,
  or unexpected behavior before proposing fixes. Enforces root-cause analysis
  over symptom fixes.
---

# Systematic Debugging

## Overview

Random fixes waste time and create new bugs. Quick patches mask underlying
issues.

**Core principle:** ALWAYS find root cause before attempting fixes. Symptom
fixes are failure.

**Violating the letter of this process is violating the spirit of debugging.**

## The Iron Law

```
NO FIXES WITHOUT ROOT CAUSE INVESTIGATION FIRST
```

If you haven't completed Phase 1, you cannot propose fixes.

## When to Use

Use for ANY technical issue: test failures, bugs, unexpected behavior,
performance problems, build failures, integration issues.

**Use ESPECIALLY when:** - Under time pressure (emergencies make guessing
tempting) - "Just one quick fix" seems obvious - You've already tried multiple
fixes - Previous fix didn't work - You don't fully understand the issue

**Don't skip when:** - Issue seems simple (simple bugs have root causes too) -
You're in a hurry (rushing guarantees rework)

## The Four Phases

You MUST complete each phase before proceeding to the next.

### Phase 1: Root Cause Investigation

**BEFORE attempting ANY fix:**

1.  **Read Error Messages Carefully** — Don't skip past errors or warnings. They
    often contain the exact solution. Read stack traces completely. Note line
    numbers, file paths, error codes.

2.  **Reproduce Consistently** — Can you trigger it reliably? What are the exact
    steps? Does it happen every time? If not reproducible, gather more data —
    don't guess.

3.  **Check Recent Changes** — What changed that could cause this? Git diff,
    recent commits, new dependencies, config changes, environmental differences.

4.  **Gather Evidence in Multi-Component Systems** — For each component
    boundary: log what data enters, log what data exits, verify
    environment/config propagation, check state at each layer. Run once to
    gather evidence showing WHERE it breaks, THEN analyze.

5.  **Trace Data Flow** — Where does the bad value originate? What called this
    with the bad value? Keep tracing up until you find the source. Fix at
    source, not at symptom.

### Phase 2: Pattern Analysis

1.  **Find Working Examples** — Locate similar working code in same codebase.
2.  **Compare Against References** — Read reference implementations COMPLETELY.
    Don't skim.
3.  **Identify Differences** — List every difference, however small. Don't
    assume "that can't matter."
4.  **Understand Dependencies** — What other components, settings, config,
    environment does this need?

### Phase 3: Hypothesis and Testing

1.  **Form Single Hypothesis** — State clearly: "I think X is the root cause
    because Y." Write it down. Be specific.
2.  **Test Minimally** — Make the SMALLEST possible change to test your
    hypothesis. If the fix doesn't work → REJECT THE HYPOTHESIS. DON'T just add
    another fix on top. IF your first fix doesn't work: STOP and re-analyze. You
    don't understand the problem yet.

### Phase 4: Implementation and Verification

1.  **Clean Implementation** — Remove any temporary debug logs. Apply the fix
    cleanly, following project style. Add comments explaining WHY.
2.  **Verify the Fix** — Reproduce the original failure scenario. Verify it's
    gone. Run ALL related tests. Check for side effects.
3.  **Add Regression Test** — Create a test that fails without this fix. Ensure
    it passes now.
