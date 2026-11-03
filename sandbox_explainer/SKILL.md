---
name: sandbox-explainer
description: >-
  Builds interactive, active-learning HTML sandbox wizards to explain complex
  codebases, PRs, documents, or technical concepts using physical metaphors,
  visceral broken states, and hands-on fixing tasks. Use when asked to create an
  interactive explainer, sandbox explainer, active-learning tutorial, or to
  explain a concept/PR using a step-by-step interactive sandbox. Don't use for
  passive 1920x1080 D3/AI-illustrated slide decks (use visual-explainer) or pure
  UI layout mocking without pedagogical steps (use sandbox-preview).
metadata:
  icon: 🧪
---

# Sandbox Explainer

Build an ephemeral, active-learning HTML sandbox wizard to explain complex technical concepts, codebases, or pull requests. Unlike passive slide decks or static documentation, a sandbox explainer forces the learner to interact with the concept—breaking it, fixing it, and playing with it—using physical metaphors and Craft UI design engineering.

## 1. Input Gathering & Clarification

Gather context from the provided codebase, PR, commit, prompt, or document.
- **Pull Requests & Commits:** Run `git show`, `git diff`, or `gh pr diff <pr>` to read the actual code changes.
- **Codebases/Docs:** Use code search (e.g., `ripgrep`, `ast-grep`) and file reading tools to map the architecture.
- **One-Shot Inference:** Infer the best physical metaphor and pedagogical spine automatically and build the explainer in one shot. Pause to ask the user (via `AskUserQuestion` in Claude Code, `ask_question` in Antigravity, structured prompt in OpenCode/Codex, or a numbered Markdown pause in CLI harnesses) ONLY if the input is completely missing (e.g., "make an explainer" with no topic) or highly ambiguous.

## 2. Pedagogical Spine (The Wizard Steps)

Design a 4-to-8 step sidebar wizard. Adapt the steps to the topic using a flexible menu of step types (e.g., Architecture Mapping, Data Flow Tracing, State Machine Toggling, Parameter Tuning). 

**Suggested Default Spine (5-Part Active Learning):**
Unless the topic strongly demands otherwise, default to this exact 5-part progression:
1. **Zoom Out (10,000-ft View):** Tee up what is being explained directly (no meta-scaffolding like "This explains..."). Anchor it in a relatable physical metaphor (e.g., a pop-up book, a mailroom sorting belt, a plumbing valve). Show the final working state in the right-hand workspace.
2. **Vocabulary (The Tangible Pieces):** Map the abstract code/files to physical nouns. Provide clickable rows that highlight or isolate the corresponding visual elements in the workspace.
3. **The Problem (Visceral Broken State):** Show exactly what breaks if the code/feature is missing or misconfigured. Force the workspace into a visually broken state (e.g., overlapping ghost textures, dropped packets piling up, infinite loading spinners).
4. **Hands-On Fix (Active Learning):** Give the learner a tool (a paintbrush, a slider, a toggle switch, a draggable node) and a specific task box to fix the broken state themselves. Provide immediate visual feedback in the workspace. Break complex fixes into multiple sequential steps if needed.
5. **Sandbox (Free Play):** Unlock all controls, toggles, and parameters. Provide an "Auto-Fix" or "Reset" button so the learner can safely experiment with edge cases and review the mental model.

## 3. Copywriting & Tone Guardrails (Physical Intuition)

Technical jargon induces cognitive overload. Enforce a strict physical-intuition writing style across all UI copy.

**Mandatory Prompt Block & Self-Critique:**
Before writing the final HTML, draft the step copy and run a self-critique pass against these rules (rewrite any violations):
- **Physical Metaphors over Jargon:** Use "digital scissors" or "sky hole-punch" instead of "alpha discard threshold". Use "traffic cop" instead of "mutex lock".
- **Action-Oriented Headlines:** Use `Given → New` continuity or active verbs (e.g., "The Ghost Eraser", "Routing the Traffic").
- **Physical Verbs:** Data does not "process" or "execute"; it "flows", "stamps", "blocks", "punches", or "snaps".
- **Safe-to-Ignore Boxes:** Include a `.ignore-box` at the bottom of complex steps explicitly listing advanced concepts, edge cases, or files the learner does not need to worry about right now to protect their cognitive load.
- **Zero AI Tropes:** Ban words like "delve", "tapestry", "crucial", "seamless". Write with `/humanizer` and `/ux-copy` principles. Drop `we`/`our` and `you`/`your` in favor of verb-led imperative or explicit-subject active voice. Omit requester names.

## 4. Tech Stack & Craft UI Laws

Read [references/template.md](references/template.md) for the mandatory HTML/CSS/JS boilerplate shell, design tokens, and keyboard navigation logic.

- **Workspace Tech:** Pick the best tool for the right-hand interactive workspace based on the topic. Vanilla HTML/CSS 3D transforms and Canvas 2D are preferred for speed and zero-dependency reliability. Lightweight CDNs (D3.js, p5.js, Three.js) are permitted if the visualization demands complex graphing or 3D rendering.
- **No Auto-Play:** Transitions between steps happen ONLY when the learner clicks Next/Back or presses the Left/Right arrow keys.
- **Craft UI & Accessibility:** Enforce `>= 7:1` WCAG AAA contrast on all text (even inside broken-state illustrations). Enforce concentric border radii (`R_inner = max(0, R_outer - padding)`). Ban `transition: all` and multi-line stadium lozenges. Never put a colored `border-left` accent stripe on a rounded card (use a leading icon or full neutral border instead). Show versions as a tiny muted bottom-right footer, never a header badge.

## 5. Build, Verify & Host

1. **Generate:** Emit a Design Read in chat (`Reading this as: ...`). Create a Python generator script or write the self-contained `index.html` directly to a local scratch or output directory (e.g., `./sandbox_out/<topic>_explainer/index.html` or an agent artifact directory). Never add temporary routes to application repositories.
2. **Serve:** Launch a background Python HTTP server on an ephemeral port (30000-49000):
   ```bash
   python3 -m http.server <PORT> --directory ./sandbox_out/<topic>_explainer &
   ```
3. **Headless Visual Verification (Mandatory):** Before sharing the link, run a headless browser (e.g., Playwright, Puppeteer, or headless Chromium via `$CHROMIUM_PATH` with `--disable-dev-shm-usage`) to take screenshots of at least Step 1 and the Hands-On Fix step:
   ```bash
   npx playwright screenshot --viewport-size="1280,800" http://localhost:<PORT>/index.html step1.png
   ```
   View the screenshots using multimodal vision capabilities. Verify Craft UI laws, check for overlapping text, CSS 3D label occlusion (e.g., `rotateX`/`rotateY` inverting visual stacks), broken wrapping, and contrast issues. Fix any visual bugs in the code before proceeding.
4. **Deliver & Prompt for Hosting:** End the chat reply with the plain `http://localhost:<PORT>/index.html` URL (and a `.url.json` bookmark if running in Antigravity). Omit `<agent-embed>` widgets unless requested. Ask the user if they want to publish the explainer permanently to a static host (e.g., `gh-pages`, Cloudflare Pages, Netlify, Vercel).
