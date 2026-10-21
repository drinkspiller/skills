---
name: handoff
description: Compact the current conversation into a handoff document for another agent to pick up and reply with a copy-pastable prompt containing the full handoff path. Can accept arguments describing what the next session will focus on to tailor the document.
---

# Handoff Skill

<!-- Originally based on https://github.com/mattpocock/skills/tree/main/skills/productivity/handoff -->

Write a handoff document summarising the current conversation so a fresh agent
can continue the work.

## Instructions

1.  **Generate Handoff File Path**: Generate a temporary file path using `mktemp
    -t handoff-XXXXXX.md`.
2.  **Read Before Write**: Read the file (or verify it is empty/accessible)
    before writing to it to ensure permissions.
3.  **Separate Signal from Noise**: Before writing, mentally separate actionable
    context (decisions, requirements, designs, pending work) from noise (debug
    logs, raw tool output, abandoned ideas, transient snippets). Only the signal
    goes into the handoff document.
4.  **Gather Remaining Work**: Actively search for outstanding work items. This
    is critical — handoffs that omit remaining work cause the next session to
    miss important context.
    -   **Project plans / task trackers**: Check for any structured plan that
        was active during the conversation (e.g. a project management framework
        like Conductor, Linear, Jira, or GitHub Projects; a `plan.md` or TODO
        list; a design doc action-items section; or any markdown file with task
        checkboxes). List all unchecked (`- [ ]`) items, grouped by phase or
        category. Reference the plan file path rather than copying full task
        descriptions.
    -   **Open issues**: If issue-tracker items (e.g. Buganizer, Jira, GitHub
        Issues, Linear) were referenced or created during the conversation,
        fetch each one and include its ID, title, status, and dependency chain.
        Note which issues block others.
    -   **Open PRs / CLs**: Check for any pull requests or changelists that were
        created or modified but not yet merged/submitted. Include their review
        status.
    -   **Conversation context**: Scan the conversation for any explicit
        follow-up items the user mentioned or acknowledged (e.g. "we'll do X
        later", "TODO: Y").
5.  **Write with a Two-Pass Structure**: First, write a 2-3 sentence **anchor
    summary** that captures the core state of the project right now. Then expand
    around that anchor with the following sections:
    -   **Conversation lineage** — include the current session/conversation ID
        and any relevant related conversation IDs (e.g., from sub-sessions,
        parent sessions, or parallel tracks) to allow tracing the history if the
        summary is insufficient.
    -   What has been completed (with CL/PR numbers and merge status).
    -   **Remaining work** — the items gathered in step 4, organised by
        priority. Include dependency chains where they exist.
    -   **Known issues / risks** — blockers, flaky infrastructure, environmental
        gotchas, or unresolved ambiguities that are not yet tracked as formal
        issues but would trip up the next session.
    -   **Problem-solving history** — document what was tried and failed, dead
        ends, and rejected approaches so the next session does not repeat them.
        Include error messages or symptoms where relevant.
    -   **Key technical concepts** — list technologies, coding conventions,
        architectural patterns, and domain terms discussed that a fresh agent
        would need to calibrate on.
    -   Key file references (table of paths and URLs), with a brief note on why
        each file matters or what changed in it.
    -   **Next steps** (place this last in the document for maximum visibility):
        recommended execution order and suggested skills to be used by the next
        session.
6.  **Avoid Duplication**: Do not duplicate content already captured in other
    artifacts (PRDs, plans, task trackers, issues, commits, diffs). Reference
    them by path or URL instead. For plan files with checkboxes, list only
    unchecked items — do not repeat checked ones.
7.  **Tailor to Next Steps**: If the user passed arguments or specified what the
    next session will focus on, tailor the handoff document accordingly to
    emphasize relevant context.
8.  **Output Path & Copy-Pastable Next-Agent Prompt**: Always inform the user of
    the full path where the handoff document was saved, and **always** include a
    copy-pastable prompt (in a fenced `text` code block) for the user to paste
    into the next agent session. The prompt must include the full path to the
    handoff document and a brief directive on what to pick up next. For example:

    ```text
    Read /tmp/handoff-XXXXXX.md to load context from the previous session, then continue with the Next Steps section.
    ```
