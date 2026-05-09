<!-- glint: disable=DevSiteLinter_g3doc -->
<!-- linter off -->
---
name: Ralph Loop
description: Run iterative, self-referential AI development loops. Use when asked to "ralph loop", "iterate until done", "keep trying until tests pass", or for tasks requiring persistent iteration with clear completion criteria.
---

# Ralph Loop

Implements the Ralph Wiggum technique for iterative, self-referential AI
development loops in Jetski. Named after Ralph Wiggum from The Simpsons,
embodying the philosophy of persistent iteration despite setbacks.

## When to Use

**Good for:**

-   Well-defined tasks with clear success criteria
-   Tasks requiring iteration and refinement (e.g., getting tests to pass)
-   Greenfield projects where you can walk away
-   Tasks with automatic verification (tests, linters, builds)

**Not good for:**

-   Tasks requiring human judgment or design decisions
-   One-shot operations
-   Tasks with unclear success criteria
-   Production debugging (use targeted debugging instead)

## Core Concepts

### The Loop

```
while not complete:
    1. Work on task
    2. Check completion criteria
    3. If not complete, iterate with same prompt
    4. Previous work persists in files/git
```

### Completion Promise

A `<promise>PHRASE</promise>` tag that signals genuine completion. The agent
MUST NOT output this until the statement is completely and unequivocally TRUE.

### Max Iterations

Safety limit to prevent infinite loops on impossible tasks.

## Usage

### Starting a Ralph Loop

Use the `/ralph_loop` workflow:

```
/ralph_loop "Build a REST API for todos. Requirements: CRUD operations, input validation, tests."
```

Or invoke directly:

```
Start a Ralph loop with:
- Task: <description>
- Completion promise: <phrase that signals done>
- Max iterations: <number>
```

### State File

The loop state is tracked in `.ralph-loop-state.json`:

```json
{
  "active": true,
  "iteration": 1,
  "max_iterations": 50,
  "completion_promise": "ALL TESTS PASSING",
  "started_at": "2026-03-18T23:00:00Z",
  "prompt": "Build a REST API..."
}
```

### Checking Status

```bash
cat .ralph-loop-state.json | jq .
```

### Canceling

Delete the state file or use `/cancel_ralph`:

```bash
rm .ralph-loop-state.json
```

## Writing Effective Prompts

### 1. Clear Completion Criteria

❌ Bad: "Build a todo API and make it good."

✅ Good:

```
Build a REST API for todos. When complete:
- All CRUD endpoints working
- Input validation in place
- Tests passing (coverage > 80%)
- README with API docs
Output: <promise>COMPLETE</promise>
```

### 2. Incremental Goals

❌ Bad: "Create a complete e-commerce platform."

✅ Good:

```
Phase 1: User authentication (JWT, tests)
Phase 2: Product catalog (list/search, tests)
Phase 3: Shopping cart (add/remove, tests)
Output <promise>COMPLETE</promise> when all phases done.
```

### 3. Self-Correction

❌ Bad: "Write code for feature X."

✅ Good:

```
Implement feature X following TDD:
1. Write failing tests
2. Implement feature
3. Run tests
4. If any fail, debug and fix
5. Refactor if needed
6. Repeat until all green
7. Output: <promise>COMPLETE</promise>
```

### 4. Escape Hatches

Always set max iterations as a safety net:

```
After 15 iterations, if not complete:
- Document what's blocking progress
- List what was attempted
- Suggest alternative approaches
```

## Implementation

### Loop Execution Pattern

When running a Ralph loop, follow this pattern each iteration:

1.  **Read State**: Check `.ralph-loop-state.json` for current iteration
2.  **Execute Task**: Work on the prompt
3.  **Check Completion**: Evaluate if completion criteria are met
4.  **Output Promise**: If genuinely complete, output
    `<promise>PHRASE</promise>`
5.  **Iterate**: If not complete, increment iteration and continue

### Critical Rules

-   **Never lie to exit**: Do NOT output a false promise to escape the loop
-   **Trust the process**: Even if stuck, continue iterating
-   **Document progress**: Each iteration should make measurable progress
-   **Check files**: Your previous work persists - read and build on it

## Reference

-   Original technique: https://ghuntley.com/ralph/
-   Claude Code plugin:
    https://github.com/anthropics/claude-code/tree/main/plugins/ralph-wiggum
