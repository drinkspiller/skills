#!/usr/bin/env python3
"""audit_slop.py - scan a web codebase for AI-generated design tells.

Plain Python, standard library only. Detection patterns and severity come from
a Reddit analysis (~3.2M posts / 3,033 on-topic comments across 47 subreddits)
of what people actually flag as making a site look AI-generated.

Usage:
    python3 audit_slop.py <path>                   # scan a dir or file
    python3 audit_slop.py <path> --severity high    # only high-signal tells
    python3 audit_slop.py <path> --json             # machine-readable (for CI)
    python3 audit_slop.py <path> --max 8            # cap examples shown per
    rule

Exit code is the number of HIGH-severity findings (0 = none), so CI can gate on
it.

Adapted from devibe_scan.py (vibecoded-design-tells, MIT license) for the
craft-ui skill gate taxonomy.
"""

import argparse, json, os, re, sys

EXTS = {
    ".html",
    ".htm",
    ".css",
    ".scss",
    ".less",
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    ".vue",
    ".svelte",
    ".astro",
    ".mdx",
}
SKIP_DIRS = {
    "node_modules",
    ".git",
    "dist",
    "build",
    ".next",
    "out",
    "vendor",
    "coverage",
    ".svelte-kit",
    ".astro",
    ".turbo",
    ".cache",
    "__pycache__",
}
W = {"high": 3, "medium": 2, "low": 1}

# Each rule: id, label, severity, fix, and patterns (compiled case-insensitive).
RULES = [
    # ---- HIGH: the top concrete tells ----
    {
        "id": "tasteful-default",
        "label": (
            "The 2026 'tasteful default' (cream bg + serif display + sage"
            " accent)"
        ),
        "sev": "high",
        "fix": (
            "Anchor color and type to the real brand or a specific reference."
            " If cream + serif is a genuine decision, add an unslop-ignore"
            " comment."
        ),
        "pats": [
            r"#(faf8f5|f5f1e8|f3eee3|fdfbf7|f7f3ec|faf6ef|f6f1e7|fbf7f0|f4efe4)\b",
            r"\bbg-(stone|amber|orange)-(50|100)\b",
            r"\b(Instrument\s*Serif|Fraunces|Playfair\s*Display|Cormorant|Spectral|DM\s*Serif)\b",
        ],
    },
    {
        "id": "ai-purple",
        "label": "AI purple / indigo / violet as primary color",
        "sev": "high",
        "fix": "Pick a brand color outside the violet/indigo/purple band.",
        "pats": [
            r"\b(bg|text|from|via|to|border|ring|fill|stroke|decoration|outline)-(indigo|violet|purple|fuchsia)-(400|500|600|700|800)\b",
            r"#(6366f1|4f46e5|818cf8|7c3aed|6d28d9|8b5cf6|a855f7|9333ea|7e22ce|c026d3|d946ef)\b",
        ],
    },
    {
        "id": "gradient-text",
        "label": "Gradient-filled text (heading/hero)",
        "sev": "high",
        "fix": (
            "Solid color on headings and copy. Gradient body text is a top-3 AI"
            " tell."
        ),
        "pats": [
            r"bg-clip-text\s+[^\"'`]*text-transparent",
            r"text-transparent\s+[^\"'`]*bg-clip-text",
            r"-webkit-background-clip\s*:\s*text",
            r"\bbackground-clip\s*:\s*text",
        ],
    },
    {
        "id": "purple-blue-gradient",
        "label": "Purple-to-blue/pink gradient",
        "sev": "high",
        "fix": (
            "Default to solid fills. If a gradient is needed, keep stops"
            " analogous and low-contrast."
        ),
        "pats": [
            r"from-(purple|violet|indigo|fuchsia)-\d+\s+(via-[a-z]+-\d+\s+)?to-(blue|indigo|pink|cyan|sky)-\d+",
            r"linear-gradient\([^)]*#(6366f1|7c3aed|8b5cf6|a855f7)[^)]*\)",
        ],
    },
    {
        "id": "artisanal-craft",
        "label": "Artisanal craft cliche (warm cream + brass + espresso)",
        "sev": "high",
        "fix": (
            "Rotate through alternative palettes: Cold Luxury, Forest"
            " Technical, or Monochromatic Pop."
        ),
        "pats": [
            r"#(f5f1ea|f7f5f1|fbf8f1|efeae0|ece6db|faf7f1|e8dfcb)\b",
            r"#(b08947|b6553a|9a2436|9c6e2a|bc7c3a|7d5621)\b",
            r"#(1a1714|1a1814|1b1814)\b",
        ],
    },
    {
        "id": "neon-glow",
        "label": "Neon glow / radial glow blob",
        "sev": "high",
        "fix": (
            "Remove indiscriminate glow effects. Use neutral bases with one"
            " sharp accent."
        ),
        "pats": [
            r"shadow-(indigo|violet|purple|fuchsia|pink)-(400|500|600)/(20|25|30|40|50)",
            r"radial-gradient\([^)]*#(6366f1|a855f7|8b5cf6|7c3aed)",
        ],
    },
    {
        "id": "viewport-spill",
        "label": "Hero section spilling below viewport",
        "sev": "high",
        "fix": (
            "Hero must resolve within min-h-[100dvh]. Cap top padding at pt-20"
            " to pt-24."
        ),
        "pats": [r"\bh-screen\b", r"\b100vh\b"],
    },
    {
        "id": "generic-cta",
        "label": "Generic action copy (Get Started / Submit / Learn More)",
        "sev": "high",
        "fix": (
            "Write specific, task-oriented microcopy: Deploy Cluster, Generate"
            " Token, Inspect Diff."
        ),
        "pats": [
            r">\s*(Get Started|Submit|Click Here|Learn More|Sign Up Now|Start"
            r" Free Trial|Try It Free)\s*<"
        ],
    },
    # ---- MEDIUM ----
    {
        "id": "three-card-grid",
        "label": "Centered hero + three-feature-card grid",
        "sev": "medium",
        "fix": (
            "Break the grid: asymmetric hero with a real screenshot, vary"
            " section layouts."
        ),
        "pats": [r"grid-cols-1\s+(sm:grid-cols-2\s+)?md:grid-cols-3"],
    },
    {
        "id": "emoji-icons",
        "label": "Emoji used as functional icons",
        "sev": "medium",
        "fix": (
            "Use SVG icon libraries (Lucide, Heroicons, Phosphor). Reserve"
            " emoji for informal contexts."
        ),
        "pats": [
            r"[\U0001F680\U0001F4CA\u26A1\U0001F3AF\U0001F4A1\U0001F525\u2728\U0001F6E1\U0001F310\U0001F4C8\U0001F916\U0001F389\U0001F4DD\U0001F9E0\U0001F6A8]"
        ],
    },
    {
        "id": "rounded-everything",
        "label": "Large rounded corners / pill buttons everywhere",
        "sev": "medium",
        "fix": (
            "Deliberate radius scale by role. Pill only for status tags and"
            " small badges."
        ),
        "pats": [
            r"\brounded-(2xl|3xl|full)\b",
            r"border-radius\s*:\s*(999\d*px|9999px)",
        ],
        "suppress": r"\b[hw]-(\d|10|11|12|14|16)(\.5)?\b",
    },
    {
        "id": "fade-animations",
        "label": "Boilerplate fade-in / hover-grow / scroll animation",
        "sev": "medium",
        "fix": (
            "Motion only when it communicates something; gate behind"
            " prefers-reduced-motion."
        ),
        "pats": [
            r"initial=\{\{\s*opacity:\s*0",
            r"whileInView",
            r"whileHover=\{\{\s*scale",
            r"\banimate-\w+.*animate-\w+",
        ],
    },
    {
        "id": "transition-all",
        "label": "transition: all (performance + slop tell)",
        "sev": "medium",
        "fix": (
            "Explicitly name animated properties. Never use transition-all or"
            " transition: all."
        ),
        "pats": [r"\btransition-all\b", r"transition\s*:\s*all\b"],
    },
    {
        "id": "font-monoculture",
        "label": (
            "Default Inter/Geist/Instrument Serif without project justification"
        ),
        "sev": "medium",
        "fix": (
            "Choose a typeface connected to the project direction, not the"
            " framework default."
        ),
        "pats": [
            r"font-family[^;]*\b(Inter|Geist(?!\s*Mono))\b",
            r"\bfont-sans\b.*\bInter\b",
        ],
    },
    {
        "id": "shadcn-default",
        "label": "Untouched shadcn default Card / theme",
        "sev": "medium",
        "fix": (
            "Theme the tokens: primary, radius, neutrals, spacing. Stock"
            " defaults are the giveaway."
        ),
        "pats": [
            r"rounded-lg\s+border\s+bg-card\s+text-card-foreground\s+shadow-sm",
            r"\"baseColor\"\s*:\s*\"(slate|zinc|gray|neutral|stone)\"",
            r"--radius\s*:\s*0\.5rem",
        ],
    },
    {
        "id": "fake-screenshots",
        "label": "Div-based fake screenshots / mock dashboards",
        "sev": "medium",
        "fix": (
            "Render real components, use authentic product photography, or use"
            " semantic placeholder slots."
        ),
        "pats": [r"rounded-full\s+bg-(gray|slate|zinc)-(200|300|400)\s+[hw]-"],
    },
    {
        "id": "fake-metrics",
        "label": "Unearned engineering precision (99.99% uptime / 10x ROI)",
        "sev": "medium",
        "fix": (
            "Use authentic data, label demo metrics clearly, or state benefits"
            " in words."
        ),
        "pats": [
            r"99\.9+%\s*(uptime|availability|reliability)",
            r"\b\d+x\s*(faster|throughput|ROI|improvement|performance)",
        ],
    },
    {
        "id": "duplicate-cta",
        "label": "Duplicate CTA intent across the same page",
        "sev": "medium",
        "fix": (
            "Choose one clear action verb and standardize across header, body,"
            " and footer."
        ),
        "pats": [
            r">\s*(Get in [Tt]ouch|Contact [Uu]s|Let's [Tt]alk|Reach"
            r" [Oo]ut)\s*<"
        ],
    },
    # ---- LOW ----
    {
        "id": "glassmorphism",
        "label": "Unbounded glassmorphism without fallback",
        "sev": "low",
        "fix": (
            "Add @media (prefers-reduced-transparency: reduce) fallback with"
            " solid fill."
        ),
        "pats": [r"backdrop-filter\s*:\s*blur", r"backdrop-blur"],
    },
    {
        "id": "bento-empty",
        "label": "Bento grid with empty placeholder cells",
        "sev": "low",
        "fix": (
            "Every bento cell must contain real content. No blank filler cards."
        ),
        "pats": [r"grid-cols-[2-4].*grid-rows-[2-4]"],
    },
]


def collect_files(root):
  """Yield (path, content) for scannable files under root."""
  if os.path.isfile(root):
    ext = os.path.splitext(root)[1].lower()
    if ext in EXTS:
      try:
        yield root, open(root, encoding="utf-8", errors="replace").read()
      except OSError:
        pass
    return
  for dirpath, dirnames, filenames in os.walk(root):
    dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
    for fn in filenames:
      ext = os.path.splitext(fn)[1].lower()
      if ext in EXTS:
        fp = os.path.join(dirpath, fn)
        try:
          yield fp, open(fp, encoding="utf-8", errors="replace").read()
        except OSError:
          pass


def scan(root, severity_filter=None):
  """Scan root and return list of finding dicts."""
  compiled = []
  for rule in RULES:
    if severity_filter and rule["sev"] != severity_filter:
      continue
    cpats = [re.compile(p, re.IGNORECASE) for p in rule["pats"]]
    csup = (
        re.compile(rule["suppress"], re.IGNORECASE)
        if rule.get("suppress")
        else None
    )
    compiled.append({**rule, "cpats": cpats, "csup": csup})

  findings = []
  for fpath, content in collect_files(root):
    lines = content.split("\n")
    for rule in compiled:
      for i, line in enumerate(lines, 1):
        if "unslop-ignore" in line:
          continue
        for pat in rule["cpats"]:
          if pat.search(line):
            if rule["csup"] and rule["csup"].search(line):
              continue
            findings.append({
                "rule": rule["id"],
                "label": rule["label"],
                "severity": rule["sev"],
                "fix": rule["fix"],
                "file": fpath,
                "line": i,
                "snippet": line.strip()[:120],
            })
            break
  return findings


def main():
  ap = argparse.ArgumentParser(
      description="Scan for AI-generated design tells."
  )
  ap.add_argument("path", help="File or directory to scan.")
  ap.add_argument(
      "--severity",
      choices=["high", "medium", "low"],
      default=None,
      help="Only show findings of this severity.",
  )
  ap.add_argument("--json", action="store_true", help="Output JSON (for CI).")
  ap.add_argument(
      "--max", type=int, default=5, help="Max examples shown per rule."
  )
  args = ap.parse_args()

  findings = scan(args.path, args.severity)

  if args.json:
    json.dump(findings, sys.stdout, indent=2)
    print()
  else:
    grouped = {}
    for f in findings:
      grouped.setdefault(f["rule"], []).append(f)

    if not grouped:
      print("\033[32m✓ No design tells found.\033[0m")
    else:
      total_high = sum(1 for f in findings if f["severity"] == "high")
      total_med = sum(1 for f in findings if f["severity"] == "medium")
      total_low = sum(1 for f in findings if f["severity"] == "low")
      print(f"\n\033[1mSlop Gate Report\033[0m")
      print(f"  HIGH: {total_high}  MEDIUM: {total_med}  LOW: {total_low}\n")

      sev_order = {"high": 0, "medium": 1, "low": 2}
      for rule_id in sorted(
          grouped, key=lambda r: sev_order.get(grouped[r][0]["severity"], 9)
      ):
        hits = grouped[rule_id]
        sev = hits[0]["severity"].upper()
        label = hits[0]["label"]
        color = {
            "HIGH": "\033[31m",
            "MEDIUM": "\033[33m",
            "LOW": "\033[36m",
        }.get(sev, "")
        print(f"  {color}[{sev}]\033[0m {label} ({len(hits)} hits)")
        print(f"         Fix: {hits[0]['fix']}")
        for h in hits[: args.max]:
          print(f"         {h['file']}:{h['line']}  {h['snippet']}")
        if len(hits) > args.max:
          print(f"         ... and {len(hits) - args.max} more")
        print()

  high_count = sum(1 for f in findings if f["severity"] == "high")
  sys.exit(min(high_count, 125))


if __name__ == "__main__":
  main()
