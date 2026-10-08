---
name: skill-opt
description: Interactively optimize any agent skill or rule file using automated test generation, trajectory reflection, and validation gating across LLM providers. Use when asked to optimize a skill, refine prompt instructions, benchmark agent rules, or run /skill-opt.
persona: Skill Optimizer
---

# /skill-opt — Interactive Skill & Rule Optimizer

**Purpose:** Interactively optimize any agent skill (`SKILL.md`) or rule file
(`*.md`) using automated test generation, trajectory reflection, and validation
gating powered by Google's Gemini models (or Anthropic, OpenAI, and OpenRouter).

--------------------------------------------------------------------------------

## Architectural Principles

1.  **Decoupled Optimization Roles (`/gemini-api` Standard):**
    -   **Target Model (`gemini-flash-latest`):** Executes task rollouts with the candidate skill placed in the top-level `system_instruction` block (fallback chain: `gemini-3.8-flash` $\rightarrow$ `gemini-3.7-flash` $\rightarrow$ `gemini-3.6-flash`).
    -   **Judge Model (`gemini-flash-lite-latest` / `gemini-flash-latest`):** Grades execution trajectories against two-tier rubrics using native JSON mode (`responseMimeType: "application/json"`).
    -   **Optimizer Model (`gemini-pro-latest`):** Analyzes sanitized behavioral feedback and synthesizes surgical Markdown patches (fallback chain: `gemini-3.1-pro-preview` $\rightarrow$ `gemini-3.8-flash`).
2.  **Optimizer Feedback Boundary (Anti-Reward-Hacking):** The judge separates raw scoring evidence (`audit_rationale`, kept only in the report artifact) from sanitized `optimizer_feedback` (plain-language descriptions of the user-visible behavior gap, stripped of literal test regexes or keywords). Reflection consumes only `optimizer_feedback` so the optimizer never games tests by copying literal check strings into `SKILL.md`.
3.  **Strict Validation Gating & Semantic Token Guards:** Candidate edits must pass YAML frontmatter/header checks, stay within a $\le 35\%$ whitespace-normalized token diff budget, respect the $\le 1.20$ token bloat cap, and achieve a multi-seed statistically significant improvement on held-out validation tasks with zero `[INVARIANT]` vetoes.
4.  **Automated Transcript Harvesting (Zero-UUID):** Mines recent session logs across Antigravity, Claude Code, and Cursor for real developer corrections and tool errors without manual lookup.
5.  **`/zoom-out` Plain-Language Communication:** All chat outputs—pre-flight test plans, 20-second progress bars, and final summaries—lead with a plain-English Bottom Line Up Front (BLUF), a compact ASCII mental model flow ($\le 5$ nodes), and a 3-Pillar breakdown (*The Problem*, *The Fix*, *The Result & Trade-Off*). Statistical proofs ($t$-scores, seed variance, diff ratios, raw scenario IDs) live in the background Proof-of-Verification (POV) artifact rather than cluttering chat.

--------------------------------------------------------------------------------

## Protocol

### Step 1: Intent Routing, Target Ingestion & House Rules

1.  **Natural-Language Intent & Sub-Mode Routing:**
    Infer the requested action and any inline house rules (`--preferences`) from the user's prompt:
    -   **`run` (Full Optimization — Default):** Requests to optimize, improve, or refine a skill/rule file execute the full multi-epoch loop (Steps 1–6).
    -   **`dry-run` (Baseline Audit / Preview):** Requests to preview, audit, or *"show what could be improved"* (as well as ambiguous optimization requests) execute Steps 1–3, run only the baseline evaluation pass, and present a `/zoom-out` diagnostic scorecard **without** running mutation epochs or modifying live files.
    -   **`harvest` (Session Friction Inspection):** Requests to inspect mistakes or *"see what failed in recent sessions"* scan session transcripts (Step 2.1) and output a plain-English `/zoom-out` friction digest without launching rollouts.
    -   **Inline House Rules (`--preferences`):** Preserve any explicit constraints stated by the user (e.g., *"keep under 200 lines"*, *"avoid first-person plural we/our"*) and inject them into both the `[INVARIANT]` rubric tier and the optimizer reflection prompt. Do not invent paths, skill names, or configuration values that the user did not provide.
2.  **Identify & Resolve Target Path(s):**
    -   If no target skill, rule file, or directory was specified, ask: *"Which skill or rule file(s) would you like to optimize? Please provide the file path(s), directory, or skill name."*
    -   **Directory Discovery:** If given a directory path (e.g., `.agents/skills/` or `.agents/rules/`), scan for descendant `SKILL.md` and `*.md` rule files, list them in chat, and prompt via `ask_question` (`"(Recommended) Run batch optimization across all N discovered skills/rules"`, `"Let me select specific files"`, `"Cancel"`).
    -   Resolve all confirmed target paths to strict absolute paths and read each file completely (plus any interdependent producer/consumer skills to verify handoff schemas).

--------------------------------------------------------------------------------

### Step 2: Automated Transcript Mining & Test Matrix Synthesis

1.  **Universal Multi-Platform Transcript Discovery:**
    -   Automatically scan existing session log directories (merging and deduplicating across all detected platforms without interrupting the user unless no logs exist and custom input is needed):
        -   **Antigravity**: `<appDataDir>/brain/` or `~/.gemini/antigravity/brain/`
        -   **Claude Code**: `~/.claude/projects/`, `~/.claude/transcripts/`, `~/.claude/sessions/`
        -   **Cursor / VS Code Copilot**: `~/.cursor/`, `~/.config/Code/User/globalStorage/`, `.vscode/`
        -   **Local Workspace**: `./.sessions/`, `./logs/`, `~/.skillopt/logs/`
    -   Normalize extracted friction turns into a unified schema (`timestamp`, `platform`, `target_skill`, `trigger_prompt`, `failing_turn`, `user_correction`, `error_signal`) and group into orthogonal failure categories.
    -   If no log directories exist (or zero turns reference the target skill), automatically fall back to synthesizing test scenarios from the skill's behavioral contract.
2.  **Synthesize Train & Val Datasets (Cardinality & Adversarial Floor):**
    -   **Minimum Sample Size Floors:** Generate at least **6 training tasks** (`|D_train| >= 6`) and **4 held-out validation tasks** (`|D_val| >= 4`) across disjoint technical domains and at least 2 orthogonal failure categories.
    -   **Adversarial Negative Probe Floor:** At least **40% of all scenarios** must be adversarial negative probes testing boundary violations, malformed inputs, or forbidden tool calls.
    -   **Two-Tier Assertion Rubrics:** Partition each scenario's 4–6 discrete `eval_criteria` into:
        -   `[INVARIANT]`: Hard veto power ($S_{\text{task}} = 0.0$ if any invariant fails). Verifies strict retention of negative prohibitions, consult-first gates, and read-only guardrails.
        -   `[QUALITY]`: Scalar partial credit ($0.0$ to $1.0$) for formatting, completeness, and tone:
            $$S_{\text{task}} = \mathbb{I}(\text{all INVARIANTS pass}) \times \left( \frac{1}{N_{\text{qual}}} \sum_{j=1}^{N_{\text{qual}}} Q_j \right)$$

--------------------------------------------------------------------------------

### Step 3: Unified Pre-Flight Gate & `/gemini-api` Runner Generation

1.  **Silent Environment & Key Resolution:**
    -   Auto-detect `GEMINI_API_KEY` from `os.environ` or shell profiles (`~/.bashrc`, `~/.profile`, `~/.zshrc`)—or `ANTHROPIC_API_KEY` / `OPENAI_API_KEY` / `OPENROUTER_API_KEY` if the user requested a non-Gemini provider.
    -   Only prompt for an API key if no valid key is discoverable in the environment.
    -   Default the scratch workspace to `.scratch/skillopt_<slug>_<timestamp>/` (or enter cumulative **Session Resumption Mode** setting `seed_skill.md` = `best_skill.md` if an existing session directory was specified).
2.  **Present Unified `/zoom-out` Pre-Flight Plan & Single Launch Modal:**
    Instead of asking multiple serial setup modals, output a single scannable pre-flight overview in chat before calling `ask_question` once:
    -   **Bottom Line Up Front (Plain English):** 1–2 sentences summarizing what skill is being tested, what recurring friction or blind spots were found, and the active model setup (`gemini-flash-latest` target / `gemini-pro-latest` critic).
    -   **Mental Model Flow:**
        ```text
        [Mined Friction + Contract Rules] ──► [10 Test Scenarios] ──► [Validated Skill Update]
        ```
    -   **Plain-Language Test Matrix Table:** Render a clean Markdown table in chat with columns `Split | Scenario | What the User Asks | Expected Agent Behavior (Plain English) | Source` (avoiding raw regexes or mathematical notation in chat).
    -   **Single Launch Gate (`ask_question`):**
        -   *Question:* "How should we run this optimization plan?"
        -   *Options:*
            -   `"(Recommended) Launch full optimization with this test matrix"`
            -   `"Run baseline dry-run only (score current skill without editing)"`
            -   `"Customize test scenarios, assertions, or model provider"`
3.  **Generate Self-Contained `/gemini-api` Harness (`run_optimizer.py`):**
    Write `skills/seed_skill.md`, `tasks/train.jsonl`, `tasks/val.jsonl`, and `run_optimizer.py` in the scratch directory using Python 3 standard library modules (`urllib.request`, `concurrent.futures`, `json`, `re`, `difflib`):
    -   **`/gemini-api` Payload & Fallback Architecture:**
        -   Endpoint: `https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={API_KEY}`.
        -   **Top-Level `system_instruction`:** Pass the candidate `SKILL.md` text inside `payload["system_instruction"] = {"parts": [{"text": skill_text}]}`—never concatenate skill instructions into `contents`.
        -   **Native JSON Mode on Judge Calls:** Set `payload["generationConfig"]["responseMimeType"] = "application/json"` on all judge calls so the judge deterministically returns `{"passed": bool, "invariant_veto": bool, "score": float, "optimizer_feedback": str, "audit_rationale": str}`.
        -   **Hierarchical Model Fallback & Backoff:**
            -   Target role: `gemini-flash-latest` $\rightarrow$ `["gemini-3.8-flash", "gemini-3.7-flash", "gemini-3.6-flash"]`.
            -   Judge role: `gemini-flash-lite-latest` $\rightarrow$ `["gemini-flash-latest", "gemini-3.8-flash"]`.
            -   Optimizer role: `gemini-pro-latest` $\rightarrow$ `["gemini-3.1-pro-preview", "gemini-3.8-flash"]`.
            -   On HTTP `404` or `503`, immediately break to the next fallback model. On HTTP `429` or timeout (`timeout=90`), sleep `2 ** attempt` seconds. Guard `candidates[0].content.parts` and log `finishReason` if empty.
        -   **Concurrent Batch Rollouts:** Execute task rollouts and judge calls in parallel using `concurrent.futures.ThreadPoolExecutor(max_workers=5)`.
    -   **Algorithmic Safety & Statistical Gating Modules:**
        -   **Pre-Flight Key Probe:** Verify API connectivity before starting rollouts; halt cleanly on `400`/`401`/`403`.
        -   **Deflated Baseline Shield:** Re-measure baseline if initial validation score is `< 0.500` or if transport errors occur; abort if repeated baselines diverge by `> 0.200`.
        -   **Optimizer Feedback Boundary:** Strip raw `eval_criteria` regexes and internal check strings from reflection prompts; pass only the judge's plain-language `optimizer_feedback` descriptions of the behavioral failure.
        -   **Whitespace-Normalized Semantic Token Diff Guard (`clip <= 0.35`):** Compute `1.0 - SequenceMatcher(None, base_tokens, cand_tokens).ratio()` on whitespace-split tokens (`re.split(r"\s+", text.strip())`) so 80-column Markdown wrapping does not trigger false rejections. Reject mutations with token diff ratio `> 0.35` or broken YAML frontmatter/headers.
        -   **Anti-Verbosity Token Bloat Guard:** Reject candidates where $R_{\text{tokens}} = \text{Tokens}(\text{cand}) / \text{Tokens}(\text{seed}) > 1.20$ unless validation score improves by $\ge +0.150$ with zero invariant vetoes.
        -   **Heuristic Step Sizing (`lr_autonomous`):** Use structural additions when baseline validation $< 0.70$, and minimal surgical phrasing edits when baseline $\ge 0.70$.
        -   **Multi-Seed Statistical Gate ($K \ge 3$ seeds):** Promote a candidate if and only if $\text{LB}(S_{\text{cand}}) = \bar{S}_{\text{cand}} - t_{0.10, K-1} \cdot \frac{s_{\text{cand}}}{\sqrt{K}} > \bar{S}_{\text{baseline}}$ and $\forall k \in [1, K], \text{Vetoes}_k = 0$. Record any rejected epoch candidates and their rejection reasons in `skillopt_report.json`.

--------------------------------------------------------------------------------

### Step 4: Background Execution & `/zoom-out` Progress Updates

1.  Launch `run_optimizer.py` in the background using `run_command` with `WaitMsBeforeAsync: 5000` and `NotificationTimeoutSeconds: 20`.
2.  Concurrently arm a 20-second conditional timer via `schedule(DurationSeconds=20, TimerCondition="<task-id>", Prompt="Check optimizer progress and emit a progress bar update")`.
3.  **`/zoom-out` 20-Second Progress Format:**
    On each 20-second wakeup while the task is running, inspect the log (`view_file` or `manage_task status`), re-arm the 20-second `schedule` timer in the same turn, and output a concise, plain-language update using the global **20-block unbracketed progress bar**:

    ```markdown
    `▓▓▓▓▓▓▓▓▓▓▓▓░░░░░░░░ 60%` (Task 2 of 3: Epoch 1 Validation — 10/16 scenarios)

    Baseline passed 7 of 10 scenarios but missed the pre-release test verification and clean working-tree checks. Testing a 5-line update on held-out validation scenarios next.
    ```

    -   **Plain-English Exception-Driven Telemetry:** Collapse passing noise into the progress bar. State in 1–2 plain sentences what was just learned or fixed and what happens next, without dumping internal task IDs (`VAL_06`, `TRAIN_34`), regexes, or timer boilerplate.

--------------------------------------------------------------------------------

### Step 5: `/zoom-out` Final Report & Deployment Gate

1.  **Write Formal Proof-of-Verification (POV) Artifact (`skillopt_report_<slug>.md`):**
    Store all detailed technical evidence in the artifact file: sample sizes (`|D_train|`, `|D_val|`, $K$ seeds), Student's $t$ confidence intervals, `[INVARIANT]` veto audits, token growth ($R_{\text{tokens}}$) and semantic diff ratios, rejected epoch diagnostics, before/after trace comparisons, and the full unified diff.
2.  **Render `/zoom-out` Summary in Chat (<350 Words, Scannable in <15s):**
    Keep the in-chat summary high-level, plain-language, and free of statistical clutter:
    -   **Bottom Line Up Front (Plain English):** 1–2 sentences stating what changed in the skill and the overall validation pass-rate improvement (e.g., *"Updated `git-release` so the agent always runs tests before creating a tag and verifies a clean working tree. Held-out pass rate improved from **33% to 100%** (+67% over baseline) with zero regressions."*).
    -   **Mental Model Flow (Compact ASCII, $\le 5$ nodes, $\le 4$ lines):**
        ```text
        [Failure Mode Observed] ──► [Skill Instruction Updated] ──► [New Agent Behavior]
        ```
    -   **The 3-Pillar Breakdown:**
        -   **The Problem:** What mistake or blind spot the agent exhibited on baseline tasks.
        -   **The Fix:** What specific rule or clarification was added to `SKILL.md` in plain conversational language.
        -   **The Result & Trade-Off:** What improves in day-to-day usage, confirming all existing guardrails held (`0 safety/invariant regressions`) and showing net line change (e.g., `+8 lines, -2 lines`).
    -   **Before vs. After Scorecard Table:** Render a clean Markdown table in chat with plain-English capability rows:
        `Capability | Before | After | Status`
    -   **What You Can Safely Ignore Right Now:** A 1-line link to `skillopt_report_<slug>.md` for the multi-seed confidence math, rejected epoch notes, and raw unified diff.
3.  **Deployment Gate (`ask_question`):**
    -   If running in `dry-run` mode, stop after presenting the baseline `/zoom-out` scorecard and ask if the user wants to launch optimization epochs.
    -   Otherwise, prompt via `ask_question`:
        -   *Question:* "Would you like to deploy the optimized skill to its original path?"
        -   *Options:*
            -   `"(Recommended) Approve and update original file in-place"`
            -   `"Keep optimized file in scratch directory only"`
            -   `"Run another optimization epoch with adjusted criteria"`

--------------------------------------------------------------------------------

### Step 6: In-Place Source Update & Snapshot Backup

1.  When approved for in-place deployment:
    -   Create a timestamped backup snapshot (`SKILL.md.bak_YYYYMMDD_HHMM`) alongside the target file.
    -   Write `best_skill.md` to the target path and verify valid YAML frontmatter and Markdown formatting.
2.  **One-Step Rollback Recovery:** If post-deployment regressions occur, restore via `cp <target_dir>/SKILL.md.bak_YYYYMMDD_HHMM <target_path>` and confirm restoration in chat.
3.  Conclude with a clickable `file://` link to the updated skill file and the backup snapshot path.
