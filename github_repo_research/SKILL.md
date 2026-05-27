---
description: Robust strategy for researching a public repository — discovering documentation, configuration schemas, and API surfaces. Use when investigating an unfamiliar library, tool, or framework hosted on GitHub (or similar forges).
alwaysApply: false
---

# Repository Research Strategy

A systematic approach to understanding a repository you haven't worked with
before. The goal is to find authoritative documentation with minimal wasted
context.

## Phase 1: Fetch the README

The README is the entry point. Always start here.

```
https://raw.githubusercontent.com/{owner}/{repo}/main/README.md
```

> **Critical**: Use `raw.githubusercontent.com`, never `github.com`. The latter
> returns ~50KB+ of HTML navigation, JS bundles, and React partials that
> consume context for zero information.

If `main` 404s, try `master`.

Scan the README for:

- Links to a **documentation site** (e.g., `docs.example.com`, GitHub Pages)
- Pointers to a **`/docs`** or **`/website`** directory
- Inline configuration examples or schema descriptions
- Links to a **wiki** (`github.com/{owner}/{repo}/wiki`)
- Badge links (often reveal CI, coverage, and package registry URLs)

## Phase 2: Discover the File Tree

If the README doesn't answer your question, map the repo structure:

```
https://api.github.com/repos/{owner}/{repo}/git/trees/main?recursive=1
```

This returns every file path in the repo. Grep the response for terms related
to your question (e.g., `config`, `mcp`, `schema`, `docs`, `reference`).

### Documentation Directory Patterns

Repos typically store docs in one of these locations:

| Pattern | Common In |
|---|---|
| `docs/` | Most projects |
| `website/docs/` | Docusaurus, Astro Starlight |
| `site/` | MkDocs, Hugo |
| `doc/` | Ruby, Elixir |
| `pages/` | Jekyll |
| `.github/wiki/` | GitHub wikis (rare in tree) |

### Documentation File Patterns

Look for these filenames in priority order:

1. **`README.md`** — top-level and per-directory
2. **`CONFIGURATION.md`**, **`CONFIG.md`** — dedicated config docs
3. **`*.mdx`**, **`*.md`** in any docs directory
4. **`CHANGELOG.md`** — useful for understanding recent schema changes
5. **`CONTRIBUTING.md`** — often documents project structure
6. **`examples/`** — working configs and usage patterns
7. **`schema.json`**, **`*.schema.ts`** — machine-readable schemas

## Phase 3: Check for a Documentation Site

Many projects host docs separately. Common hosting patterns:

| URL Pattern | Platform |
|---|---|
| `{owner}.github.io/{repo}/` | GitHub Pages |
| `docs.{project}.dev` | Custom domain |
| `{repo}.readthedocs.io` | Read the Docs |
| `wiki.{repo}.io` | Wiki-style |

When fetching doc site pages, target specific paths rather than the root:

```
https://{owner}.github.io/{repo}/configuration/
https://{owner}.github.io/{repo}/reference/
https://{owner}.github.io/{repo}/guides/
https://{owner}.github.io/{repo}/api/
```

## Phase 4: Read Source for Schema Truth

When documentation is absent, incomplete, or truncated, the source code is the
canonical schema reference. The type definitions tell you exactly what fields
are supported.

### By Language

**Rust** — look for `#[derive(Deserialize)]` structs:
```
src/config.rs
crates/{name}-core/src/config.rs
src/config/*.rs
```

**TypeScript/JavaScript** — look for `interface` or `type` exports:
```
src/types.ts
src/config.ts
src/schema.ts
lib/types.d.ts
```

**Go** — look for structs with JSON/TOML/YAML tags:
```
pkg/config/config.go
internal/config/types.go
cmd/*/config.go
```

**Python** — look for dataclasses, Pydantic models, or TypedDicts:
```
src/{name}/config.py
{name}/models.py
{name}/schema.py
```

### Discovery via Grep

If the file tree is large, search for the specific field or section name:

```
https://github.com/{owner}/{repo}/search?q={term}&type=code
```

Note: unauthenticated API code search may return 401. The web UI works but
returns HTML. Prefer scanning the API tree + targeted raw fetches.

## Phase 5: Check Tests and Fixtures

Test files often contain the most complete examples of valid configuration:

```
tests/
test/
fixtures/
testdata/
*_test.rs
*.test.ts
*_test.go
```

Look for fixture files (`.toml`, `.json`, `.yaml`) in test directories — they
exercise edge cases the docs may not cover.

## Anti-Patterns

| Don't | Do Instead |
|---|---|
| Fetch `github.com/{owner}/{repo}` | Fetch `raw.githubusercontent.com/...` |
| Guess file paths repeatedly | Use the API tree first |
| Assume docs are complete | Verify claims against source types |
| Read the entire source tree | Grep the API tree, then fetch targeted files |
| Trust outdated blog posts | Check CHANGELOG.md for breaking changes |
