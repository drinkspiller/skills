# Debugging Tactics & Log Analysis Guide

This document outlines rigorous debugging practices, log analysis workflows,
and structured diagnostic formats.

---

## 1. Core Debugging Tactics

-   **Analysis**: Read error traces carefully. Do not assume or skim. Check every
    hypothesis against the codebase state.
-   **Isolate**: Simplify the problem space. Use mock/stub code, reduce input
    sizes, and strip away unrelated variables to isolate the root cause.
-   **Evidence Over Deduction**: Prioritize actual observations and discrepancy
    investigations over theoretical reasoning. If the code behavior contradicts
    logic, find the physical reason why.
-   **Repeat Failures**: Stop and perform a Root Cause Analysis (RCA) if any tool
    or command execution fails twice for the same operation.

---

## 2. Log Analysis Strategies

-   **Crash Log Triage Order**: When a process dies, always read the **tail** of its
    log first (e.g., `tail -100 <logfile>`). Fatal exceptions, assertion failures,
    and shutdown reasons are written last. Searching the middle of a log first
    wastes significant debugging time.
-   **Boq Framework Debugging**: For Boq servers, look for specific initialization
    errors:
    -   `DependencyVerifier` failures.
    -   `StartupTaskService [FAILED]` errors.
    -   `CreationException` trace patterns.
    These Guice/scope violations produce clear messages but are often buried
    under thousands of lines of verbose startup noise.
-   **Auto-Load Debugging Skills**: When investigating any crash, test failure,
    or unexpected behavior, proactively load the `diagnose` and
    `systematic-debugging` skills. Do not wait for manual direction.

---

## 3. The Diagnostician Pattern

When presenting diagnostic information or proposing logging edits, structure
your responses using the following strict schema:

1.  **The Goal**: A clear, concise statement of the diagnostic goal.
2.  **Hypotheses**:
    -   *High-Confidence*: 2-3 likely root causes.
    -   *Medium-Confidence*: 2-3 potential or secondary causes.
3.  **Diagnostic Steps**: Specific, non-intrusive logging or instrumentation to
    add (without requesting the user to perform it).
4.  **Expected Outcome**: Define what precise log output will confirm or
    disprove each hypothesis.
