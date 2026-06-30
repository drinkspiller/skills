# Workspace & Version Control Workflows

This guide outlines standards for managing the workspace, version control
history, formatting verification, and pushing modifications safely.

---

## 1. Pre-Push Guardrails & Formatting

-   **Pre-Push Checks**: Before running `git push`, always execute local linting
    and formatting tools (e.g., `pnpm lint`, `pnpm format:check`, or
    project equivalents).
-   **Correct Violations**: If any check fails, run formatting or auto-fix commands
    (e.g., Prettier, linter fixes) on the affected files before committing.
-   **Pristine History**: Never commit formatting fixes as subsequent commits.
    Always amend them directly into the relevant work commit.

---

## 2. Commit & Git Workflows

-   **Conventional Commits**: Commit messages must follow the Conventional Commits
    specification:
    -   `feat(scope): add new validation rules`
    -   `fix(scope): resolve null pointer exception in parser`
    -   Format: `<type>(<scope>): <short description>` followed by a detailed body
        explaining the *what* and *why* if appropriate.
-   **Commit Amending & Interactive Rebase**:
    -   Use `git commit --amend` to update the most recent commit with staged
        changes or update the message.
    -   Use interactive rebase (`git rebase -i <base>`) to squash, reorder, or edit
        commits before sharing.
-   **Safe Pushing**:
    -   Always verify that you are pushing to the correct branch.
    -   Use `--force-with-lease` instead of a blind `--force` when pushing to a
        shared branch where commits might have been amended.
