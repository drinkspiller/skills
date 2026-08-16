---
name: skill-opt
description: Interactively optimize any agent skill or rule file using automated test generation, trajectory reflection, and validation gating across LLM providers. Use when asked to optimize a skill, refine prompt instructions, benchmark agent rules, or run /skill-opt.
persona: Skill Optimizer
---

# /skill-opt — Interactive Skill & Rule Optimizer

**Purpose:** Interactively optimize any agent skill (`SKILL.md`) or rule file (`*.md`) using automated test generation, trajectory reflection, and validation gating across LLM providers.

--------------------------------------------------------------------------------

## Architectural Principles

1.  **Decoupled Optimization Roles:**
    -   **Target Model (e.g. `gemini-2.5-flash`, `claude-3-7-sonnet`, `gpt-4o-mini`):** The runtime agent executing task rollouts to expose instructional blind spots and failure modes.
    -   **Optimizer Model (e.g. `gemini-2.5-pro`, `claude-3-5-sonnet`, `o3-mini`):** The meta-critic analyzing execution trajectories, diagnosing root-cause ambiguities, and synthesizing surgical Markdown patches.
2.  **Strict Validation Gating & Syntax Guards:** Candidate edits are only accepted if they pass automated frontmatter/Markdown syntax checks and achieve a strict score improvement on unseen validation tasks.
3.  **Universal Transcript Harvesting (Zero-UUID):** Automatically mines recent session logs for real developer corrections and failure turns across multiple agent platforms without requiring manual lookup.
4.  **Algorithmic Safety Modules:** Employs deterministic edit distance bounding (clip <=35% line change), multi-trace batch aggregation, and heuristic step sizing to prevent catastrophic forgetting.
5.  **Multi-Skill Cross-Alignment:** Ensures interdependent skills (e.g., track planning and implementation) maintain synchronized handoff schemas by actively verifying consumer/producer files.

--------------------------------------------------------------------------------

## Protocol

### Step 1: Target Ingestion & Verification

1.  Identify the target skill, rule path, directory, or multi-skill bundle requested by the user.
2.  If no path was provided, ask: *"Which skill or rule file(s) would you like to optimize? Please provide the file path(s), directory, or skill name."*
3.  **Directory & Descendant Discovery:**
    -   If the user provides a directory path:
        -   Scan the directory recursively for all descendant `SKILL.md` files and `*.md` rule files.
        -   Present the list of all discovered descendant files in chat.
        -   Prompt the user using `ask_question`:
        -   *Question:* "Directory contains N skills/rules. How should we proceed?"
        -   *Options:*
            -   `"(Recommended) Run batch optimization across all N discovered skills/rules"`
            -   `"Let me select specific files from the list"`
            -   `"Cancel"`
4.  **Absolute Path Resolution:** Resolve all confirmed target path(s) to strict absolute paths.
5.  Read each target file completely to ingest its existing frontmatter, behavioral steps, tool calls, and lifecycle constraints.

--------------------------------------------------------------------------------

### Step 2: Automated Eval Synthesis & Targeted Transcript Mining

1.  **Universal Multi-Platform Transcript Discovery & Aggregation:**
    -   Automatically probe common agent transcript and session log locations across tools:
        -   **Antigravity**: `<appDataDir>/brain/` or `~/.gemini/antigravity/brain/`
        -   **Claude Code**: `~/.claude/projects/`, `~/.claude/transcripts/`, `~/.claude/sessions/`
        -   **Cursor / Windsurf / VS Code Copilot**: `~/.cursor/`, `~/.config/Code/User/globalStorage/`, `.vscode/`
        -   **Local Workspace / CLI**: `./.sessions/`, `./logs/`, `~/.skillopt/logs/`
    -   **Handling Multiple Detected Platforms:**
        -   If logs are detected across multiple platforms:
        -   Present the detected platforms and prompt via `ask_question`:
            -   *Question:* "Detected session logs across multiple platforms. How should we harvest friction?"
            -   *Options:*
                -   `"(Recommended) Harvest and merge friction turns across all detected platforms"`
                -   `"Let me select specific platforms from the list"`
                -   `"Skip log harvesting and synthesize from skill contract only"`
        -   When merging, deduplicate identical friction traces and synthesize a unified training set.
    -   **Single Platform or Custom Path:**
        -   If exactly one log directory is detected, automatically scan it for turns referencing the target skill.
    -   **Graceful Fallback When No Log Directory Exists:**
        -   If no log directory is detected, prompt via `ask_question`:
            -   *Question:* "No default session logs detected. How would you like to build test scenarios?"
            -   *Options:*
                -   `"(Recommended) Auto-synthesize edge cases from the skill contract (no logs needed)"`
                -   `"Specify a custom transcript directory or log file"`
                -   `"Paste a recent failure or correction snippet manually"`
        -   If the user provides a custom path or snippet, ingest it; otherwise proceed with pure contract-driven synthesis.
2.  **Deconstruct the Behavioral Contract:** Analyze the target file to identify:
    -   Mandatory prerequisite checks and inputs.
    -   Interactive flow requirements (e.g., `ask_question` formatting, report-first ask-second).
    -   Tool calling protocols and sequential stop barriers.
    -   Output artifact schemas and file modification constraints.
3.  **Multi-Skill Schema Check (Interdependent Bundles):**
    -   If optimizing interdependent skills (e.g., producer and consumer skills), read the related skill files.
    -   Cross-reference output schemas against consumer expectations to prevent handoff regressions.
4.  **Synthesize Train & Val Datasets:** Auto-generate 2–3 training scenarios (combining mined transcript turns with synthetic edge cases) and 1–2 held-out validation scenarios in distinct technical domains:
    -   Each scenario must define an `id`, `prompt`, and 4–6 discrete `eval_criteria` assertions.
5.  **Present Matrix in Chat:** Output the full generated test matrix in your response message body formatted as a clean Markdown table detailing the scenario prompt, target behavior, source (Mined vs. Synthetic), and assertion criteria.
6.  **Interactive Elicitation:** Invoke `ask_question` to confirm the test matrix:
    -   *Question:* "Would you like to add any custom test scenarios or target specific failure cases?"
    -   *Options:*
        -   `"(Recommended) Proceed with the generated test matrix"`
        -   `"I want to add custom test scenarios"`
        -   `"Refine the existing assertions"`
7.  If the user provides custom scenarios, append them to the dataset splits.

--------------------------------------------------------------------------------

### Step 3: Workspace Environment, Provider & Runner Setup

1.  **Provider Selection & Environment Key Check:**
    -   Ask the user which model provider they prefer:
        -   `Google Gemini` (Default: Target `gemini-2.5-flash`, Optimizer `gemini-2.5-pro`, Key: `GEMINI_API_KEY`)
        -   `Anthropic` (Target `claude-3-7-sonnet`, Optimizer `claude-3-5-sonnet`, Key: `ANTHROPIC_API_KEY`)
        -   `OpenAI` (Target `gpt-4o-mini`, Optimizer `gpt-4o` or `o3-mini`, Key: `OPENAI_API_KEY`)
        -   `OpenRouter / Custom API` (Custom target/optimizer model names, Key: `OPENROUTER_API_KEY`)
    -   **Environment Variable Detection & Persistence Flow:**
        -   Check `os.environ` for the provider's key (e.g. `GEMINI_API_KEY`, `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `OPENROUTER_API_KEY`).
        -   **If an environment variable exists:**
        -   Prompt via `ask_question`:
            -   *Question:* "Found active {PROVIDER}_API_KEY in environment. Use this key?"
            -   *Options:*
                -   `"(Recommended) Yes, use the existing environment variable"`
                -   `"No, I want to provide a different key for this session"`
        -   **If NO environment variable exists (or user wants to supply a different key):**
        -   Solicit the API key from the user.
        -   Prompt via `ask_question`:
            -   *Question:* "Persist this API key to your environment for future sessions?"
            -   *Options:*
                -   `"(Recommended) Yes, export to ~/.bashrc for future sessions"`
                -   `"No, keep it local to this session only (.env in scratch)"`
        -   If the user selects export, append `export <PROVIDER>_API_KEY="<key>"` to their `~/.bashrc`.
    -   Store the active key in a local `.env` file within the scratch directory or reference `os.environ["<PROVIDER>_API_KEY"]`. Never embed keys in version-controlled files.
2.  **Suggest Workspace Directory or Detect Existing Session:**
    -   If the user provides an existing session directory, enter **Session Resumption Mode** (see §3.5).
    -   Otherwise, propose a new dedicated scratch path: `.scratch/skillopt_<slug>_<timestamp>/`
3.  **Confirm Workspace Path:** Invoke `ask_question`:
    -   *Question:* "Where should the optimization session run?"
    -   *Options:*
        -   `"(Recommended) Use suggested scratch path: <suggested_path>"`
        -   `"Resume/re-run an existing session directory"`
        -   `"Specify a custom workspace directory"`
4.  **Generate Harness Files & Algorithmic Guard Modules:**
    -   **Self-Contained Runner (Default — Zero External Clones):**
        -   SkillOpt generates a self-contained Python script (`run_optimizer.py`) directly in the scratch directory using Python's standard library (`urllib.request`, `json`, `re`, `difflib`).
        -   `skills/seed_skill.md`: A pristine copy of the original target file.
        -   `tasks/train.jsonl`: Formatted training scenarios and rubrics.
        -   `tasks/val.jsonl`: Formatted held-out validation scenarios.
        -   `run_optimizer.py` implements:
        -   **Pre-Flight Key Validation:** Performs an immediate probe against the selected provider's endpoint upon startup. If the key is missing, empty, or returns an authentication error (400/401/403), halts immediately with: `sys.exit("ERROR: Invalid or missing API key. Set <PROVIDER>_API_KEY before running.")`.
        -   **Frontmatter & Syntax Validation Guard:** Pre-validates candidate mutations before running validation rollouts. Ensures valid YAML frontmatter (`name:`, `description:` present) and non-truncated Markdown headers. Discards malformed mutations automatically.
        -   **Deterministic Edit Distance Bounding (Lightweight `clip`):** Computes line diff ratios using `difflib`. Automatically rejects candidate mutations that delete or modify more than **35% of existing lines** in a single epoch or drop required markdown headers, preventing destructive hallucinations without spending extra API tokens.
        -   **Multi-Trace Batch Aggregation (Lightweight `aggregate`):** When multiple task rollouts fail in a training batch, concatenates all failed trajectory traces and assertion violations into a single unified reflection prompt, synthesizing one cohesive patch that addresses all failure modes simultaneously.
        -   **Heuristic Step Sizing (Lightweight `lr_autonomous`):** Dynamically injects granularity directives into the reflection prompt based on current validation performance:
            -   *Baseline score < 0.70:* Directs the model to perform structural additions, missing procedural steps, and prerequisite guards.
            -   *Baseline score ≥ 0.70:* Directs the model to perform minimal surgical edits (targeted phrasing, single-line constraint additions) while strictly preserving all working sections.
        -   Exponential backoff retry handling on API endpoints.
        -   Rollout -> Multi-Trace Aggregated Reflection -> Syntax/Clip Guard -> Validation Gating loop across 2 epochs.
    -   **Upstream SkillOpt Repo Clone (Optional / WebUI / Sleep):**
        -   If the user explicitly asks to run upstream Microsoft SkillOpt tools (e.g., launching `skillopt_webui` or running `skillopt_sleep`), the agent checks if `https://github.com/microsoft/SkillOpt.git` exists locally in `~/.config/skillopt_repo` or the scratch workspace.
        -   If missing, it runs `git clone https://github.com/microsoft/SkillOpt.git` and installs dependencies (`pip install -e .[webui]`) before launching.
5.  **Session Resumption & Script Updates:**
    -   When re-running or resuming an existing session:
        -   **Cumulative Checkpointing:** Set `seed_skill.md` to the previous `best_skill.md` so new epochs build upon prior improvements rather than resetting to the original draft.
        -   **Dataset & Parameter Edits:** Allow appending new tasks to `train.jsonl` or editing `run_optimizer.py` (e.g., adjusting `num_epochs`, `max_edit_tokens`, or prompt constraints) without regenerating the entire workspace.

--------------------------------------------------------------------------------

### Step 4: Execution & Continuous Progress Updates

1.  Launch `run_optimizer.py` as a background process.
2.  **Mandatory Frequent Progress Streaming:** Output status updates every 30 seconds or upon epoch transitions:
    -   Current target file, active epoch (e.g., Epoch 1/2), and active phase (Rollout, Reflection, or Validation Gate).
    -   Real-time score deltas (e.g., "Epoch 1 training rollout completed with score 0.85; reflecting on 1 failure trace...").
    -   Validation gate decisions (Accepted with score gain vs. Rejected with rollback).
3.  Maintain execution until all epochs conclude and the final `best_skill.md` is saved.

--------------------------------------------------------------------------------

### Step 5: Report Artifact Generation & Deployment Gate

1.  Read the resulting `best_skill.md` and compute the unified diff against `seed_skill.md`.
2.  Create a comprehensive comparison report containing:
    -   **Executive Summary:** Overview of score gains and line count changes.
    -   **Performance Table:** Baseline vs. Final validation scores and percentage improvement.
    -   **Key Behavioral Refinements:** Detailed breakdown of resolved failure modes (e.g., modal batching, step ordering, schema gaps).
    -   **Unified Diff Block:** Complete Markdown diff showing exact deletions and additions.
3.  Present the report link to the user.
4.  Prompt the user for deployment confirmation using `ask_question`:
    -   *Question:* "Would you like to deploy the optimized skill to its original path?"
    -   *Options:*
        -   `"(Recommended) Approve and update original file in-place"`
        -   `"Keep optimized file in scratch directory only"`
        -   `"Run another optimization epoch with adjusted criteria"`
5.  **Handling Re-Runs from the Deployment Gate:**
    -   If the user selects `"Run another optimization epoch with adjusted criteria"`, elicit what parameters or test criteria should be adjusted, update `tasks/train.jsonl` or `run_optimizer.py` in-place, set `seed_skill.md` = `best_skill.md`, and re-launch Step 4.

--------------------------------------------------------------------------------

### Step 6: In-Place Source Update & Snapshot Backup

1.  If the user approves the in-place update:
    -   **Automatic Pre-Deployment Snapshot:** Create a timestamped backup copy (`SKILL.md.bak_YYYYMMDD_HHMM`) in the target directory before modifying the original file.
    -   Write the contents of `best_skill.md` directly to the original absolute file path.
    -   Verify that YAML frontmatter and formatting integrity are strictly preserved.
2.  Announce completion with a direct link to the updated source file.
