---
name: ae-inspect-describe
description: Inspect the active Adobe After Effects composition via the After Effects MCP bridge (https://github.com/Dakkshin/after-effects-mcp) and generate an exhaustive technical and motion design specification for translating it into a production web/app UI animation. Use when inspecting After Effects compositions, extracting layer hierarchies, auditing keyframes/expressions/effects, or translating AE animations into WebGL, Three.js, Canvas 2D, or CSS/SVG.
notes: Intended to be used with the After Effects MCP server (https://github.com/Dakkshin/after-effects-mcp).
metadata:
  mcp_server: https://github.com/Dakkshin/after-effects-mcp
---

# After Effects Inspect & Describe

> **Prerequisite**: This skill requires the After Effects MCP server
> ([https://github.com/Dakkshin/after-effects-mcp](https://github.com/Dakkshin/after-effects-mcp)).

## Pre-Flight Check: MCP Server Availability

Before executing the inspection workflow:

1.  **Verify MCP Server Availability**: Check if the After Effects MCP server
    tools (e.g., `run-script`, `get-results`, `setLayerKeyframe`,
    `setLayerExpression`, `apply-effect`, or `mcp_aftereffects_*` tools) are
    available in the active session.
2.  **If NOT Found or Unreachable**:

    -   Stop execution immediately.
    -   Reply to the user with the following message:

        ```text
        The After Effects MCP server could not be found. Please ensure
        After Effects is running with the MCP bridge active, and
        install/configure the MCP server from:
        https://github.com/Dakkshin/after-effects-mcp
        ```

    -   Do not attempt to guess or hallucinate composition layers, keyframes, or
        effect parameters without the live MCP bridge.
3.  **If Found**: Proceed with the inspection workflow below.

--------------------------------------------------------------------------------

## MCP Tool Execution Flow

Query the active After Effects state systematically using the MCP bridge.

### Step 0: Discover Server Capabilities

Call the `get-help` tool first to retrieve the server's current capability
documentation, available predefined scripts, and supported operations. This
orients the agent to the specific server version and configuration before
committing to an extraction sequence.

### Step 1: Discover Compositions

Read the `aftereffects://compositions` resource via `read_resource` to list all
compositions in the current project. This is the simplest path to discover
composition names and IDs.

Alternatively, use the `list-compositions` MCP **prompt** (note: this is a
prompt, not a tool — invoke it via the prompt interface, not `call_mcp_tool`).

### Step 2: Inspect Project & Composition Settings

Execute `run-script` to extract canvas resolution, frame rate, duration, and
background color. The `run-script` tool accepts the following JSON input shape:

```json
{
  "script": "<predefined-script-name>",
  "parameters": { "<key>": "<value>" }
}
```

The `script` parameter accepts predefined script names registered with the MCP
server (e.g., project info or layer info scripts). The exact names depend on the
server's configuration — consult the `get-help` output from Step 0 to identify
available scripts. After calling `run-script`, always call `get-results` to
retrieve the output.

### Step 3: Extract Layer Tree

Execute `run-script` with the appropriate layer info script and pass the target
composition name via the `parameters` field. Follow with `get-results` to
extract the complete layer stack, parent-child hierarchies, blend modes, track
mattes, and key transform properties.

### Step 4: Deep Effect & Expression Introspection

For custom effect pipelines, individual parameter controls, or expression
strings not fully captured in the top-level dump, execute targeted ExtendScript
snippets via `run-script` to read `layer.property("Effects")`, expression text,
and keyframe easing handles.

--------------------------------------------------------------------------------

## Error Handling

If any `run-script` or `get-results` call returns an error:

-   **No project open**: Inform the user that After Effects has no active
    project. Do not proceed with inspection.
-   **Composition not found**: Report the exact name that failed and list
    available compositions from the `aftereffects://compositions` resource so
    the user can select the correct one.
-   **Script execution timeout or unknown script**: Fall back to `get-help` to
    re-check available predefined scripts, or ask the user to confirm the server
    version supports the requested operation.
-   **Never hallucinate results** after a failed MCP call. Always report the
    failure and ask the user how to proceed.

--------------------------------------------------------------------------------

## User Consultation: Motion Accessibility

Before generating the final implementation plan, check with the user regarding
their motion accessibility preference:

-   Ask how they want to handle `prefers-reduced-motion` preferences (e.g.,
    providing an instant opacity fade fallback, zero-amplitude resting state,
    static layout snapshot, or standard animation only).
-   Incorporate their preference directly into the engineering and
    implementation sections of the specification.

--------------------------------------------------------------------------------

## Motion Inspection & Translation Specification

Generate an exhaustive technical and motion design specification for translating
the inspected composition into a production web/app UI animation.

Your analysis must include:

1.  **Composition & Layer Hierarchy**:

    -   Canvas resolution, frame rate, duration, and background color.
    -   Complete layer stack (names, types, parent-child hierarchies, blending
        modes, track mattes).
    -   Where appropriate to the composition's structure, describe the natural
        layer hierarchy without forcing artificial tiering.

2.  **Effects, Expressions & Keyframe Audit**:

    -   Extract every applied effect (e.g., Gaussian Blur, Turbulent Displace,
        Gradient Ramp, Noise) with exact property values.
    -   Transcribe and deconstruct all ExtendScript / AE expressions (e.g.,
        `time * x`, `wiggle()`, `linear()`, `ease()`, ping-pong evolution).
    -   Document keyframe data: spatial interpolation, temporal easing handles
        (influence & speed percentages), and cycle durations.

3.  **Motion Designer's Visual Breakdown**:

    -   Character and visual aesthetic of the animation (cadence, rhythm,
        breathing cycles, spatial weight distribution).
    -   Behavior at screen boundaries (e.g., edge pinning, bounce vs.
        translation/drift).

4.  **Engineering & Algorithmic Translation**:

    -   Map each After Effects technique to its modern web/native counterpart
        (e.g., WebGL fragment shader, Canvas 2D, [Three.js](http://three.js/),
        or CSS/SVG).
    -   Provide the mathematical formulation reproducing the visual physics of
        all motions (harmonic oscillations, 3D simplex noise slices, Gaussian
        diffusion kernels, transition easing curves).
    -   Color architecture: exact hex values, color chord pairs, hold durations,
        and cross-fade math.
    -   Accessibility handling: concrete implementation details adhering to the
        user's selected reduced-motion approach.

5.  **Production Implementation Plan**:

    -   Minimal code skeleton implementing the motion in a standalone static
        page.
    -   Interactive control handles (sliders/dropdowns) with recommended default
        values matching the AE composition.

--------------------------------------------------------------------------------

## Output Artifact & Reporting Format

1.  **Write Specification Artifact**: Persist the complete, exhaustive
    specification to a dedicated Markdown artifact (`ae_motion_spec.md`).
2.  **Chat Summary**: In the chat response, deliver a high-level executive
    summary covering the composition identity, core visual physics, key
    technical translation decisions, and accessibility strategy, accompanied by
    a direct reference to the generated `ae_motion_spec.md` artifact.
