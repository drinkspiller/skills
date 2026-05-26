---
name: markdown-output-hierarchy
description: >-
  Enforces a systematic formatting hierarchy in markdown documentation files.
  Use when creating or editing .md files — covers headers, emphasis, code
  spans, links, admonitions, tables, and lists. Maps six semantic roles to
  markdown primitives with a decision tree for ambiguous cases.
---

# Markdown Output Hierarchy

## When to Use

Apply this system whenever you create or edit a markdown documentation file.
Triggers:

- "write a README"
- "create documentation"
- "format this doc"
- "clean up the markdown"
- "make this doc more readable"
- editing any `.md` file (README, g3doc, changelog, guide)

---

## The System

Six roles, no overlap. Every piece of documentation text gets exactly one:

| Role | Markdown | When to use |
| :--- | :------- | :---------- |
| **Structure** | `**bold**`, `##` headers, `---` rules | Section headings, key term introductions, label text (`**Mode:**`), table headers |
| **Secondary** | *italic*, plain text, parentheticals | Explanatory context, descriptions, caveats the reader can skip, parenthetical asides |
| **Actionable** | `` `inline code` ``, `[links](url)`, fenced code blocks | Commands to run, API names, file paths, URLs, config keys, anything the reader will copy or click |
| **Safe** | ✅ emoji, **bold** positive terms | Success states, "enabled", "complete", "included", "supported", positive confirmations |
| **Caution** | ⚠️ emoji, **bold** caution terms | Non-destructive warnings, deprecation notices, "experimental", "not yet supported", "use with care" |
| **Danger** | 🚨 emoji, **bold** danger terms, blockquote callouts | Breaking changes, data loss risk, security warnings, removal notices. **Never for informational content.** |

### The Hierarchy Rule

When two roles could apply, the **higher-priority** role wins. Priority
order (highest first):

1. Danger
2. Caution
3. Safe
4. Actionable
5. Structure
6. Secondary

---

## Decision Tree for Ambiguous Cases

When you're unsure which role applies, walk this tree:

```
Is this a COMMAND, PATH, API NAME, or URL the reader will copy/click?
  └─ Yes → `inline code` or [link](url) (actionable)

Could this cause DATA LOSS, BREAKAGE, or a SECURITY issue?
  └─ Yes → 🚨 **bold** + blockquote callout (danger)

Does the reader need to NOTICE this but it's not dangerous?
  └─ Yes → Is it positive/confirming?
       └─ Yes → ✅ **bold** (safe)
       └─ No  → ⚠️ **bold** (caution)

Is this a KEY TERM, LABEL, or SECTION HEADING?
  └─ Yes → **bold** or ## header (structure)

Is this EXPLANATORY text the reader can skip?
  └─ Yes → *italic* or plain text (secondary)

None of the above?
  └─ Plain text, no formatting
```

### Common Ambiguous Cases

| Scenario | Tempting choice | Correct choice | Why |
| :------- | :-------------- | :------------- | :-- |
| Function name in a sentence | **bold** | `` `code` `` | It's an actionable API reference, not emphasis |
| "Deprecated" label | `` `code` `` | ⚠️ **bold** | It's a caution state, not something to copy |
| File path in an explanation | *italic* | `` `code` `` | The reader might need to copy/navigate to it |
| "Required" next to a field | ⚠️ caution | **bold** | It's structural metadata, not a warning |
| Config value `true` | **bold** | `` `code` `` | It's a literal value the reader would type |
| "Successfully deployed" | `` `code` `` | ✅ **bold** | It's a positive state, not a copyable string |
| Flag `--verbose` in prose | **bold** | `` `code` `` | It's a literal CLI flag |
| "This will delete all data" | ⚠️ caution | 🚨 **danger** | Data loss = danger, not caution |
| Environment name "staging" | **bold** | `` `code` `` | It's an actionable identifier |
| "Note:" at start of a line | **bold** | *italic* | It's secondary context, not a structural label |

---

## Patterns

### API / CLI Reference Entry

**Structure** for the command name, **Actionable** for flags and values,
**Secondary** for descriptions:

```markdown
### `gcloud app deploy`

Deploy an application to Google App Engine.

**Flags:**

| Flag | Default | Description |
| :--- | :------ | :---------- |
| `--project` | — | *The target GCP project ID.* |
| `--promote` | `true` | *Route all traffic to the new version.* |
| `--no-promote` | — | *Deploy without routing traffic. ⚠️ Requires manual promotion.* |

**Returns:** The deployed version URL.
```

### Step-by-Step Tutorial

**Structure** for step headers, **Actionable** for commands, **Secondary**
for explanations, **Safe** for completion:

```markdown
## Getting Started

### Step 1: Install dependencies

*This installs the core SDK and its peer dependencies.*

`​`​`bash
npm install @example/sdk
`​`​`

### Step 2: Configure your project

Create a config file at `~/.example/config.yaml`:

`​`​`yaml
project: my-app
region: us-central1
`​`​`

### Step 3: Verify

Run the health check:

`​`​`bash
example doctor
`​`​`

✅ **You should see "All checks passed."** You're ready to build.
```

### Configuration Table

**Structure** for headers, **Actionable** for keys and defaults,
**Secondary** for descriptions, **Caution** for constraints:

```markdown
## Configuration Options

| Key | Type | Default | Description |
| :--- | :--- | :------ | :---------- |
| `port` | `number` | `8080` | *The port the server listens on.* |
| `timeout_ms` | `number` | `30000` | *Request timeout.* ⚠️ **Values below 1000 may cause dropped connections.** |
| `log_level` | `string` | `"info"` | *One of:* `"debug"`, `"info"`, `"warn"`, `"error"`. |
| `enable_cache` | `boolean` | `true` | *In-memory response cache.* |
```

### Concept Introduction

**Structure** for the term, **Secondary** for the definition and rationale,
**Actionable** for related code/API:

```markdown
## Circuit Breaker

**Circuit Breaker** is a resilience pattern that prevents cascading failures
by stopping requests to an unhealthy dependency.

*When a downstream service fails repeatedly, the circuit "opens" — all
subsequent calls return immediately with an error instead of waiting for
a timeout. After a cooldown period, the circuit "half-opens" to test
recovery.*

In code, wrap outbound calls with `CircuitBreaker.execute()`:

`​`​`python
breaker = CircuitBreaker(failure_threshold=5, recovery_timeout=30)
result = breaker.execute(lambda: client.get("/health"))
`​`​`
```

### Troubleshooting Entry

**Danger** or **Caution** for the symptom, **Secondary** for the cause,
**Actionable** for the fix:

```markdown
## Troubleshooting

### ⚠️ "Connection refused" on startup

*The server cannot bind to the configured port because another process
is already using it.*

Check what's using the port and kill it:

`​`​`bash
lsof -i :8080
kill -9 <PID>
`​`​`

Then restart:

`​`​`bash
example serve
`​`​`

---

### 🚨 "Data integrity check failed"

*The local cache is corrupted. This typically happens after an unclean
shutdown.*

**This will delete your local cache.** Back up first if needed:

`​`​`bash
cp -r ~/.example/cache ~/.example/cache.bak
example cache --reset
`​`​`
```

### Warning / Breaking Change Callout

**Danger** for breaking changes, **Caution** for deprecations,
**Actionable** for migration commands:

```markdown
> 🚨 **Breaking Change in v3.0:** The `legacy_mode` config key has been
> removed. If your `config.yaml` contains this key, delete it before
> upgrading or the server will fail to start.

> ⚠️ **Deprecated:** `client.fetch()` is deprecated and will be removed
> in v4.0. Use `client.request()` instead. See the
> [migration guide](./migration-v4.md).
```

### Code Example with Explanation

**Actionable** for the code block, **Secondary** for line-by-line
explanations, **Structure** for the section label:

```markdown
### Example: Retry with exponential backoff

`​`​`python
import time

def retry(fn, max_attempts=3, base_delay=1.0):
    for attempt in range(max_attempts):
        try:
            return fn()
        except Exception as e:
            if attempt == max_attempts - 1:
                raise
            delay = base_delay * (2 ** attempt)
            time.sleep(delay)
`​`​`

*The `base_delay` doubles after each failure (`1s → 2s → 4s`), giving
the downstream service time to recover without overwhelming it with
retries.*
```

### Before / After Migration Guide

**Structure** for labels, **Actionable** for code, **Caution** for
what changed, **Safe** for the result:

```markdown
## Migrating from v2 to v3

⚠️ **The `init()` function signature has changed.** The `options` parameter
is now required.

**Before (v2):**

`​`​`python
client = Client.init()
`​`​`

**After (v3):**

`​`​`python
client = Client.init(options=ClientOptions(region="us-central1"))
`​`​`

✅ **After updating all call sites**, run the migration validator:

`​`​`bash
example migrate --check
`​`​`
```

---

## Anti-Patterns

1. **Bold everything** — If everything is bold, nothing is. Reserve `**bold**`
   for structural labels and role-specific emphasis only.

2. **Code spans for emphasis** — `` `don't do this` `` for words that aren't
   code. Use **bold** or *italic* instead. Code formatting implies "this is
   a literal, copyable value."

3. **Admonitions for routine info** — Callout blocks (blockquotes with emoji)
   are for genuinely exceptional situations. Don't use 🚨 or ⚠️ for things
   the reader expects.

4. **Naked links** — `https://example.com` is hard to scan. Always use
   descriptive link text: `[Example docs](https://example.com)`.

5. **Formatting salad** — Using bold + italic + code in one phrase:
   ***`don't`***. Pick one role per span.

6. **Headers as emphasis** — `### Don't use headers just to make text big`.
   Headers create navigable structure. If you need emphasis within a
   paragraph, use **bold**.

7. **Emoji overload** — ✅ and ⚠️ carry meaning in this system. Don't mix in
   decorative emoji (🎉 🚀 💡) — they dilute the signal.
