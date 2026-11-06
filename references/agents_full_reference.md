# Full Verbose Reference for `agents.md`

This file preserves the full multi-paragraph prose and extended examples for the
compacted rules in `../AGENTS.md`. Consult on demand when detailed examples or
edge-case walkthroughs are needed.

-   **Subagent Progress & Main-Chat Relay (Extended Details)**:

    -   *Built-in 2-Stage Subagents (`DeepCoder` & `DeepInvestigator` — Parent
        90s Conditional Heartbeat)*: Because built-in `DeepCoder` and
        `DeepInvestigator` run nested 2-stage worker pipelines whose compiled
        system prompts strictly prohibit interim `send_message` updates, the
        parent agent MUST concurrently call `schedule(DurationSeconds=90,
        TimerCondition="<subagent_id>", Prompt="Check subagent progress and emit
        a progress bar update")` (or `TimerCondition="any"` when multiple
        parallel subagents are running) in the same turn as `invoke_subagent`.
        On each 90-second timer wakeup while a subagent remains active, the
        parent calls `manage_subagents(Action="list")` and inspects recent steps
        in the active worker/grandchild `transcript.jsonl`, outputs `\n\n` +
        `` `▓▓▓▓▓▓▓▓▓▓░░░░░░░░░░ XX%` (Task X of Y)`` + `\n\n` + a 1–2 sentence
        status summary in main chat, and concurrently re-arms
        `schedule(DurationSeconds=90, TimerCondition="<subagent_id>", ...)`.
    -   *1-Stage Custom / `self` Subagents (Child `send_message` Relay)*: When
        running as a 1-stage subagent (`self` or `define_subagent`), on every
        progress-note turn (Turn 1, then every ~3–4 turns or ~10 tool calls,
        before slow operations, and when pivoting all the way until completion),
        call
        `send_message(Recipient="<parent_id>", Message="[Progress]\n\n`▓▓▓▓▓▓▓▓▓▓░░░░░░░░░░
        XX%` (Task X of Y)\n\n<note>")` in the same turn alongside your next
        tool call(s). When awakened by an interim `[Progress]` message, the
        parent echoes the progress bar block in main chat and ends the turn (0
        tool calls).

-   **Figma Auth & PAT Fallback (`figma-context` vs. MCP OAuth)**:

    1.  `figma-developer-mcp-server` uses a separate OAuth token from
        `~/.figma_token`. On a `403 Token expired` error from Figma MCP, check
        `test -f ~/.figma_token || test -n "$FIGMA_API_KEY"` (existence only,
        never printing token bytes) and run the CLI node fetcher without
        `--screenshot` before tripping the External Tool Auth Circuit Breaker.
    2.  PATs scoped to `file_content:read` succeed on `/v1/files/<key>/nodes`
        (default node fetch without `--screenshot`) but return `403 Forbidden`
        or time out on `/v1/images` (`--screenshot`). Fetch node YAML without
        `--screenshot` (`--depth 2` on parent flows, full depth on child
        frames); never diagnose a `/v1/images` `403` as an expired PAT when
        `/v1/files/<key>/nodes` succeeds.
    3.  When a user message contains multiple labeled credentials (e.g., host-
        or machine-specific labels), never use first-match `re.search`
        (`matches[0]`); pair each token with its surrounding label via
        `re.finditer` and select the credential matching the active host.

-   **Blender `bpy` Mesh, Texture & Toon-Outline Guardrails**:

    -   **New `bmesh` Faces**: Always call `f.normal_update()` immediately after
        `bm.faces.new(...)` before reading `f.normal`; otherwise
        zero-initialized normals hide inverted winding and turn backface-culled
        `Solidify` outlines solid black.
    -   **In-Memory Image Persistence**: After mutating `img.pixels[:]`, call
        `img.update()` and `img.pack()` — never `img.reload()`, which discards
        the packed pixel buffer in Blender 5.x.
    -   **EEVEE Dithered Outline Masking**: Gate `POINT` attributes like
        `outline_keep` with a `Math (GREATER_THAN 0.95)` node before `Mix
        Shader` so interpolated `(0, 1)` triangle boundaries do not render as
        dithered black stipple.
    -   **Garment UV & Boundary Topology**:
        -   Use a 1-to-1 full-height UV island (`~1000 px/m`) instead of
            modulo-wrapped tiles whenever a garment has non-repeating vertical
            features (center plackets, button rows, collar drop shadows, or
            bottom hem splits).
        -   Sandwich coarse base-mesh material transitions (e.g., diagonal
            skin-to-shirt triangles along a V-neck) underneath a clean overlay
            quad strip (`~14 mm` wide) so sawtooth triangle edges cannot show
            from any camera angle.
        -   For open-neck point/spread collars, partition the collar strip along
            its arc `r`: use the lower segment (`r = 0..10`) as a flush V-neck
            placket band from the V-apex up to the collar gorge (`outline_keep =
            0.0` on its outer flush edge), and flare the collar leaf (`r =
            10..34`) downward and outward from the gorge to the collar point
            with planar tangent-frame UV projection so woven check/plaid
            patterns stay square and un-sheared.
