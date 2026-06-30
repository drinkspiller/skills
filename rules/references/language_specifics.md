# Language-Specific Coding Standards

This guide outlines language-specific rules and patterns that must be adhered
to when writing or editing code.

---

## 1. TypeScript Standards

-   **Strict Typing**: Ensure strict type checking is enabled. Never use `any` as
    a catch-all escape hatch. Leverage precise union, intersection, or utility
    types.
-   **Iteration**: Use `for...of` loops for arrays and iterables instead of raw
    index-based loops or `.forEach`, unless functional mapping is more readable.
-   **Promise Handling**: Floating promises are strictly forbidden. Always
    explicitly handle promise rejections (e.g., using `await`, `.catch()`, or
    wrapping in `try...catch` blocks).
-   **Discriminated Unions**: Structure complex conditional data models using a
    distinguishing `kind` field. Implement corresponding type guards to narrow
    types safely.

---

## 2. Python Standards

-   **Type Hints**: Always include explicit type hints for new or modified
    function signatures (including arguments and return types).
-   **String Formatting**: Exclusively use modern f-strings (`f"value: {val}"`)
    for string interpolation. Avoid old `%` formatting or `.format()` calls.
