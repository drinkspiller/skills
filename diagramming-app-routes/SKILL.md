---
name: diagramming-app-routes
description: >-
  Builds or updates a static HTML sitemap and routing flowchart (hand-authored
  inline SVG, route-by-user-state table, and request-perimeter pipeline) that
  documents a web app's routes, auth/allowlist/waitlist/terms gates, and
  server-side request checks, grounded in the actual code of a set of commits
  or pull requests. Keeps a dated backup of the previous version. Use when
  asked to "update the routing flow", "add the new routes to the sitemap",
  "diagram the routes/guards in these PRs", "show the waitlist/allowlist
  flow", or to refresh a routing/architecture flowchart after route or gate
  changes. Don't use for cloud-infrastructure diagrams with vendor icons or
  Mermaid-only output.
---

# Diagramming App Routes

Produces a one-file, zero-JS HTML page that answers "what happens when a user
hits route X in state Y", grounded in code. Visual and editorial decisions live
in [design_system.md](references/design_system.md); the page skeleton with
layout-grid coordinates is [template.html](assets/template.html). Read both
before drawing.

## 1. Collect the changes

-   Identify the change set: a PR list, a commit range, or a branch. For
    stacked PRs or branches, read the **top of the stack** for the final state
    and use each PR's description only to attribute features.
-   Pull only the diffs that define routing:

    ```bash
    git diff <base>...<head> -- '<client>/routes.*' '<client>/*guard*' '<server>/<entry handler>'
    # or, per PR:
    gh pr diff <num> --repo <owner>/<repo> -- <paths>
    ```

-   Read new gate modules in full at `<head>` to get: what decides "allowed",
    which environments enforce it, dev overrides (query params, env vars), the
    controlling feature flag, and the exact deny behavior (404 vs redirect vs
    error code).
-   For the request perimeter, open the service/handler at a representative
    endpoint and record the **order** of checks (e.g. allowlist → terms →
    content safety → backend → output check) and their status codes. Find
    which endpoints skip the allowlist check.
-   Don't trust PR descriptions for behavior; confirm in code.

## 2. Draw

1.  **Back up first**: `cp index.html index.v<N>-<YYYY-MM-DD>.html` next to the
    live page (date = the old page's modification date). Link it from the new
    footer.
2.  Start from the existing page if there is one (keep its geometry and
    palette); otherwise copy `assets/template.html`.
3.  Apply [design_system.md](references/design_system.md): happy path down
    `x=680`, public left, deny right, new nodes teal-dashed with a `NEW` pill,
    arrow color = outcome, ≤2 lines per diamond.
4.  Rebuild the route table with one column per user state the gates now
    distinguish; mark new rows `is-new` + `badge-new`.
5.  Add the request-perimeter SVG when the changes add server-side checks.
6.  Add the pending-changes callout if any change is unmerged, and the
    source-changes grid (PR/commit links), stating which changes don't affect
    routing.

## 3. Verify the render

```bash
scripts/render_check.sh <page.html> /tmp/routing.png
```

Open the PNG and fix every defect from design_system.md §8 (diamond text
spill, label overlaps, text wider than its box, lines past the SVG edge).
Re-render once after fixes.

## 4. Publish and report

-   Copy the file to wherever the page is hosted (static host, `gh-pages`
    branch, docs folder). No build step.
-   Reply with what changed per section, and call out anything plausible but
    **unverified** that was deliberately left off the diagram.
