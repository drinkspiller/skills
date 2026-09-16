---
name: gemini-api
description: Practical guide and zero-dependency recipes for calling Google's Gemini API directly (HTTP/REST, Python urllib, curl). Use when generating text, structured JSON, running batch LLM calls, configuring models, or setting up GEMINI_API_KEY without needing skill-opt.
---

# Calling the Gemini API

This skill provides direct, zero-dependency recipes and reference patterns for
calling Google's Gemini API across Python and the command line.

--------------------------------------------------------------------------------

## 1. Authentication & Environment

All requests authenticate via an API key passed in the query parameter
`?key=${GEMINI_API_KEY}` or header `x-goog-api-key`.

### Environment Setup

```bash
# Check if key is present
echo "$GEMINI_API_KEY"

# If not set, export in ~/.bashrc or current shell
export GEMINI_API_KEY="AIzaSy..."
```

In Python:

```python
import os
import sys

api_key = os.environ.get("GEMINI_API_KEY", "")
if not api_key:
    sys.exit("ERROR: GEMINI_API_KEY environment variable is not set.")
```

--------------------------------------------------------------------------------

## 2. Models & Capabilities

Endpoint template:

```
https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={API_KEY}
```

### Preferred First Choices (Auto-Updating Pointers)

Always prefer these canonical aliases for general text and reasoning tasks. They automatically resolve to the latest stable production model snapshots:

| Model Alias | Purpose | Latency / Throughput |
| :--- | :--- | :--- |
| `gemini-pro-latest` | Complex reasoning, multi-step refactoring, architecture critique, system analysis | Highest quality, medium latency |
| `gemini-flash-latest` | General text generation, code transformation, balanced synthesis | Fast, balanced quality |
| `gemini-flash-lite-latest` | High-volume batch evaluation, rapid classification, scoring, triage | Lowest latency, highest QPS |

### Alternative & Fixed Version Models (Alts)

Use these when pinning to specific generation architectures or preview features:

| Model | Classification | Description |
| :--- | :--- | :--- |
| `gemini-3.8-flash` | Latest Flash generation | Advanced speed-optimized model with expanded context reasoning |
| `gemini-3.7-flash` | Stable Flash generation | High-performance reasoning with low latency |
| `gemini-3.6-flash` | Workhorse Flash | Proven balanced reasoning and code generation |
| `gemini-3.1-pro-preview` | Deep Pro preview | Frontier reasoning for architectural design and complex debugging |

### Specialized Image Models (Image Generation & Edits Only)

These models use the standard `:generateContent` endpoint but return image payloads inside `candidates[0].content.parts[].inlineData` (`image/png` or `image/jpeg`) rather than text:

| Model | Task | Endpoint / Notes |
| :--- | :--- | :--- |
| `gemini-3.1-flash-image` | Rapid image generation & edits | Fast image synthesis via `:generateContent` |
| `gemini-3-pro-image` | High-fidelity image generation | Multi-turn visual refinement and detailed asset synthesis |

### Dynamic Model Fallback Strategy

When automating API calls, design model selection hierarchically:
1. Try `gemini-flash-latest` (or `gemini-flash-lite-latest` for batch jobs).
2. Fallback to `gemini-pro-latest`.
3. Fallback to pinned snapshots (`gemini-3.8-flash`, `gemini-3.7-flash`, `gemini-3.1-pro-preview`).

--------------------------------------------------------------------------------

## 3. Zero-Dependency Python Helper (Standard Library)

Use this production-grade, self-contained implementation without needing
external packages (`requests`, `google-generativeai`):

```python
import json
import os
import time
import urllib.error
import urllib.request
from typing import Any, Dict, List, Optional

def call_gemini(
    prompt: str,
    system_instruction: Optional[str] = None,
    model: str = "gemini-flash-latest",
    fallback_models: Optional[List[str]] = None,
    temperature: float = 0.2,
    max_output_tokens: Optional[int] = None,
    json_mode: bool = False,
    api_key: Optional[str] = None,
    max_retries: int = 3
) -> str:
    """Invokes Gemini API with model fallback and exponential backoff."""
    key = api_key or os.environ.get("GEMINI_API_KEY", "")
    if not key:
        raise ValueError("GEMINI_API_KEY not configured in environment.")

    candidate_models = [model] + (fallback_models or [
        "gemini-pro-latest",
        "gemini-flash-lite-latest",
        "gemini-3.8-flash",
        "gemini-3.7-flash",
        "gemini-3.1-pro-preview"
    ])

    # Payload Construction
    payload: Dict[str, Any] = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": temperature,
        }
    }

    if system_instruction:
        payload["system_instruction"] = {
            "parts": [{"text": system_instruction}]
        }

    if max_output_tokens:
        payload["generationConfig"]["maxOutputTokens"] = max_output_tokens

    if json_mode:
        payload["generationConfig"]["responseMimeType"] = "application/json"

    data_bytes = json.dumps(payload).encode("utf-8")

    for current_model in candidate_models:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{current_model}:generateContent?key={key}"

        for attempt in range(1, max_retries + 1):
            req = urllib.request.Request(
                url,
                data=data_bytes,
                headers={"Content-Type": "application/json"}
            )
            try:
                with urllib.request.urlopen(req, timeout=60) as resp:
                    res = json.loads(resp.read().decode("utf-8"))
                    cands = res.get("candidates", [])
                    if cands and "content" in cands[0]:
                        parts = cands[0]["content"].get("parts", [])
                        if parts and "text" in parts[0]:
                            return parts[0]["text"].strip()
                    return ""
            except urllib.error.HTTPError as e:
                # 404 or 503: model unavailable -> try fallback model
                if e.code in (404, 503):
                    break
                # 429: rate limited -> backoff
                time.sleep(2 ** attempt)
            except Exception:
                time.sleep(2 ** attempt)

    return ""
```

--------------------------------------------------------------------------------

## 4. Common Recipes

### A. Structured JSON Extraction

```python
schema_prompt = "Extract entities and status from: 'Host db-prod-01 CPU peaked at 98% and failed health check.'"
response_json = call_gemini(
    prompt=schema_prompt,
    system_instruction="You are an automated triage parser. Output valid JSON matching: {'host': str, 'metric': str, 'status': str}.",
    json_mode=True
)
data = json.loads(response_json)
print(data["host"], data["status"])
```

### B. High-Throughput Concurrent Batch Calls

Run multiple prompts in parallel using `concurrent.futures`:

```python
import concurrent.futures

prompts = [
    ("Prompt 1", "Explain Paxos"),
    ("Prompt 2", "Explain Raft"),
    ("Prompt 3", "Explain 2PC")
]

def worker(item):
    label, text = item
    res = call_gemini(prompt=text, model="gemini-2.5-flash-lite")
    return label, res

with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:
    results = list(pool.map(worker, prompts))

for label, response in results:
    print(f"=== {label} ===\n{response[:100]}...\n")
```

--------------------------------------------------------------------------------

## 5. Quick CLI / Curl Verification

Test an API key and connectivity from the shell in one line:

```bash
curl -s -X POST \
  "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-lite:generateContent?key=${GEMINI_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"contents":[{"parts":[{"text":"Reply with: API CONNECTION SUCCESSFUL"}]}]}' \
  | grep -o '"text": *"[^"]*"'
```

--------------------------------------------------------------------------------

## 6. Critical Rules & Gotchas

1.  **System Instructions Placement**: Never put system prompts in `contents`.
    Always place them in the dedicated top-level `system_instruction: {"parts":
    [{"text": "..."}]}` block.
2.  **Key Security**: Never commit raw API keys to Git, Fig, Piper, or review
    CLs. Always read from `os.environ["GEMINI_API_KEY"]`.
3.  **Candidate Parsing**: Always guard access: `res.get("candidates",
    [])[0].get("content", {}).get("parts", [])[0].get("text", "")`. If a
    response is blocked by safety filters, `candidates[0].content.parts` may be
    empty. Check `finishReason` if text is blank.
4.  **Timeouts**: Wrap `urlopen` in explicit timeouts (`timeout=60` or `90`) to
    prevent hanging processes on network partitions.
