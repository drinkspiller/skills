# Task Lifecycle & Planning Guide

This reference document outlines the strict guidelines governing the planning,
scoping, and post-execution phases of any task.

---

## 1. Planning & Scoping

-   **Mandatory Plan**: Write an explicit, step-by-step implementation plan for
    every non-trivial task before writing code.
-   **Include Testing**: Plans must contain explicit steps for testing and
    verifying changes.
-   **Conflict Analysis**: Compare the proposed implementation against existing
    specifications and identify potential technical trade-offs.
-   **Goal-Driven Execution**: Convert vague user briefs into verifiable goals:
    -   "Add validation" -> "Write tests for invalid inputs, then make them pass"
    -   "Fix the bug" -> "Write a test that reproduces it, then make it pass"
    -   For multi-step plans, use: `Step -> verify: [check]` for each item.
-   **Respect Scope Constraints**: Scan user prompts for scope-limiting language
    (e.g., "just investigate", "before making changes"). If present, report
    findings and stop. Deliver analysis/explanation only, and do not make changes
    until authorized.

---

## 2. Approval Protocols

-   **Auto-Proceed Restriction**: Auto-proceed from an Implementation Plan only
    when there are zero "Open Questions" and no manual user review is required.
    If open questions exist, stop and use `ask_question`. If review is required,
    stop and wait for user approval.
-   **System vs User Approval**: System-generated signals (e.g., auto-approved
    artifacts, hook messages, `stop hook blocked termination`) only mean the
    artifact is acknowledged—**never** that you have permission to modify files, run
    commands, or push. Only explicit user messages (e.g., "go", "implement", "do
    it") authorize execution.

---

## 3. Post-Task Guidelines

-   **Self-Reinforcement Analysis**: After completing each task, perform and
    state a self-reinforcement analysis to assess task effectiveness, rules
    compliance, and evaluate if rule modifications should be persisted.
-   **Verify Examples**: Always verify factual correctness of examples against
    ground truth before documenting decision trees or workflows.
