# Anti-Patterns Reference Guide

*Derived from common software engineering and LLM development anti-patterns.*

This guide identifies common failure modes when using AI models to modify,
debug, or refactor codebases, along with actionable remediation patterns.

---

## Code Generation & Thinking Failure Modes

| Principle | Anti-Pattern | Fix |
| :--- | :--- | :--- |
| **Think Before Coding** | Silently assumes formats, fields, and scope without verification. | List assumptions explicitly and ask for clarification *before* writing code. |
| **Simplicity First** | Introducing unnecessary abstractions (e.g., Strategy pattern) for a single calculation. | Implement simple, linear code (one function) until complexity actually demands it. |
| **Surgical Changes** | Reformatting unrelated blocks, changing quotes, or adding type hints while fixing a bug. | Only change the precise lines of code that directly fix the reported issue. |
| **Goal-Driven** | Making vague declarations like "I will review and improve the codebase." | Define clear, verifiable steps (e.g., "Write test for bug X -> make it pass -> verify no regressions"). |

---

## Guidelines for Success

These guidelines are working effectively if:
1.  **Fewer Unnecessary Changes**: Your diff contains only targeted edits that map
    directly to the request.
2.  **Less Code Overcomplication**: There are fewer rewrites caused by building
    speculative abstractions.
3.  **Proactive Clarification**: Clarifying questions are raised *before*
    submitting implementation drafts.
