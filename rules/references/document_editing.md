# Document Editing & Code Preservation Guide

This reference document establishes the guidelines for editing existing files,
preserving document structure, and applying surgical modifications safely.

---

## 1. Editing Guardrails

-   **No Full-Document Overwrites**: Avoid full-file overwrites (`write_to_file`
    with overwrite) to preserve token bandwidth and prevent clobbering un-analyzed
    code blocks. Always prefer targeted, surgical chunk replacements
    (`replace_file_content` / `multi_replace_file_content`).
-   **Mandatory Inspection**: Proactively inspect a document's layout, style,
    and tab/indentation patterns before making any modifications.
-   **Method Boundaries**: Keep method/function edits concise (ideally under 30
    lines). Limit indentation nesting to a maximum of 3 levels.
-   **Newline Preservation**: All edited and new files must terminate with a
    single trailing newline.

---

## 2. Surgical Changes Rules

When editing existing source code:
-   **Scope Isolation**: Do not "improve" or reformat adjacent code, comments,
    or spacing. Focus strictly on the required edit.
-   **Style Matching**: Match the surrounding style, naming conventions, and
    idioms exactly. Do not refactor code that is not broken.
-   **Dead Code**:
    -   Remove any imports, variables, or functions that *your changes* made
        unused.
    -   Do not remove pre-existing dead code unless explicitly requested. Mention
        it in your response if appropriate.
-   **The Traceability Test**: Every single line changed or added must trace
    directly back to the user's specific request.
