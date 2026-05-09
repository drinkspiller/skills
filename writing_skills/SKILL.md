---
name: writing-skills
description: Guides the creation, editing, and maintenance of Agent Skills. Consult when modifying SKILL.md files to ensure best practices.
---

# Writing Effective Agent Skills

Skills are reusable packages of knowledge and capabilities that extend an
agent's potential. This guide details how to write skills that are discoverable,
efficient, and reliable.

## Core Principles

### 1. Concise is Key

The context window is a shared resource. Every token in your skill competes with
conversation history and other active contexts.

*   **Assume Competence**: The agent is already smart. Don't explain concepts it
    likely knows (e.g., "PDFs are Portable Document Format...").
*   **Focus on the Delta**: Only document what is specific to *this* task, tool,
    or environment.

### 2. Progressive Disclosure

Don't dump everything into `SKILL.md`. Use a hierarchical structure:

*   **L0 (Metadata)**: `name` and `description` are ALWAYS loaded. Make them
    perfect.
*   **L1 (Overview)**: `SKILL.md` is loaded when the skill is *activated*. Keep
    it under 500 lines.
*   **L2 (Details)**: `references/`, `scripts/`, and `examples/` are loaded *on
    demand*.

### 3. Solvable, Not Just Descriptive

Effective skills offer *capabilities* and *toolkits*, not just *documentation*.

**Crucially, distinguish between a Skill and a Workflow:**

*   **Skill (Flexible Toolkit)**: Use for situational tasks requiring agent
    judgment, branching logic, or optional steps. Frame these as "Key Actions"
    or "Capabilities" rather than sequential steps.
*   **Workflow (Rigid Script)**: Use for deterministic, linear tasks that must
    be executed in an exact order. (See the `gemini-workflows` skill for
    details).
    *   **Bad**: "You can use the `requests` library to fetch the URL."
    *   **Good**: "Run `scripts/fetch_data.py <url>` to get the JSON response."

## Skill Structure

A standard skill looks like this:

```
my_skill_folder/          # snake_case (Google3 convention)
├── SKILL.md              # Entry point (Required)
├── scripts/              # Executable helpers (Libraries, Binaries)
├── references/           # Detailed documentation (loaded on demand)
│   ├── api_docs.md
│   └── templates.md
└── resources/            # Static assets, images, etc.
```

### The `SKILL.md` File

Must start with YAML frontmatter:

```yaml
---
name: my-skill-name       # kebab-case (Standard convention)
description: A concise, third-person description of what the skill does and when to use it.
---
```



#### The Description (CRITICAL)

The `description` is the **only** thing the agent sees before selecting a skill.
It determines discovery.

*   **Gerund Name**: Use the gerund form (verb + -ing) for names (e.g.,
    `debugging-spanner`). Max 64 characters.
*   **Third Person**: "Extracts text from PDFs..." (NOT "I can help you...").
    Max 1024 characters.
*   **Trigger-Focused**: Include *when* to use it. "Use when debugging Flume
    pipelines or analyzing log protos."
*   **Keywords**: Include specific terms users might say (e.g., "BigQuery",
    "Spanner", "cherry-pick").

## Best Practices

### Writing Instructions

*   **Show, Don't Tell**: Use examples. Input/Output pairs are often clearer
    than prose.
*   **Consistent Terminology**: Pick one term (e.g., "Replica" vs "Task") and
    stick to it.
*   **Avoid Time-Sensitivity**: Don't write "As of 2024...". If needed, put
    legacy patterns in a separate reference section.
*   **Be Accurate**: Use real paths (e.g., `google3/...`) and valid syntax.
    Don't guess.

### Scripting & Automation

*   **Encapsulate Complexity**: If a task involves more than 2-3 manual steps
    (especially if they involve finding IDs or cross-referencing files), create
    a script in `scripts/`. This reduces agent error and fatigue.
*   **Relative Paths**: Always reference scripts using relative paths within the
    skill documentation (e.g., `scripts/find_cl.sh`, **NOT**
    `/absolute/path/to/scripts/find_cl.sh`).
*   **Language Choice**:
    *   **Bash**: Best for wrapping linear shell commands (e.g., `g4`, `grep`,
        `sed`).
    *   **Python**: Best for parsing complex outputs, JSON processing, or
        rigorous logic.
*   **Environment Assumptions**: You can assume standard Google-specific tools
    (`g4`, `blaze`, `hg`, `code_search`) are available in the path. You do not
    need to check for their existence.

### Creating and Updating Skills

*   **Use Version Control (CRITICAL)**:
    *   **NEVER** create or edit files in `~/.gemini/gemini/skills` or
        `gemini/global_skills`. These are local caches and your changes **WILL
        BE LOST**.
    *   **ALWAYS** work in google3 version control.
    *   **For NEW skills**: Create them under
        `//experimental/users/<username>/.../<skill_name>/`. Each user may have
        their own preferred location, find it if not obvious.
    *   **For EXISTING skills**: Use `code_search` to find the actual source
        file in google3 and edit that instead.
*   **Respect Context**: When editing existing skills, respect the original
    structure unless explicitly asked to refactor. Avoid drastic changes.
*   **Preserve Details**: Err on the side of caution. Do not remove details from
    existing skills unless you are certain they are unnecessary.

## Implementation Patterns

*   **Structured I/O**: Use **JSON** for complex configurations instead of
    markdown tables to ensure the model parses the data reliably.
*   **CLI Cheat Sheet**: Instead of a full automation, provide a "power-user
    manual" for existing CLIs that explains tricky flags and error codes the
    model usually misses.

## Anti-Patterns

*   **The "Everything Bagel"**: Avoid one massive skill covering unrelated
    topics.
*   **Performative Padding**: Avoid "polite" language ("I am happy to help")
    that wastes tokens without adding value.
*   **Static Stale Data**: Do not include raw UUIDs, temporary paths, or
    hardcoded dates that will quickly become stale.

### Authoring Checklist

-   [ ] **Naming**: Is the name in gerund form (verb + -ing) and under 64
    characters?
-   [ ] **Discovery**: Does the description clearly state *what* it does in the
    third person?
-   [ ] **Conciseness**: Is `SKILL.md` < 500 lines? Are details moved to
    `references/`?
-   [ ] **Structure**: Are references one level deep? (Avoid chains like `A -> B
    -> C`).
-   [ ] **Utility**: Does it provide *actions* (scripts/workflows) rather than
    just advice?
-   [ ] **Formatting**: Are file paths using forward slashes (`/`)?
-   [ ] **Verification**: Did you include build/test commands?
-   [ ] **Source Validity**: Are you editing the google3 source file, NOT the
    local cache?
