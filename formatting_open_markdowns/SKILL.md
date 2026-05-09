---
name: formatting-open-markdowns
description: Formats all currently open markdown files in the editor using mdformat. Use when requested to format open files or active documents.
---

# Formatting Open Markdowns

This skill provides instructions for formatting all markdown files that are currently open in the user's editor.

## Triggers

- "format open markdown files"
- "mdformat open files"
- "format active document if it's markdown"

## Procedure

1.  **Identify open files**: Look at the `Active Document` and `Other open documents` in the `User Environment` or `ADDITIONAL_METADATA` section of the prompt.
2.  **Filter for Markdown**: Select only those files that have the `.md` extension or are labeled as `LANGUAGE_MARKDOWN`.
3.  **Run mdformat**: For each identified file, execute the following command to format it in-place:

```shell
/google/bin/releases/corpeng-engdoc/tools/mdformat --in_place {file_path}
```

Replace `{file_path}` with the absolute path of the file.

## Example

If the user has `/google/src/cloud/skyebot/<some_workspace>/google3/labs/language/mixboard/README.md` open:

```shell
/google/bin/releases/corpeng-engdoc/tools/mdformat --in_place /google/src/cloud/skyebot/<some_workspace>/google3/labs/language/mixboard/README.md
```
