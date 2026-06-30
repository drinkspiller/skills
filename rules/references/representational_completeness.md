# Representational Completeness Guide

Representational completeness ensures that communications, documentation, and
rationale are completely articulated without omissions, distortions, or overly
broad generalizations.

---

## 1. Anti-Deletion: Recover what was left out

-   **State the "Why"**: Every action or decision must include its causal
    rationale. Avoid proposing a change without explaining *why* it is necessary.
-   **Specify Every Referent**: Nouns are incomplete without their objects. Do not
    refer to generic entities (e.g., "the module" or "it") without specifying
    the exact component or variable name.

---

## 2. Anti-Distortion: Unfreeze nominalizations

-   **Demonstrate, Don't Label**: Unpack static labels or high-level abstract
    descriptions with a concrete instance showing the actual process in action.
    -   ❌ "Implement verification to ensure data validity."
    -   ✅ "Write tests that submit negative values, and ensure they return a
        `400 Bad Request` status."

---

## 3. Anti-Generalization: Bound universal claims

-   **Make the Specific Instance the Sentence**: State the concrete case directly
    and explicitly instead of wrapping it in generic introductory structures
    like "For example".
    -   ❌ "Users might experience issues under certain conditions. For example,
        if the API times out..."
    -   ✅ "If the downstream API times out after 400ms, the system returns a
        cached fallback response."
