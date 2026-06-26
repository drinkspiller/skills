---
name: skill-creator
description: >-
  Creates new AI agent skills, modifies and improves existing ones, and iterates on skill
  quality through structured evaluation. Use when creating a skill from scratch,
  improving an existing skill's instructions or triggering, running ablation
  tests to measure skill value (with-vs-without skill), reviewing skills,
  or diagnosing why a skill doesn't trigger or produces wrong output. Also use
  when capturing a recurring workflow as a reusable skill. Don't use for general 
  code changes outside skill directories.
---

# Skill Creator

A generalized guide and workflow for creating and iteratively improving AI agent skills.

## What Skills Are

Agent skills are opinionated cheatsheets. They encode what the agent gets wrong without help — the gotchas, the exact commands, the conditional logic, and the "do this, not that" decisions that turn an unreliable agent into a reliable one.

A skill's value is the delta between the agent with the skill and the agent without it. If the agent already handles a task well out-of-the-box, a skill adds noise without value. If the agent consistently fails without specific guidance, that guidance is the skill.

Skills are **NOT**:
- **Documentation or tutorials** — leave general explanatory text to standard project documentation.
- **Full applications or libraries** — complex code bases belong in standard application repositories.
- **One-off scripts** — the agent can write ephemeral scripts itself.

**Create a skill when** the agent fails reliably without one, the workflow recurs, and consistency matters. **Don't create one** for one-off tasks, things the agent already handles well, or workflows that change frequently.

---

## Core Principles

### 1. Experience Before Theory
Try the task before writing the skill. Run typical user prompts yourself without any skill loaded and observe where the failures occur. The actual roadblocks and gotchas you discover are the true content of the skill. Speculation about what *might* go wrong produces noise; real experience produces signal.

### 2. Explain the Why
AI models comply better with understood intent than with rigid, unexplained directives. When you explain *why* an instruction exists, the model can generalize the rule to edge cases that the instruction doesn't literally cover.

- ❌ `Always use ripgrep (rg) instead of grep.`
- ✅ `Use ripgrep (rg) instead of grep — ripgrep respects .gitignore by default and avoids searching large dependency directories like node_modules.`

If you find yourself writing `ALWAYS` or `NEVER` in caps, pause and ask if you can explain the causal rationale instead.

### 3. Signal, Not Noise
Every line in a skill must earn its place in the context window. 

**Signal (keep):**
- Gotchas from real failure modes.
- Exact command patterns with concrete flags and values.
- Domain-specific business logic and branching workflows.
- Anti-patterns the agent defaults to without warning.

**Noise (remove):**
- Boilerplate the agent already knows (e.g., "always validate your output").
- Verbose explanations of basic concepts the model understands from base training.
- Redundant restatements of the same instruction.

### 4. One Job Well
Each skill should do one focused job. If describing a skill requires "and" between unrelated capabilities, split it into separate skills. Broad skills trigger unreliably because their descriptions cannot be specific enough to match diverse user intents accurately.

### 5. Generalize, Don't Overfit
You will test your skill against a few specific cases, but it will eventually run on hundreds of diverse prompts. After adding a rule or fix, ask: *"Will this help on a prompt I haven't seen yet, or did I just hardcode a workaround for my specific test case?"*

### 6. Verify, Don't Trust
Every instruction should lead to a verifiable state. Include runnable validation commands, expected output patterns, or concrete success criteria so the agent can self-correct if it makes a mistake.

### 7. Bundle What Repeats
If the agent independently writes similar helper scripts or code snippets across multiple runs, that is a strong signal the skill should bundle that code. Place reusable utilities in a `scripts/` subdirectory to save future invocations from reinventing the wheel.

---

## The Creation Lifecycle

Creating a skill is an iterative product development process: **Understand → Experience → Draft → Evaluate → Improve**.

### Phase 1: Understand
1. **Check for duplicates**: Ensure a similar skill doesn't already exist in your workspace or organization catalog.
2. **Collect representative prompts**: Gather 2–5 realistic user requests that this skill should handle.
3. **Define success criteria**: Clearly define what verifiable state indicates the task was completed successfully.

### Phase 2: Experience
Run through the representative prompts manually or have the base agent attempt them **without the skill**. Note:
- Where did the agent get stuck or hallucinate flags?
- What secondary tools or command-line flags were required to fix errors?
- What fallback strategies worked when primary methods failed?

### Phase 3: Draft
Create the directory structure for your skill:
```text
my_skill/
├── SKILL.md              # Main metadata and instructions
├── scripts/              # Optional helper scripts for deterministic tasks
└── references/           # Optional detailed docs loaded on demand
```

1. **Write the YAML Frontmatter**: Craft a precise `name` and `description` (see rules below).
2. **Write the Body**: Use imperative phrasing ("Run the validator", not "You should run..."). Provide concrete input-to-output examples.
3. **Keep it modular**: If the skill requires large schemas or extensive reference tables, place them in `references/` and link to them directly from `SKILL.md`.

### Phase 4: Evaluate & Improve
Test the skill by running the representative prompts again with the skill enabled. 
- **Compare performance**: Does the agent complete the task faster, cheaper, or more reliably than without the skill?
- **Diagnose failures**: If the agent ignores the skill, refine the frontmatter `description`. If it follows the skill but fails, refine the instructions in the body.
- **Iterate**: Strip out instructions that don't change behavior, and refine the ones that do.

---

## Crafting the Frontmatter Description

The `description` field in the YAML frontmatter is critical — it is the **only** text the agent reads when deciding whether to trigger and load the full skill.

### Rules for Descriptions
1. **Third-Person Capability Statement**: Start with what the skill does (e.g., *"Analyzes Dockerfiles and optimizes build caching..."*). Avoid first/second person (*"I can help you"*).
2. **Include Triggers**: Explicitly state `"Use when..."` followed by typical user intents.
3. **Include Negative Triggers**: State `"Don't use for..."` to prevent false-positive triggering on related but distinct tasks.
4. **Avoid Internal Jargon**: Use general domain concepts so the model recognizes the relevance even if the user rephrases their prompt.

### Example

❌ **Bad (Vague, lacks triggers):**
```yaml
description: >-
  Helper tools for working with databases and queries.
```

✅ **Good (Specific, includes positive and negative triggers):**
```yaml
description: >-
  Analyzes PostgreSQL query plans and optimizes slow SQL joins and indexes. 
  Use when debugging high database latency, inspecting EXPLAIN ANALYZE output, 
  or resolving table lock contention. Don't use for general schema migrations 
  or database setup tasks.
```
