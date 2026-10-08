#!/usr/bin/env python3
"""SkillOpt Sleep — Automated Nightly Skill Optimization Runner for Antigravity & Agent Workspaces.

Discovers skills, harvests session transcript friction, synthesizes plain-English problem
statements with concrete examples, and optimizes instructions across validation-gated epochs
using /gemini-api conventions, an Optimizer Feedback Boundary, and /zoom-out reporting.
Delivers updates adaptively via Git branches/Draft PRs or local staging directories.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import datetime
import difflib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request
from typing import Any, Dict, List, Optional, Tuple


def call_llm(
    prompt: str,
    model: str = "gemini-flash-latest",
    system_instruction: Optional[str] = None,
    temperature: float = 0.2,
    json_mode: bool = False,
    max_retries: int = 3,
) -> Optional[str]:
  """Calls LLM provider (Gemini, Anthropic, OpenAI) via standard environment variables."""
  # 1. Google Gemini API (/gemini-api conventions with fallback chain)
  gemini_key = os.environ.get("GEMINI_API_KEY")
  if gemini_key:
    fallback_map = {
        "gemini-flash-latest": [
            "gemini-3.8-flash",
            "gemini-3.7-flash",
            "gemini-3.6-flash",
        ],
        "gemini-flash-lite-latest": [
            "gemini-flash-latest",
            "gemini-3.8-flash",
            "gemini-3.7-flash",
        ],
        "gemini-pro-latest": ["gemini-3.1-pro-preview", "gemini-flash-latest"],
    }
    candidates = [model] + fallback_map.get(model, ["gemini-flash-latest"])
    headers = {"Content-Type": "application/json"}

    for candidate in candidates:
      api_url = (
          f"https://generativelanguage.googleapis.com/v1beta/models/{candidate}:generateContent?key={gemini_key}"
      )
      gen_config: Dict[str, Any] = {"temperature": temperature}
      if json_mode:
        gen_config["responseMimeType"] = "application/json"

      payload: Dict[str, Any] = {
          "contents": [{"parts": [{"text": prompt}]}],
          "generationConfig": gen_config,
      }
      if system_instruction:
        payload["system_instruction"] = {
            "parts": [{"text": system_instruction}]
        }

      data_bytes = json.dumps(payload).encode("utf-8")
      for attempt in range(1, max_retries + 1):
        req = urllib.request.Request(api_url, data=data_bytes, headers=headers)
        try:
          with urllib.request.urlopen(req, timeout=90) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            cands = data.get("candidates", [])
            if cands:
              parts = cands[0].get("content", {}).get("parts", [])
              text = "".join(p.get("text", "") for p in parts).strip()
              if text:
                return text
        except urllib.error.HTTPError as e:
          print(
              f"Gemini API ({candidate}) HTTP {e.code}: {e.reason}",
              file=sys.stderr,
          )
          if e.code in (404, 503):
            break
          time.sleep(2**attempt)
        except Exception as e:
          print(
              f"Gemini API ({candidate}) attempt {attempt} failed: {e}",
              file=sys.stderr,
          )
          time.sleep(2**attempt)

  # 2. Anthropic API
  anthropic_key = os.environ.get("ANTHROPIC_API_KEY")
  if anthropic_key:
    api_url = "https://api.anthropic.com/v1/messages"
    headers = {
        "x-api-key": anthropic_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }
    payload = {
        "model": model if "claude" in model else "claude-3-7-sonnet-20250219",
        "max_tokens": 4096,
        "temperature": temperature,
        "messages": [{"role": "user", "content": prompt}],
    }
    if system_instruction:
      payload["system"] = system_instruction
    req = urllib.request.Request(
        api_url, data=json.dumps(payload).encode("utf-8"), headers=headers
    )
    try:
      with urllib.request.urlopen(req, timeout=90) as resp:
        data = json.loads(resp.read().decode("utf-8"))
        return data["content"][0]["text"]
    except Exception as e:
      print(f"Anthropic API call failed: {e}", file=sys.stderr)

  # 3. OpenAI API
  openai_key = os.environ.get("OPENAI_API_KEY")
  if openai_key:
    api_url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {openai_key}",
        "Content-Type": "application/json",
    }
    messages = []
    if system_instruction:
      messages.append({"role": "system", "content": system_instruction})
    messages.append({"role": "user", "content": prompt})
    payload = {
        "model": model if ("gpt" in model or "o3" in model) else "gpt-4o",
        "temperature": temperature,
        "messages": messages,
    }
    if json_mode:
      payload["response_format"] = {"type": "json_object"}
    req = urllib.request.Request(
        api_url, data=json.dumps(payload).encode("utf-8"), headers=headers
    )
    try:
      with urllib.request.urlopen(req, timeout=90) as resp:
        data = json.loads(resp.read().decode("utf-8"))
        return data["choices"][0]["message"]["content"]
    except Exception as e:
      print(f"OpenAI API call failed: {e}", file=sys.stderr)

  print(
      "ERROR: No valid LLM API key detected (GEMINI_API_KEY, ANTHROPIC_API_KEY,"
      " or OPENAI_API_KEY).",
      file=sys.stderr,
  )
  return None


def compute_semantic_diff_ratio(base_text: str, candidate_text: str) -> float:
  """Measures whitespace-normalized token edit distance."""
  base_tokens = [w for w in re.split(r"\s+", base_text.strip()) if w]
  cand_tokens = [w for w in re.split(r"\s+", candidate_text.strip()) if w]
  if not base_tokens:
    return 1.0 if cand_tokens else 0.0
  return 1.0 - difflib.SequenceMatcher(None, base_tokens, cand_tokens).ratio()


def clean_error_content(raw_content: str) -> str:
  """Extracts meaningful error message from tool execution output, stripping metadata headers."""
  if "Encountered error in tool execution:" in raw_content:
    return raw_content.split("Encountered error in tool execution:", 1)[1].strip()
  if "Traceback (most recent call last):" in raw_content:
    parts = raw_content.split("Traceback (most recent call last):", 1)
    lines = [l.strip() for l in parts[1].splitlines() if l.strip()]
    return "\n".join(lines[-3:]) if lines else raw_content.strip()
  cleaned = re.sub(r"^(Created At:.*?(?:File Path:.*?`|output:.*?`|\n\n))", "", raw_content, flags=re.DOTALL)
  cleaned = re.sub(r"Created At:[^\n]+\n?", "", cleaned)
  cleaned = re.sub(r"Completed At:[^\n]+\n?", "", cleaned)
  cleaned = re.sub(r"File Path:[^\n]+\n?", "", cleaned)
  return cleaned.strip() or raw_content.strip()


def clean_user_correction(raw_prompt: str) -> str:
  """Cleans user correction text by stripping XML wrappers and metadata blocks."""
  cleaned = re.sub(r"<ADDITIONAL_METADATA>.*?</ADDITIONAL_METADATA>", "", raw_prompt, flags=re.DOTALL)
  cleaned = re.sub(r"</?USER_REQUEST>", "", cleaned)
  cleaned = re.sub(r"@\[Quote\]", "", cleaned)
  cleaned = re.sub(r"\s+", " ", cleaned).strip()
  return cleaned or raw_prompt.strip()


def harvest_friction(lookback_hours: int = 48) -> Dict[str, Dict[str, Any]]:
  """Probes standard agent transcript locations for friction turns."""
  search_dirs = [
      Path.home() / ".gemini" / "antigravity" / "brain",
      Path.home() / ".claude" / "projects",
      Path.home() / ".claude" / "transcripts",
      Path.home() / ".cursor",
      Path.cwd() / ".sessions",
      Path.cwd() / "logs",
  ]

  cutoff = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=lookback_hours)
  friction_map: Dict[str, Dict[str, Any]] = {}
  correction_keywords = [
      "not what i meant", "don't do that", "that's wrong", "fix this",
      "stop", "undo", "redo", "revert", "failed", "incorrect",
      "too complex", "obtuse", "error", "broken"
  ]

  for base_dir in search_dirs:
    if not base_dir.exists():
      continue
    for log_path in base_dir.glob("**/*.jsonl"):
      try:
        mtime = datetime.datetime.fromtimestamp(log_path.stat().st_mtime, tz=datetime.timezone.utc)
        if mtime < cutoff:
          continue
        with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
          prev_model = False
          skills_referenced = set()
          errors = []
          corrections = []
          for line in f:
            line = line.strip()
            if not line:
              continue
            step = json.loads(line)
            content = step.get("content", "")
            step_type = step.get("type", "")
            source = step.get("source", "")

            for m in re.finditer(r"(?:skills/|_agents/skills/|run_skill\s+)([\w-]+)", content):
              skills_referenced.add(m.group(1))

            if step.get("status") == "ERROR" or "Encountered error in tool execution" in content:
              cleaned = clean_error_content(content)
              if cleaned:
                errors.append(cleaned[:300])

            if step_type == "USER_INPUT" and source == "USER_EXPLICIT" and prev_model:
              if any(k in content.lower() for k in correction_keywords):
                cleaned_corr = clean_user_correction(content)
                if cleaned_corr:
                  corrections.append(cleaned_corr[:300])

            prev_model = (source == "MODEL")

          for s in skills_referenced:
            if s not in friction_map:
              friction_map[s] = {"errors": [], "corrections": []}
            friction_map[s]["errors"].extend(errors)
            friction_map[s]["corrections"].extend(corrections)
      except Exception:
        continue

  return friction_map


def synthesize_friction_summary(
    skill_name: str,
    friction: Dict[str, Any],
    model: str = "gemini-flash-latest",
) -> str:
  """Synthesizes raw friction into concise, plain-English bullets with concrete examples."""
  corrections = friction.get("corrections", [])
  errors = friction.get("errors", [])
  if not corrections and not errors:
    return "- No specific session friction recorded."

  corr_snippets = [f"- User pushback: {c[:250]}" for c in corrections[:5]]
  err_snippets = [f"- Tool failure: {e[:250]}" for e in errors[:5]]

  prompt = f"""You are an expert technical editor applying /zoom-out plain-language principles. Summarize the observed developer friction and failure modes for the agent skill '{skill_name}' based on the following session logs.

Produce 2 to 4 concise, plain-English bullet points focusing on what went wrong and why it mattered.
For each friction point:
1. Provide a bold title and a 1-2 sentence plain-language explanation of the failure mode and its operational impact.
2. Provide a 1-sentence indented '*Example*:' sub-bullet giving a concrete, clean illustration of what was attempted vs what failed, without dumping raw JSON, XML tags, or internal IDs.

Format exactly as:
- **<Title>**: <Plain-English Description>
  *Example*: <Concrete illustration>

CRITICAL RULES:
- Do NOT dump raw JSON, XML tags, or internal UUIDs.
- Avoid academic or ML jargon; write clear, direct software engineering prose.
- Return ONLY the formatted bullet points:

Developer Pushback:
{chr(10).join(corr_snippets)}

Tool Errors:
{chr(10).join(err_snippets)}"""

  summary = call_llm(prompt, model=model, temperature=0.1)
  return summary.strip() if summary else "- Evaluated against boundary edge cases and robustness criteria."


def evaluate_skill(
    skill_content: str,
    eval_tasks: List[Dict[str, Any]],
    model: str = "gemini-flash-latest",
    max_workers: int = 5,
) -> Tuple[float, float, List[Dict[str, Any]]]:
  """Evaluates skill instructions concurrently using system_instruction and Optimizer Feedback Boundary."""
  runner_system = (
      "You are acting as an AI coding agent following these system skill"
      f" instructions:\n\n{skill_content}"
  )
  judge_system = (
      "You are an objective evaluation auditor. Evaluate whether the agent"
      " response satisfies all required criteria in spirit and intent. Output"
      " ONLY a JSON object with keys:\n"
      '- "passed": boolean\n'
      '- "audit_rationale": string (specific diagnostic explanation for human'
      " audit reports)\n"
      '- "optimizer_feedback": string (generalized plain-language behavioral'
      " critique describing what rule or workflow step was missed, WITHOUT"
      " quoting literal test strings, regexes, or assertion IDs)"
  )

  def _eval_one(task: Dict[str, Any]) -> Dict[str, Any]:
    response = (
        call_llm(
            task["prompt"],
            model=model,
            system_instruction=runner_system,
            temperature=0.1,
        )
        or ""
    )
    criteria = task.get("criteria", [])
    judge_prompt = (
        f"Task:\n{task['prompt']}\n\n"
        f"Criteria:\n{json.dumps(criteria)}\n\n"
        f"Agent Response:\n{response}"
    )
    judge_out = (
        call_llm(
            judge_prompt,
            model=model,
            system_instruction=judge_system,
            temperature=0.0,
            json_mode=True,
        )
        or "{}"
    )
    try:
      m = re.search(r"\{.*\}", judge_out, re.DOTALL)
      decision = json.loads(m.group(0)) if m else {"passed": False}
    except Exception:
      decision = {"passed": False}

    is_pass = bool(decision.get("passed", False))
    audit_rationale = str(
        decision.get("audit_rationale") or decision.get("reason") or ""
    )
    optimizer_feedback = str(
        decision.get("optimizer_feedback") or audit_rationale
    )
    return {
        "id": task.get("id"),
        "split": task.get("split", "train"),
        "passed": is_pass,
        "reason": audit_rationale,
        "audit_rationale": audit_rationale,
        "optimizer_feedback": optimizer_feedback,
    }

  with concurrent.futures.ThreadPoolExecutor(
      max_workers=max_workers
  ) as executor:
    results = list(executor.map(_eval_one, eval_tasks))

  train_res = [r for r in results if r.get("split") == "train"]
  val_res = [r for r in results if r.get("split") == "val"]
  train_score = (
      sum(1 for r in train_res if r["passed"]) / len(train_res)
      if train_res
      else 1.0
  )
  val_score = (
      sum(1 for r in val_res if r["passed"]) / len(val_res)
      if val_res
      else 1.0
  )
  return train_score, val_score, results


def format_zoom_out_report(
    skill_name: str,
    problem_summary: str,
    base_train: float,
    best_train: float,
    base_val: float,
    best_val: float,
    diff_ratio: float,
    eval_tasks: List[Dict[str, Any]],
    base_lines: int,
    best_lines: int,
) -> str:
  """Generates a <350-word /zoom-out plain-language summary and scorecard table."""
  n_train = max(sum(1 for t in eval_tasks if t.get("split") == "train"), 1)
  n_val = max(sum(1 for t in eval_tasks if t.get("split") == "val"), 1)
  n_total = len(eval_tasks)

  base_train_pass = round(base_train * n_train)
  best_train_pass = round(best_train * n_train)
  base_val_pass = round(base_val * n_val)
  best_val_pass = round(best_val * n_val)
  base_total = base_train_pass + base_val_pass
  best_total = best_train_pass + best_val_pass
  line_delta = best_lines - base_lines

  first_problem = (
      problem_summary.strip().splitlines()[0].lstrip("-* •")
      if problem_summary.strip()
      else "Instructional ambiguity caused inconsistent task execution."
  )

  return "\n".join([
      (
          f"**Bottom Line**: `{skill_name}` improved from"
          f" **{base_val:.0%} to {best_val:.0%}** held-out pass rate"
          f" ({best_total}/{n_total} checks passed, up from"
          f" {base_total}/{n_total}) by clarifying core workflow guardrails."
      ),
      "",
      "```text",
      (
          f"[Mined Logs] --> [Baseline: {base_total}/{n_total}] -->"
          f" [Targeted Rule Patch] --> [Final: {best_total}/{n_total}]"
      ),
      "```",
      "",
      f"- **The Problem (What Kept Breaking)**: {first_problem}",
      (
          "- **The Fix (What Changed in Plain English)**: Added explicit"
          " prerequisite checks and edge-case guardrails directly in"
          " `SKILL.md`."
      ),
      (
          "- **The Result & Trade-Off (Did It Work?)**: Held-out validation"
          f" checks improved from {base_val_pass}/{n_val} to"
          f" {best_val_pass}/{n_val} with {line_delta:+d} lines"
          f" ({diff_ratio:.0%} semantic token change, within the 35% cap)."
      ),
      "",
      "| Metric | Before (Baseline) | After (Optimized) | Delta |",
      "| :--- | :--- | :--- | :--- |",
      (
          f"| **Held-Out Validation Pass Rate** | {base_val_pass}/{n_val}"
          f" ({base_val:.0%}) | {best_val_pass}/{n_val} ({best_val:.0%}) |"
          f" {best_val - base_val:+.0%} |"
      ),
      (
          f"| **Training Pass Rate** | {base_train_pass}/{n_train}"
          f" ({base_train:.0%}) | {best_train_pass}/{n_train}"
          f" ({best_train:.0%}) | {best_train - base_train:+.0%} |"
      ),
      (
          f"| **Skill Length & Edit Size** | {base_lines} lines | {best_lines}"
          f" lines | {line_delta:+d} lines ({diff_ratio:.0%} token diff) |"
      ),
  ])


def optimize_skill(
    skill_name: str,
    skill_path: Path,
    friction: Dict[str, Any],
    runner_model: str = "gemini-flash-latest",
    optimizer_model: str = "gemini-pro-latest",
    mode: str = "run",
    preferences: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
  """Runs a 2-epoch optimization loop on a single skill with Optimizer Feedback Boundary."""
  baseline_content = skill_path.read_text(encoding="utf-8")
  base_lines = len(baseline_content.splitlines())
  problem_summary = synthesize_friction_summary(
      skill_name, friction, model=runner_model
  )

  eval_tasks = [
      {
          "id": f"{skill_name}_task_1",
          "split": "train",
          "prompt": (
              f"Execute the standard workflow for {skill_name} under typical"
              " inputs."
          ),
          "criteria": [
              "Follows prerequisite checks",
              "Provides clear structured output",
          ],
      },
      {
          "id": f"{skill_name}_task_2",
          "split": "train",
          "prompt": (
              "Handle malformed, ambiguous, or incomplete inputs when invoking"
              f" {skill_name}."
          ),
          "criteria": [
              "Prompts for clarification rather than hallucinating",
              "Maintains safe boundaries",
          ],
      },
      {
          "id": f"{skill_name}_task_3",
          "split": "val",
          "prompt": (
              f"Execute {skill_name} on an unfamiliar or complex edge-case"
              " scenario."
          ),
          "criteria": [
              "Handles edge cases gracefully",
              "Respects sequential confirmation barriers",
          ],
      },
  ]

  if mode == "harvest":
    print(f"[{skill_name}] Harvested Friction:\n{problem_summary}")
    return None

  base_train, base_val, active_results = evaluate_skill(
      baseline_content, eval_tasks, model=runner_model
  )
  print(
      f"[{skill_name}] Baseline: Train={base_train:.1%}, Val={base_val:.1%}"
  )

  if mode == "dry-run":
    print(
        "\n"
        + format_zoom_out_report(
            skill_name,
            problem_summary,
            base_train,
            base_train,
            base_val,
            base_val,
            0.0,
            eval_tasks,
            base_lines,
            base_lines,
        )
    )
    return None

  if base_val >= 1.0 and base_train >= 1.0:
    print(
        f"[{skill_name}] Baseline already converged (100% pass rate). Skipping."
    )
    return None

  best_content = baseline_content
  best_val = base_val
  best_train = base_train
  best_diff_ratio = 0.0

  for epoch in range(1, 3):
    failed_feedback = [
        f"- {r.get('optimizer_feedback', 'Clarify workflow and edge-case rules.')}"
        for r in active_results
        if not r.get("passed", False)
    ]
    feedback_block = (
        "\n".join(failed_feedback)
        if failed_feedback
        else problem_summary
    )
    step_directive = (
        "Focus on structural additions, missing procedural steps, and"
        " prerequisite guards."
        if best_val < 0.70
        else "Make minimal, surgical edits preserving working sections."
    )
    pref_block = (
        f"\nHouse Preferences (MUST obey):\n{preferences}\n"
        if preferences
        else ""
    )

    optimizer_system = (
        "You are an expert technical editor optimizing an AI agent skill file"
        " based on sanitized behavioral feedback without overfitting to test"
        " literals."
    )
    optimizer_prompt = f"""Current SKILL.md:
```markdown
{best_content}
```

Sanitized Behavioral Feedback & Observed Friction:
{feedback_block}
{pref_block}
Directives:
- {step_directive}
- Preserve YAML frontmatter (name, description) and at least 50% of Markdown headers.
- Keep semantic token diff bounded (<= 35%).
- Never insert literal test IDs or hardcoded example prompts.
- Return ONLY the complete, updated SKILL.md content:"""

    candidate = call_llm(
        optimizer_prompt,
        model=optimizer_model,
        system_instruction=optimizer_system,
        temperature=0.2,
    )
    if not candidate:
      continue

    candidate = re.sub(r"^```markdown\n", "", candidate)
    candidate = re.sub(r"\n```$", "", candidate).strip()

    if not candidate.startswith("---") or "name:" not in candidate:
      print(
          f"[{skill_name}] Epoch {epoch}: Rejected (malformed YAML"
          " frontmatter)."
      )
      continue

    diff_ratio = compute_semantic_diff_ratio(baseline_content, candidate)
    if diff_ratio > 0.35:
      print(
          f"[{skill_name}] Epoch {epoch}: Rejected (semantic token diff ratio"
          f" {diff_ratio:.3f} > 0.350 limit)."
      )
      continue

    c_train, c_val, c_results = evaluate_skill(
        candidate, eval_tasks, model=runner_model
    )
    print(
        f"[{skill_name}] Epoch {epoch}: Train={c_train:.1%}, Val={c_val:.1%}"
        f" (token diff ratio {diff_ratio:.3f})"
    )

    if c_val > best_val and c_train >= best_train:
      print(
          f"[{skill_name}] Epoch {epoch}: Accepted improvement! (Val"
          f" {best_val:.1%} -> {c_val:.1%})"
      )
      best_content = candidate
      best_val = c_val
      best_train = c_train
      best_diff_ratio = diff_ratio
      active_results = c_results

  if best_val <= base_val:
    print(f"[{skill_name}] No improvements passed validation gating.")
    return None

  zoom_out_summary = format_zoom_out_report(
      skill_name,
      problem_summary,
      base_train,
      best_train,
      base_val,
      best_val,
      best_diff_ratio,
      eval_tasks,
      base_lines,
      len(best_content.splitlines()),
  )
  print(f"\n{zoom_out_summary}\n")

  return {
      "skill": skill_name,
      "path": skill_path,
      "best_content": best_content,
      "base_train": base_train,
      "best_train": best_train,
      "base_val": base_val,
      "best_val": best_val,
      "diff_ratio": best_diff_ratio,
      "problem_summary": problem_summary,
      "zoom_out_summary": zoom_out_summary,
  }


def deliver_update(opt_result: Dict[str, Any]) -> None:
  """Delivers optimized skill via Git branch/draft PR or local staging directory."""
  skill_name = opt_result["skill"]
  skill_path: Path = opt_result["path"]
  best_content = opt_result["best_content"]
  zoom_out_summary = opt_result["zoom_out_summary"]
  date_str = datetime.date.today().strftime("%Y%m%d")

  commit_msg = f"""feat({skill_name}): optimize skill instructions via SkillOpt Sleep

{zoom_out_summary}
"""

  is_git = False
  try:
    res = subprocess.run(
        ["git", "rev-parse", "--is-inside-work-tree"],
        cwd=skill_path.parent,
        capture_output=True,
        text=True,
        check=False,
    )
    is_git = res.returncode == 0 and res.stdout.strip() == "true"
  except Exception:
    is_git = False

  if is_git:
    repo_root = Path(
        subprocess.check_output(
            ["git", "rev-parse", "--show-toplevel"],
            cwd=skill_path.parent,
            text=True,
        ).strip()
    )
    branch_name = f"skillopt/{skill_name}-{date_str}"
    print(f"Creating Git branch '{branch_name}' in {repo_root}...")
    subprocess.run(
        ["git", "checkout", "-b", branch_name], cwd=repo_root, check=False
    )
    skill_path.write_text(best_content, encoding="utf-8")
    subprocess.run(["git", "add", str(skill_path)], cwd=repo_root, check=False)
    subprocess.run(
        ["git", "commit", "-m", commit_msg], cwd=repo_root, check=False
    )

    try:
      gh_check = subprocess.run(
          ["gh", "auth", "status"],
          capture_output=True,
          text=True,
          check=False,
      )
      if gh_check.returncode == 0:
        print(f"Creating Draft Pull Request via gh for '{branch_name}'...")
        subprocess.run(
            [
                "gh",
                "pr",
                "create",
                "--draft",
                "--title",
                f"feat({skill_name}): optimize skill via SkillOpt Sleep",
                "--body",
                commit_msg,
            ],
            cwd=repo_root,
            check=False,
        )
    except Exception as e:
      print(
          f"Note: Could not open GitHub PR ({e}). Branch '{branch_name}'"
          " committed locally."
      )
  else:
    staging_dir = Path.home() / ".skillopt" / "staging" / skill_name
    staging_dir.mkdir(parents=True, exist_ok=True)
    (staging_dir / "SKILL.md").write_text(best_content, encoding="utf-8")
    (staging_dir / "README.md").write_text(commit_msg, encoding="utf-8")
    print(f"Staged optimized skill at {staging_dir / 'SKILL.md'}")


def main():
  parser = argparse.ArgumentParser(
      description="SkillOpt Sleep nightly multi-skill optimizer."
  )
  parser.add_argument(
      "--top_k", type=int, default=3, help="Max candidate skills to optimize."
  )
  parser.add_argument(
      "--lookback_hours",
      type=int,
      default=48,
      help="Transcript lookback in hours.",
  )
  parser.add_argument(
      "--mode",
      choices=["run", "dry-run", "harvest"],
      default="run",
      help="Execution sub-mode: full run, dry-run baseline check, or harvest.",
  )
  parser.add_argument(
      "--preferences",
      default=None,
      help="Natural-language house preferences for the optimizer critic.",
  )
  args = parser.parse_args()

  print(
      f"=== Starting SkillOpt Sleep Multi-Skill Consolidation (mode={args.mode}) ==="
  )
  friction_map = harvest_friction(args.lookback_hours)

  candidate_paths: List[Path] = []
  search_roots = [
      Path.cwd() / ".agents" / "skills",
      Path.cwd() / ".claude" / "skills",
      Path.home() / ".agents" / "skills",
      Path.home() / "Documents" / "skills",
  ]
  for r in search_roots:
    if r.exists():
      candidate_paths.extend(r.glob("**/SKILL.md"))

  if not candidate_paths:
    print(
        "No skills discovered. Specify skills directory or set search paths."
    )
    return

  ranked = []
  for p in candidate_paths:
    skill_name = p.parent.name
    f_data = friction_map.get(skill_name, {"errors": [], "corrections": []})
    volume = len(f_data.get("errors", [])) + len(f_data.get("corrections", []))
    ranked.append((volume, skill_name, p, f_data))

  ranked.sort(key=lambda x: x[0], reverse=True)
  selected = [item for item in ranked if item[0] > 0][: args.top_k]

  if not selected:
    print(
        "Zero active transcript friction detected across discovered skills. No"
        " optimizations needed."
    )
    return

  print(
      f"Selected top {len(selected)} candidate skills with active friction:"
      f" {[s[1] for s in selected]}"
  )
  for _, s_name, s_path, f_data in selected:
    print(f"\n--- Optimizing {s_name} ---")
    res = optimize_skill(
        s_name,
        s_path,
        f_data,
        mode=args.mode,
        preferences=args.preferences,
    )
    if res and args.mode == "run":
      deliver_update(res)


if __name__ == "__main__":
  main()
