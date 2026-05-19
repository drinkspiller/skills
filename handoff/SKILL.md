---
name: handoff
description: Compact the current conversation into a handoff document for another agent to pick up. Can accept arguments describing what the next session will focus on to tailor the document.
---

# Handoff Skill

Write a handoff document summarising the current conversation so a fresh agent
can continue the work.

## Instructions

1.  **Generate Handoff File Path**: Generate a temporary file path using `mktemp
    -t handoff-XXXXXX.md`.
2.  **Read Before Write**: Read the file (or verify it is empty/accessible)
    before writing to it to ensure permissions.
3.  **Content to Include**:
    *   Summary of the current state of the task.
    *   What has been completed.
    *   What is pending.
    *   Next steps.
    *   Suggest the skills to be used, if any, by the next session.
4.  **Avoid Duplication**: Do not duplicate content already captured in other
    artifacts (PRDs, plans, Conductor track spec / project guidelines, issues,
    commits, diffs). Reference them by path or URL instead.
5.  **Tailor to Next Steps**: If the user passed arguments or specified what the
    next session will focus on, tailor the handoff document accordingly to
    emphasize relevant context.
6.  **Output Path**: Inform the user of the path where the handoff document was
    saved.
