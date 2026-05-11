---
name: tech-doc-codelab
description: >-
  Write technical documentation and hands-on codelabs for software concepts,
  frameworks, and architectures. Use when asked to "document this", "explain how
  X works", "write a codelab for", "walk me through", or "teach me about" a
  technical topic. Produces markdown docs and step-by-step exercises.
---

# Technical Documentation & Codelabs

Two modes, one skill. Use **Doc mode** to explain a concept. Use **Codelab
mode** to teach it through a guided exercise. The user may ask for one or both.

## Before You Write

1.  **Confirm the topic.** If the user didn't provide one, ask. Don't guess.
2.  **Gather context.** If the user supplied reference docs, code, or links,
    read them first. Search the codebase or internal docs if you need more.
3.  **Pick the mode.** If the request says "explain" or "document", use Doc
    mode. If it says "walk me through" or "codelab", use Codelab mode. If both,
    write the doc first, then the codelab.

## Doc Mode

Write a standalone markdown document that covers the topic. Follow this
structure, dropping any section that doesn't apply:

### Structure

```
# [Topic Title]

One paragraph: what it is, why it exists, what problem it solves.

## Key Concepts

Short definitions. No fluff. Use a term list or bullets. Define jargon here
so later sections can use it without re-explaining.

## How It Works

Walk through the mechanics. Describe the components, what each one does, and
how they connect. Use a mermaid diagram if the relationships are non-trivial.

### [Component Name]

- What it does
- What it owns
- How it relates to other components

## When to Use It

Concrete scenarios where this concept applies. Real examples from the
codebase or domain, not hypotheticals.

## Trade-offs

What you gain. What you give up. No "despite its challenges" hedging -- just
state the costs plainly.

## Code Example

A short, focused snippet that shows the concept in action. One concept per
snippet. Annotate with inline comments where the code alone isn't clear.
```

### Doc Mode Rules

-   **Lead with the point.** First sentence of every section should be the
    actual information, not a setup for it.
-   **Be specific.** Name real files, classes, and functions. Don't say "the
    relevant module" when you can say `//foo/bar:baz`.
-   **Skip the pedagogy.** Don't write "Let's explore" or "Think of it as". Just
    state the thing.
-   **One idea per section.** If you're covering two ideas, make two sections.
-   **Code over prose.** If a 10-line snippet explains it better than three
    paragraphs, use the snippet.

## Codelab Mode

Write a hands-on exercise that builds something real. The reader should have
working code at the end.

### Structure

~~~
# [Codelab Title]

## What You'll Build

One sentence. What the reader will have at the end of this exercise.

## Prerequisites

- Tools, access, packages needed
- Assumed knowledge (be honest about what you expect them to know)

## Steps

### Step 1: [Verb phrase] (e.g., "Set up the workspace")

What to do, why, and the exact commands or code.

**Do this:**
```language
actual code or command
~~~

**What happened:** Brief explanation of what that code did and why it matters
for the next step.

### Step 2: [Next verb phrase]

...

## Verify It Works

How to confirm the exercise succeeded. Exact command, expected output.

## What You Learned

Three to five bullet points. No summaries of summaries.

## Going Further (optional)

Pointers to next steps, related concepts, or extensions they could try. ```

### Codelab Mode Rules

-   **Assume nothing silently.** If a step requires knowledge you haven't
    covered, say so in Prerequisites. Don't let readers hit a wall mid-step.
-   **Every step must do something.** No steps that are just explanation. Each
    step should produce a change the reader can see or verify.
-   **Show the actual output.** After commands, show what the reader should
    expect to see. This is how they know they're on track.
-   **Explain forward, not backward.** When explaining why a step matters, say
    what it enables in future steps, not what led up to it.
-   **Keep steps small.** If a step takes more than 5 minutes or changes more
    than ~20 lines, split it.
-   **Name the file.** Every code block that the reader should write into a file
    needs to say which file, with a full path.

## Style Guide (Both Modes)

Read [references/style_rules.md](references/style_rules.md) before writing. Key
points:

-   **No throat-clearing.** Cut introductory filler. Start with the content.
-   **No false drama.** Don't inflate stakes. A latency metric is a latency
    metric, not a "fundamental shift in how we think about performance".
-   **Straight language.** Use "is" instead of "serves as". Use "shows" instead
    of "highlights". Use "because" instead of "not because X, but because Y".
-   **Minimal em-dashes.** Two per document max.
-   **No bold-first bullets.** Don't start every list item with `**Keyword**:`.
-   **Concrete > abstract.** Numbers, file paths, class names, and output
    snippets beat vague descriptions every time.

## Adapting to a Style Example

If the user provides an existing document as a style reference:

1.  Match its heading depth, section ordering, and level of detail.
2.  Match its tone (formal vs. conversational, dense vs. spacious).
3.  Don't match its anti-patterns. If the style example has AI tropes, drop
    them. Write it the way a careful human editor would.
