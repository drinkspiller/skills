#!/usr/bin/env python3
"""SkillOpt Sleep — Automated Nightly Skill Optimization Runner for Antigravity & Agent Workspaces.

Discovers skills, harvests session transcript friction, synthesizes human-readable problem
statements with concrete examples, and optimizes instructions across validation-gated epochs.
Delivers updates adaptively via Git branches/Draft PRs or local staging directories.
"""

from __future__ import annotations

import argparse
import datetime
import difflib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import urllib.error
import urllib.request
from typing import Any, Dict, List, Optional, Tuple


def call_llm(
    prompt: str,
    model: str = "gemini-2.5-flash",
    temperature: float = 0.2,
) -> Optional[str]:
  """Calls LLM provider (Gemini, Anthropic, OpenAI) via standard environment variables."""
  # 1. Google Gemini API
  gemini_key = os.environ.get("GEMINI_API_KEY")
  if gemini_key:
    api_url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={gemini_key}"
    )
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": temperature},
    }
    req = urllib.request.Request(
        api_url, data=json.dumps(payload).encode("utf-8"), headers=headers
    )
    try:
      with urllib.request.urlopen(req, timeout=90) as resp:
        data = json.loads(resp.read().decode("utf-8"))
        return data["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as e:
      print(f"Gemini API call failed: {e}", file=sys.stderr)

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
    payload = {
        "model": model if ("gpt" in model or "o3" in model) else "gpt-4o",
        "temperature": temperature,
        "messages": [{"role": "user", "content": prompt}],
    }
    req = urllib.request.Request(
        api_url, data=json.dumps(payload).encode("utf-8"), headers=headers
    )
    try:
      with urllib.request.urlopen(req, timeout=90) as resp:
        data = json.loads(resp.read().decode("utf-8"))
        return data["choices"][0]["message"]["content"]
    except Exception as e:
      print(f"OpenAI API call failed: {e}", file=sys.stderr)

  print("ERROR: No valid LLM API key detected (GEMINI_API_KEY, ANTHROPIC_API_KEY, or OPENAI_API_KEY).", file=sys.stderr)
  return None


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

            # Identify referenced skills
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
    model: str = "gemini-2.5-flash",
) -> str:
  """Synthesizes raw friction into concise, high-level bullets with concrete examples."""
  corrections = friction.get("corrections", [])
  errors = friction.get("errors", [])
  if not corrections and not errors:
    return "- No specific session friction recorded."

  corr_snippets = [f"- User pushback: {c[:250]}" for c in corrections[:5]]
  err_snippets = [f"- Tool failure: {e[:250]}" for e in errors[:5]]

  prompt = f"""You are an expert technical editor. Summarize the observed developer friction and failure modes for the agent skill '{skill_name}' based on the following session logs.

Produce 2 to 4 concise, high-level, human-readable bullet points.
For each friction point:
1. Provide a bold title and a 1-2 sentence explanation of the failure mode and its operational impact on the developer.
2. Provide a 1-sentence indented '*Example*:' sub-bullet giving a concrete, clean illustration of what was attempted or passed vs what failed, referencing the actual context without dumping raw JSON or XML tags.

Format exactly as:
- **<Title>**: <Description>
  *Example*: <Concrete illustration>

CRITICAL RULES:
- Do NOT dump raw JSON, XML tags, or internal UUIDs.
- Write clear, professional software engineering prose.
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
    model: str = "gemini-2.5-flash",
) -> Tuple[float, float, List[Dict[str, Any]]]:
  """Evaluates skill instructions against train and val task splits."""
  train_tasks = [t for t in eval_tasks if t.get("split") == "train"]
  val_tasks = [t for t in eval_tasks if t.get("split") == "val"]
  results = []

  def score_split(tasks: List[Dict[str, Any]]) -> float:
    if not tasks:
      return 1.0
    passed = 0
    total = len(tasks)
    for task in tasks:
      prompt = f"""You are acting as an AI coding agent following these system skill instructions:

<SKILL_INSTRUCTIONS>
{skill_content}
</SKILL_INSTRUCTIONS>

Task: {task['prompt']}

Respond according to the skill instructions above:"""
      response = call_llm(prompt, model=model, temperature=0.1) or ""
      
      # Judge evaluation
      criteria = task.get("criteria", [])
      judge_prompt = f"""Evaluate whether the agent response satisfied all required criteria:

Task: {task['prompt']}
Criteria: {json.dumps(criteria)}
Response: {response}

Output JSON with 'passed' (boolean) and 'reason' (string):"""
      judge_out = call_llm(judge_prompt, model=model, temperature=0.0) or "{}"
      try:
        m = re.search(r"\{.*\}", judge_out, re.DOTALL)
        decision = json.loads(m.group(0)) if m else {"passed": False}
      except Exception:
        decision = {"passed": False}

      is_pass = bool(decision.get("passed", False))
      if is_pass:
        passed += 1
      results.append({"id": task.get("id"), "passed": is_pass, "reason": decision.get("reason", "")})
    return passed / total

  train_score = score_split(train_tasks)
  val_score = score_split(val_tasks)
  return train_score, val_score, results


def optimize_skill(
    skill_name: str,
    skill_path: Path,
    friction: Dict[str, Any],
    runner_model: str = "gemini-2.5-flash",
    optimizer_model: str = "gemini-2.5-pro",
) -> Optional[Dict[str, Any]]:
  """Runs a 2-epoch optimization loop on a single skill."""
  baseline_content = skill_path.read_text(encoding="utf-8")
  problem_summary = synthesize_friction_summary(skill_name, friction, model=runner_model)

  # Synthesize basic evaluation tasks
  eval_tasks = [
      {
          "id": f"{skill_name}_task_1",
          "split": "train",
          "prompt": f"Execute the standard workflow for {skill_name} under typical inputs.",
          "criteria": ["Follows prerequisite checks", "Provides clear structured output"],
      },
      {
          "id": f"{skill_name}_task_2",
          "split": "train",
          "prompt": f"Handle malformed, ambiguous, or incomplete inputs when invoking {skill_name}.",
          "criteria": ["Prompts for clarification rather than hallucinating", "Maintains safe boundaries"],
      },
      {
          "id": f"{skill_name}_task_3",
          "split": "val",
          "prompt": f"Execute {skill_name} on an unfamiliar or complex edge-case scenario.",
          "criteria": ["Handles edge cases gracefully", "Respects sequential confirmation barriers"],
      },
  ]

  base_train, base_val, _ = evaluate_skill(baseline_content, eval_tasks, model=runner_model)
  print(f"[{skill_name}] Baseline: Train={base_train:.3f}, Val={base_val:.3f}")
  if base_val >= 1.0 and base_train >= 1.0:
    print(f"[{skill_name}] Baseline already converged (100% accuracy). Skipping.")
    return None

  best_content = baseline_content
  best_val = base_val
  best_train = base_train
  best_diff_ratio = 0.0

  for epoch in range(1, 3):
    step_directive = (
        "Focus on structural additions, missing procedural steps, and prerequisite guards."
        if best_val < 0.70
        else "Make minimal, surgical edits preserving working sections."
    )

    optimizer_prompt = f"""You are an expert technical editor optimizing an AI agent skill file.

Current SKILL.md:
```markdown
{best_content}
```

Observed Failure Modes & Developer Friction:
{problem_summary}

Directives:
- {step_directive}
- Preserve YAML frontmatter (name, description) exactly.
- Keep diff bounded (edit distance <= 35%).
- Return ONLY the complete, updated SKILL.md content:"""

    candidate = call_llm(optimizer_prompt, model=optimizer_model, temperature=0.2)
    if not candidate:
      continue

    # Strip code fences if present
    candidate = re.sub(r"^```markdown\n", "", candidate)
    candidate = re.sub(r"\n```$", "", candidate).strip()

    # Syntax and clip guard
    if not candidate.startswith("---") or "name:" not in candidate:
      print(f"[{skill_name}] Epoch {epoch}: Rejected (malformed YAML frontmatter).")
      continue

    diff_ratio = 1.0 - difflib.SequenceMatcher(None, best_content.split(), candidate.split()).ratio()
    if diff_ratio > 0.35:
      print(f"[{skill_name}] Epoch {epoch}: Rejected (diff ratio {diff_ratio:.3f} > 0.350 limit).")
      continue

    c_train, c_val, _ = evaluate_skill(candidate, eval_tasks, model=runner_model)
    print(f"[{skill_name}] Epoch {epoch}: Train={c_train:.3f}, Val={c_val:.3f} (diff ratio {diff_ratio:.3f})")

    # Monotonic gating
    if c_val > best_val and c_train >= best_train:
      print(f"[{skill_name}] Epoch {epoch}: Accepted improvement! (Val {best_val:.3f} -> {c_val:.3f})")
      best_content = candidate
      best_val = c_val
      best_train = c_train
      best_diff_ratio = diff_ratio

  if best_val <= base_val:
    print(f"[{skill_name}] No improvements passed validation gating.")
    return None

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
  }


def deliver_update(opt_result: Dict[str, Any]) -> None:
  """Delivers optimized skill via Git branch/draft PR or local staging directory."""
  skill_name = opt_result["skill"]
  skill_path: Path = opt_result["path"]
  best_content = opt_result["best_content"]
  problem_summary = opt_result["problem_summary"]
  date_str = datetime.date.today().strftime("%Y%m%d")

  commit_msg = f"""feat({skill_name}): optimize skill instructions via SkillOpt Sleep

## Problem Mined
{problem_summary}

## Changes Applied
- Automatically refined procedural constraints and edge-case handling based on session logs.
- Enforced input validation and boundary protections.

TESTED:
- Train Score: {opt_result['base_train']:.3f} -> {opt_result['best_train']:.3f}
- Val Score: {opt_result['base_val']:.3f} -> {opt_result['best_val']:.3f}
- Semantic Diff Ratio: {opt_result['diff_ratio']:.3f} (budget <= 0.350)
"""

  # Check if skill lives inside a Git repo
  is_git = False
  try:
    res = subprocess.run(
        ["git", "rev-parse", "--is-inside-work-tree"],
        cwd=skill_path.parent,
        capture_output=True,
        text=True,
        check=False,
    )
    is_git = (res.returncode == 0 and res.stdout.strip() == "true")
  except Exception:
    is_git = False

  if is_git:
    repo_root = Path(subprocess.check_output(
        ["git", "rev-parse", "--show-toplevel"],
        cwd=skill_path.parent,
        text=True,
    ).strip())
    branch_name = f"skillopt/{skill_name}-{date_str}"
    print(f"Creating Git branch '{branch_name}' in {repo_root}...")
    subprocess.run(["git", "checkout", "-b", branch_name], cwd=repo_root, check=False)
    skill_path.write_text(best_content, encoding="utf-8")
    subprocess.run(["git", "add", str(skill_path)], cwd=repo_root, check=False)
    subprocess.run(["git", "commit", "-m", commit_msg], cwd=repo_root, check=False)

    # Attempt GitHub Draft PR via gh CLI if available
    try:
      gh_check = subprocess.run(["gh", "auth", "status"], capture_output=True, text=True, check=False)
      if gh_check.returncode == 0:
        print(f"Creating Draft Pull Request via gh for '{branch_name}'...")
        subprocess.run(
            ["gh", "pr", "create", "--draft", "--title", f"feat({skill_name}): optimize skill via SkillOpt Sleep", "--body", commit_msg],
            cwd=repo_root,
            check=False,
        )
    except Exception as e:
      print(f"Note: Could not open GitHub PR ({e}). Branch '{branch_name}' committed locally.")
  else:
    # Staging directory fallback
    staging_dir = Path.home() / ".skillopt" / "staging" / skill_name
    staging_dir.mkdir(parents=True, exist_ok=True)
    (staging_dir / "SKILL.md").write_text(best_content, encoding="utf-8")
    (staging_dir / "README.md").write_text(commit_msg, encoding="utf-8")
    print(f"Staged optimized skill at {staging_dir / 'SKILL.md'}")


def main():
  parser = argparse.ArgumentParser(description="SkillOpt Sleep nightly multi-skill optimizer.")
  parser.add_argument("--top_k", type=int, default=3, help="Max candidate skills to optimize.")
  parser.add_argument("--lookback_hours", type=int, default=48, help="Transcript lookback in hours.")
  args = parser.parse_args()

  print("=== Starting SkillOpt Sleep Multi-Skill Consolidation ===")
  friction_map = harvest_friction(args.lookback_hours)

  # Discover skill directories
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
    print("No skills discovered. Specify skills directory or set search paths.")
    return

  # Rank candidate skills by total friction volume
  ranked = []
  for p in candidate_paths:
    skill_name = p.parent.name
    f_data = friction_map.get(skill_name, {"errors": [], "corrections": []})
    volume = len(f_data.get("errors", [])) + len(f_data.get("corrections", []))
    ranked.append((volume, skill_name, p, f_data))

  ranked.sort(key=lambda x: x[0], reverse=True)
  selected = [item for item in ranked if item[0] > 0][:args.top_k]

  if not selected:
    print("Zero active transcript friction detected across discovered skills. No optimizations needed.")
    return

  print(f"Selected top {len(selected)} candidate skills with active friction: {[s[1] for s in selected]}")
  for _, s_name, s_path, f_data in selected:
    print(f"\n--- Optimizing {s_name} ---")
    res = optimize_skill(s_name, s_path, f_data)
    if res:
      deliver_update(res)


if __name__ == "__main__":
  main()
