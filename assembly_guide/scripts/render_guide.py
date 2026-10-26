#!/usr/bin/env python3
"""Lints and compiles step-by-step assembly, maintenance, and teardown guides."""

from __future__ import annotations

import argparse
import base64
import html
import json
import math
import mimetypes
import os
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile
from typing import Any

VALID_ARCHETYPES = frozenset({"assembly", "roundtrip", "teardown"})
VALID_DIALECTS = frozenset({"manual", "workbench"})
VALID_TOOL_LINEUP_KINDS = frozenset({
    "torx_key",
    "hex_key",
    "wrench",
    "universal_wrench",
    "screwdriver",
    "soldering_iron",
    "pliers",
    "mat",
    "spudger",
    "tweezers",
    "pcb",
    "cable",
    "brass_brush",
    "cardboard_box",
    "zip_tie",
    "fan",
    "nozzle",
})
VALID_DIFFICULTIES = (
    "Very Easy",
    "Easy",
    "Moderate",
    "Difficult",
    "Very Difficult",
)
COLOR_PALETTE: dict[str, dict[str, str]] = {
    "black": {"hex": "#18181b", "halo": "#fff", "label": "BLACK"},
    "red": {"hex": "#d92d20", "halo": "#fff", "label": "RED"},
    "orange": {"hex": "#f97316", "halo": "#fff", "label": "ORANGE"},
    "yellow": {"hex": "#c8d400", "halo": "#18181b", "label": "YELLOW"},
    "green": {"hex": "#16a34a", "halo": "#fff", "label": "GREEN"},
    "cyan": {"hex": "#0284c7", "halo": "#fff", "label": "CYAN"},
    "blue": {"hex": "#2563eb", "halo": "#fff", "label": "BLUE"},
    "magenta": {"hex": "#db2777", "halo": "#fff", "label": "MAGENTA"},
}
SPATIAL_COLORS = frozenset(COLOR_PALETTE.keys() - {"black"})
BANNED_ACTION_PHRASES = (
    "locate the screw",
    "remember to be careful",
    "can now be removed",
    "is now removed",
    "should be removed",
)
WORD_NUMBERS = {
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
}
# Contrast-first assignment order: the first three hues are maximally distinct
# so small steps never pair near neighbors like red/orange or blue/cyan.
COLOR_SEQUENCE = (
    "red",
    "blue",
    "green",
    "orange",
    "magenta",
    "cyan",
    "yellow",
)
CONFUSABLE_PAIRS = (
    frozenset({"red", "orange"}),
    frozenset({"orange", "yellow"}),
    frozenset({"blue", "cyan"}),
    frozenset({"red", "magenta"}),
)
# Pairs above are tolerated only when a step genuinely needs this many hues.
CONFUSABLE_MIN_COLORS = 4
MAX_MARKER_COLORS_PER_IMAGE = 3
META_COPY_PATTERNS = (
    r"\bi\s*fix\s*it\b",
    r"print[- ]ready",
    r"\bprusa\s*(?:&|and|/|\+)",
    r"\bprusa[- ](?:style|manual|guide|handbook|knowledge base|format)",
    r"build handbook",
)
SNAKE_CASE_RE = re.compile(
    r"(?<![\w/.\-])[a-z][a-z0-9]*(?:_[a-z0-9]+)+(?![\w/.\-])"
)
CAD_COORD_RE = re.compile(r"\b[XYZ]\s*=\s*-?\d")


def _apply_display_names(text: str, names: dict[str, str]) -> str:
  """Replaces CAD identifiers (bare or in backticks) with builder names."""
  for key in sorted(names, key=len, reverse=True):
    label = names[key]
    text = text.replace(f"`{key}`", label)
    text = re.sub(rf"(?<![\w/.\-]){re.escape(key)}(?![\w/.\-])", label, text)
  text = re.sub(r"\b([Tt]he) the\b", r"\1", text)
  text = re.sub(
      r"\b(one|two|three|four|five|six|seven|eight|\d+\s*T(?:\s*\([^)]+\))?)\s+the\s+",
      r"\1 ",
      text,
      flags=re.IGNORECASE,
  )
  return text


class LintFinding:
  """Represents a deterministic structural or cognitive lint finding."""

  def __init__(self, code: str, severity: str, message: str) -> None:
    self.code = code
    self.severity = severity  # "ERROR" or "WARN"
    self.message = message

  def format(self) -> str:
    return f"[{self.severity}] {self.code}: {self.message}"


def _infer_fastener_count(bullet: dict[str, Any]) -> int | None:
  """Extracts explicit fastener count if specified on a bullet."""
  explicit = bullet.get("fastener_count")
  if isinstance(explicit, int) and explicit > 0:
    return explicit
  text = str(bullet.get("text", "")).lower()
  match_nx = re.search(r"\b(\d+)\s*x\s*m\d", text)
  if match_nx:
    return int(match_nx.group(1))
  match_word = re.search(
      r"\b(one|two|three|four|five|six|seven|eight|\d+)\s+"
      r"(?:m\d[\w.-]*|tx\s*\d+|torx|phillips|allen|hex)\s+"
      r"(?:torx\s+)?(?:screws?|bolts?|nuts?)",
      text,
  )
  if match_word:
    token = match_word.group(1)
    return int(token) if token.isdigit() else WORD_NUMBERS.get(token)
  return None


def lint_guide(
    guide: dict[str, Any], allow_text_only: bool = False
) -> list[LintFinding]:
  """Audits a guide dictionary against the step-by-step authoring gates."""
  findings: list[LintFinding] = []
  title = str(guide.get("title", "")).strip()
  if not title:
    findings.append(
        LintFinding("G-SCHEMA", "ERROR", "Top-level 'title' is required.")
    )

  archetype = guide.get("archetype", "roundtrip")
  if archetype not in VALID_ARCHETYPES:
    findings.append(
        LintFinding(
            "G-SCHEMA",
            "ERROR",
            f"Invalid archetype '{archetype}'. Expected one of"
            f" {sorted(VALID_ARCHETYPES)}.",
        )
    )

  dialect = guide.get("default_dialect", "manual")
  if dialect not in VALID_DIALECTS:
    findings.append(
        LintFinding(
            "G-SCHEMA",
            "ERROR",
            f"Invalid default_dialect '{dialect}'. Expected 'manual' or"
            " 'workbench'.",
        )
    )

  steps = guide.get("steps")
  if not isinstance(steps, list) or not steps:
    findings.append(
        LintFinding("G-SCHEMA", "ERROR", "'steps' must be a non-empty list.")
    )
    return findings

  display_names = guide.get("display_names", {}) or {}
  meta_fields: list[tuple[str, str]] = [
      (f, str(guide.get(f, ""))) for f in ("title", "subtitle", "category")
  ]
  meta_fields += [
      (f"variants[{i}]", f"{v.get('label', '')} {v.get('note', '')}")
      for i, v in enumerate(guide.get("variants", []) or [])
  ]
  for s_i, s in enumerate(steps, start=1):
    meta_fields.append((f"step {s_i} title", str(s.get("title", ""))))
    meta_fields.append((f"step {s_i} milestone", str(s.get("milestone", ""))))
    meta_fields += [
        (f"step {s_i} bullet {b_i}", str(b.get("text", "")))
        for b_i, b in enumerate(s.get("bullets", []), start=1)
    ]
  for field, value in meta_fields:
    for pat in META_COPY_PATTERNS:
      if re.search(pat, value, re.IGNORECASE):
        findings.append(
            LintFinding(
                "G-META-COPY",
                "ERROR",
                f"{field}: Guide copy must describe the product, never the"
                " guide format. Remove references to other publishers' guide"
                " styles or 'print-ready'.",
            )
        )
        break

  has_asymmetric_cues = False
  for idx, step in enumerate(steps, start=1):
    snum = step.get("number", idx)
    stitle = str(step.get("title", "")).strip()
    prefix = f"Step {snum} ({stitle or 'untitled'})"
    if not stitle:
      findings.append(
          LintFinding("G-SCHEMA", "ERROR", f"{prefix}: Missing step 'title'.")
      )

    images = step.get("images", [])
    if not isinstance(images, list):
      findings.append(
          LintFinding("G-SCHEMA", "ERROR", f"{prefix}: 'images' must be list.")
      )
      images = []
    if not images and not allow_text_only:
      findings.append(
          LintFinding(
              "G-IMAGE-CAP",
              "ERROR",
              f"{prefix}: Has 0 visuals. Provide 1-3 visuals per step.",
          )
      )
    elif len(images) > 3:
      findings.append(
          LintFinding(
              "G-IMAGE-CAP",
              "ERROR",
              f"{prefix}: Has {len(images)} visuals (max 3). Split the step.",
          )
      )

    marker_colors: set[str] = set()
    circle_counts: dict[str, int] = {}
    is_staging = bool(images) and all(img.get("tool_lineup") for img in images)
    for img_i, img in enumerate(images, start=1):
      has_source = any(
          img.get(k) for k in ("src", "svg", "tool_lineup", "ui_screen")
      )
      if not has_source:
        findings.append(
            LintFinding(
                "G-SCHEMA",
                "ERROR",
                f"{prefix} visual {img_i}: Must set 'src', 'svg',"
                " 'tool_lineup', or 'ui_screen'.",
            )
        )
      for lineup_item in img.get("tool_lineup") or []:
        lkind = str(lineup_item.get("kind", "")).strip()
        if lkind not in VALID_TOOL_LINEUP_KINDS:
          findings.append(
              LintFinding(
                  "G-PLACEHOLDER-SHAPE",
                  "ERROR",
                  f"{prefix} visual {img_i}: tool_lineup item"
                  f" '{lineup_item.get('label', '?')}' uses unknown kind"
                  f" '{lkind}', which renders a generic dashed placeholder box."
                  " Use a 3D render ('src') for printed/custom parts or a"
                  " supported kind"
                  f" ({', '.join(sorted(VALID_TOOL_LINEUP_KINDS))}).",
              )
          )
      raw_svg = str(img.get("svg", ""))
      if raw_svg and "<image" not in raw_svg:
        circle_tags = len(re.findall(r"<(?:circle|ellipse)\b", raw_svg))
        has_plate_label = bool(
            re.search(r"\bplate\s*\d+\b", raw_svg, re.IGNORECASE)
        )
        is_part_staging_title = bool(
            re.search(
                r"\bstag(?:e|ing)\b.*\bparts?\b|\bprinted\s+parts?\b",
                stitle,
                re.IGNORECASE,
            )
        )
        if has_plate_label or (is_part_staging_title and circle_tags >= 3):
          findings.append(
              LintFinding(
                  "G-GENERIC-PART-SVG",
                  "WARN",
                  f"{prefix} visual {img_i}: Uses generic 2D SVG circles/boxes"
                  " to represent 3D parts. Replace flat 2D shapes with 3D"
                  " renders ('src') that accurately show part geometry,"
                  " bosses, pockets, and orientation.",
              )
          )
      img_colors = {
          m.get("color", "orange")
          for m in img.get("markers", [])
          if m.get("color", "orange") in SPATIAL_COLORS
      }
      if len(img_colors) > MAX_MARKER_COLORS_PER_IMAGE:
        findings.append(
            LintFinding(
                "G-MARKER-COLORS",
                "WARN",
                f"{prefix} visual {img_i}: Uses {len(img_colors)} marker colors"
                f" (max {MAX_MARKER_COLORS_PER_IMAGE}). Split the visual or"
                " merge bullets so the foreground stays readable.",
            )
        )
      svg_text = " ".join(
          re.findall(r"<text[^>]*>(.*?)</text>", str(img.get("svg", "")), re.S)
      )
      svg_text = _apply_display_names(
          re.sub(r"<[^>]+>", " ", svg_text), display_names
      )
      svg_leak = sorted(set(SNAKE_CASE_RE.findall(svg_text)))
      if svg_leak or CAD_COORD_RE.search(svg_text):
        findings.append(
            LintFinding(
                "G-CAD-LEAK",
                "WARN",
                f"{prefix} visual {img_i}: Diagram labels contain designer data"
                f" ({', '.join(svg_leak[:3]) or 'X/Y/Z coordinates'}).",
            )
        )
      for m in img.get("markers", []):
        mcolor = m.get("color", "orange")
        if mcolor not in COLOR_PALETTE:
          findings.append(
              LintFinding(
                  "G-SCHEMA",
                  "ERROR",
                  f"{prefix} visual {img_i}: Unknown marker color '{mcolor}'.",
              )
          )
          continue
        if m.get("shape") != "loupe" and mcolor in SPATIAL_COLORS:
          marker_colors.add(mcolor)
        if m.get("shape") == "circle":
          circle_counts[mcolor] = circle_counts.get(mcolor, 0) + 1
      circles_on_img = [
          m for m in img.get("markers", []) if m.get("shape") == "circle"
      ]
      for ci_idx, c1 in enumerate(circles_on_img):
        for c2 in circles_on_img[ci_idx + 1 :]:
          dist = math.hypot(
              float(c1.get("x", 0.0)) - float(c2.get("x", 0.0)),
              float(c1.get("y", 0.0)) - float(c2.get("y", 0.0)),
          )
          r_sum = float(c1.get("r", 3.8)) + float(c2.get("r", 3.8))
          if dist < r_sum * 0.92:
            findings.append(
                LintFinding(
                    "G-MARKER-OVERLAP",
                    "WARN",
                    f"{prefix} visual {img_i}: Circle markers at"
                    f" ({c1.get('x')}, {c1.get('y')}) and"
                    f" ({c2.get('x')}, {c2.get('y')}) overlap"
                    f" (distance {dist:.1f} < {r_sum:.1f}). For tightly"
                    " clustered fasteners in perspective or exploded views,"
                    " use an 'arrow' or 'rect' marker instead of overlapping"
                    " circles.",
                )
            )
            break

    bullets = step.get("bullets", [])
    if not isinstance(bullets, list) or not bullets:
      findings.append(
          LintFinding(
              "G-SCHEMA", "ERROR", f"{prefix}: Must contain at least 1 bullet."
          )
      )
      continue
    if len(bullets) > 7:
      findings.append(
          LintFinding(
              "G-BULLET-LOAD",
              "WARN",
              f"{prefix}: Has {len(bullets)} bullets (> 7). Split into smaller"
              " atomic steps.",
          )
      )

    bullet_colors: set[str] = set()
    bullet_color_order: list[str] = []
    action_indices: list[int] = []
    last_warning_index = -1

    for b_i, b in enumerate(bullets):
      btype = b.get("type", "action")
      btext = str(b.get("text", "")).strip()
      lower_text = btext.lower()

      mapped = _apply_display_names(btext, display_names)
      if re.search(
          r"\b(red|orange|yellow|green|cyan|blue|magenta)\b\s*"
          r"(ring|rings|box|boxes|arrow|arrows|circle|circles|marker|markers|outline)",
          lower_text,
      ):
        findings.append(
            LintFinding(
                "G-COLOR-WORD",
                "WARN",
                f"{prefix} bullet {b_i + 1}: Names a marker color in prose. The"
                " bullet glyph already carries the color, and recoloring makes"
                " the word stale.",
            )
        )
      leaked = sorted(set(SNAKE_CASE_RE.findall(mapped.replace("`", " "))))
      if leaked or CAD_COORD_RE.search(mapped):
        detail = ", ".join(leaked[:3]) if leaked else "X/Y/Z coordinates"
        findings.append(
            LintFinding(
                "G-CAD-LEAK",
                "WARN",
                f"{prefix} bullet {b_i + 1}: Builder copy contains designer"
                f" data ({detail}). Use human part names (or 'display_names')"
                " and drop CAD coordinates.",
            )
        )

      if re.search(
          r"\b(\d+(?:\.\d+)?\s*nm|lb-in|zip\s*tie|thermal\s*paste)\b",
          lower_text,
      ):
        has_asymmetric_cues = True

      if btype in ("action", "subaction"):
        action_indices.append(b_i)
        bcolor = b.get("color", "black")
        if bcolor not in COLOR_PALETTE:
          findings.append(
              LintFinding(
                  "G-SCHEMA",
                  "ERROR",
                  f"{prefix}: Unknown bullet color '{bcolor}'.",
              )
          )
        elif bcolor in SPATIAL_COLORS:
          bullet_colors.add(bcolor)
          if bcolor not in bullet_color_order:
            bullet_color_order.append(bcolor)
          fcount = _infer_fastener_count(b)
          ccount = circle_counts.get(bcolor, 0)
          if fcount is not None and ccount > 0 and fcount != ccount:
            findings.append(
                LintFinding(
                    "G-FASTENER-COUNT-SYNC",
                    "WARN",
                    f"{prefix}: '{bcolor}' bullet states {fcount} fastener(s)"
                    f" but visuals mark {ccount} '{bcolor}' circle(s).",
                )
            )
        for phrase in BANNED_ACTION_PHRASES:
          if phrase in lower_text:
            findings.append(
                LintFinding(
                    "G-VAGUE-FILLER",
                    "WARN",
                    f"{prefix}: Avoid weak/passive phrasing ('{phrase}'). Use"
                    " direct imperative verbs.",
                )
            )
      elif btype == "warning":
        last_warning_index = b_i
      elif btype == "info":
        if re.match(r"^(note|info)\s*:", lower_text):
          findings.append(
              LintFinding(
                  "G-NOTE-REDUNDANCY",
                  "WARN",
                  f"{prefix}: Omit literal 'Note:'/'Info:' prefix on 'info'"
                  " bullets; the icon already signals it.",
              )
          )
      elif btype == "pin":
        if re.match(r"^reminder\s*:", lower_text):
          findings.append(
              LintFinding(
                  "G-NOTE-REDUNDANCY",
                  "WARN",
                  f"{prefix}: Omit literal 'Reminder:' prefix on 'pin'"
                  " bullets.",
              )
          )
      else:
        findings.append(
            LintFinding(
                "G-SCHEMA", "ERROR", f"{prefix}: Unknown bullet type '{btype}'."
            )
        )

    if (
        last_warning_index != -1
        and action_indices
        and last_warning_index > action_indices[-1]
    ):
      findings.append(
          LintFinding(
              "G-WARN-ORDER",
              "ERROR",
              f"{prefix}: Trailing 'warning' appears after all action bullets."
              " Place warnings BEFORE the risky action they guard.",
          )
      )

    if is_staging and len(bullet_colors) > 1:
      findings.append(
          LintFinding(
              "G-STAGING-COLOR",
              "WARN",
              f"{prefix}: Tool/parts staging step color-codes"
              f" {len(bullet_colors)} items. Use black bullets and box at most"
              " one easily confused item.",
          )
      )
    expected = [c for c in COLOR_SEQUENCE if c in bullet_color_order]
    if bullet_color_order != expected:
      findings.append(
          LintFinding(
              "G-COLOR-ORDER",
              "WARN",
              f"{prefix}: Spatial colors appear as"
              f" {' -> '.join(bullet_color_order)}; assign them top to bottom"
              " in contrast-first order"
              f" ({' -> '.join(COLOR_SEQUENCE[:len(bullet_color_order)])}).",
          )
      )
    step_colors = bullet_colors | marker_colors
    if len(step_colors) < CONFUSABLE_MIN_COLORS:
      for pair in CONFUSABLE_PAIRS:
        if pair <= step_colors:
          a, b = sorted(pair)
          findings.append(
              LintFinding(
                  "G-COLOR-CONFUSABLE",
                  "WARN",
                  f"{prefix}: Uses near-neighbor hues '{a}' and '{b}' with only"
                  f" {len(step_colors)} colors. Use the contrast-first order"
                  " (red, blue, green) so callouts are easy to tell apart.",
              )
          )

    if images:
      missing_on_img = bullet_colors - marker_colors
      for col in sorted(missing_on_img):
        findings.append(
            LintFinding(
                "G-COLOR-SYNC",
                "ERROR",
                f"{prefix}: Bullet uses color '{col}' with no matching '{col}'"
                " marker on any visual in this step.",
            )
        )
      orphan_on_img = marker_colors - bullet_colors
      for col in sorted(orphan_on_img):
        findings.append(
            LintFinding(
                "G-COLOR-SYNC",
                "WARN",
                f"{prefix}: Visual has '{col}' marker with no matching '{col}'"
                " bullet in this step.",
            )
        )
      is_staging_title = bool(
          re.search(r"\bstag(?:e|ing)\b|\btools?\b", stitle, re.IGNORECASE)
      )
      is_complex_subassembly = not is_staging_title and bool(
          re.search(
              r"\b(?:sub-?assembly|spindle|pulley|servo\s+horn|timing\s+belt|"
              r"gt2.*belt|upper\s+bearing|hub\s+plate)\b",
              stitle,
              re.IGNORECASE,
          )
      )
      has_exploded_or_assembled_view = any(
          re.search(
              r"\b(?:exploded|stack|assembled|mated|wraps|context)\b",
              f"{img.get('caption', '')} {img.get('src', '')}",
              re.IGNORECASE,
          )
          for img in images
      )
      if (
          is_complex_subassembly
          and len(bullet_colors) >= 3
          and (len(images) < 2 or not has_exploded_or_assembled_view)
      ):
        findings.append(
            LintFinding(
                "G-SUBASSEMBLY-SINGLE-IMAGE",
                "WARN",
                f"{prefix}: Multi-part sub-assembly step must include paired 3D"
                " visuals: an Exploded Stack 3D render (coaxial alignment line"
                " + numbered 1..N stack order) and an Assembled In-Context"
                " (ghosted housing) 3D render.",
            )
        )

  if archetype == "teardown" and has_asymmetric_cues:
    findings.append(
        LintFinding(
            "G-ASYMMETRIC-REVERSAL",
            "ERROR",
            "Archetype 'teardown' cannot use reverse-order reassembly"
            " when torque specs or single-use consumables (zip ties, thermal"
            " paste) are present. Switch to 'roundtrip' with explicit"
            " reassembly steps.",
        )
    )
  return findings


_CODE_CHIP_RE = re.compile(
    r"(?<! )/(?!"
    r" )|\\|\$|--|\.[A-Za-z]{1,4}$|^\[|\(\)|^(?:python3?|sudo|cd|pip) "
)


def _render_code_span(match: re.Match[str]) -> str:
  """Keeps chips for commands, paths, and on-screen strings; bolds values."""
  content = match.group(1)
  if _CODE_CHIP_RE.search(content):
    return f"<code>{content}</code>"
  return f'<strong class="ag-val">{content}</strong>'


def _format_inline_md(text: str) -> str:
  """Converts inline bold, italic, code, and ASCII arrows safely to HTML.

  Backtick spans become monospace chips only for commands, file paths, and
  on-screen strings. Measurements and part numbers render as bold values so
  bullets keep a readable prose rhythm.

  Args:
    text: Bullet or caption text with lightweight Markdown.

  Returns:
    Escaped HTML.
  """
  escaped = html.escape(text)
  escaped = escaped.replace("-&gt;", "→")
  escaped = re.sub(r"`([^`]+)`", _render_code_span, escaped)
  escaped = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", escaped)
  escaped = re.sub(r"\*([^*]+)\*", r"<em>\1</em>", escaped)
  escaped = re.sub(r"\(\s+", "(", escaped)
  escaped = re.sub(r"\s+\)", ")", escaped)
  return escaped


def _resolve_image_src(src: str, base_dir: pathlib.Path, embed: bool) -> str:
  if not embed or src.startswith(("http://", "https://", "data:")):
    return src
  candidate = (base_dir / src).resolve()
  if not candidate.is_file():
    return src
  mime, _ = mimetypes.guess_type(str(candidate))
  mime = mime or "image/png"
  encoded = base64.b64encode(candidate.read_bytes()).decode("ascii")
  return f"data:{mime};base64,{encoded}"


def _render_tool_silhouette(kind: str, cx: float, scale: float) -> str:
  """Renders clean orthographic tool/part silhouettes in a 400x300 viewBox."""
  top = 225 - int(155 * scale)
  bot = 225
  if kind in ("torx_key", "hex_key"):
    arm = int(26 * scale)
    stroke_w = 5 if scale >= 0.9 else 4
    tip = (
        f'<circle cx="{cx}" cy="{bot}" r="3.2" fill="#27272a"/>'
        if kind == "torx_key"
        else ""
    )
    return (
        f'<path d="M {cx - arm} {top} L {cx - 3} {top} Q {cx} {top} {cx}'
        f' {top + 4} L {cx} {bot}" fill="none" stroke="#27272a"'
        f' stroke-width="{stroke_w}" stroke-linecap="round"/>{tip}'
    )
  if kind == "wrench":
    return (
        f'<rect x="{cx - 7}" y="{top + 18}" width="14"'
        f' height="{bot - top - 36}" rx="4" fill="#d4d4d8" stroke="#52525b"'
        ' stroke-width="2"/>'
        f'<circle cx="{cx}" cy="{top + 18}" r="14" fill="#d4d4d8"'
        ' stroke="#52525b" stroke-width="2"/>'
        f'<rect x="{cx - 5}" y="{top + 2}" width="10" height="14" fill="#fff"/>'
        f'<circle cx="{cx}" cy="{bot - 14}" r="12" fill="#d4d4d8"'
        ' stroke="#52525b" stroke-width="2"/>'
        f'<rect x="{cx - 4}" y="{bot - 26}" width="8" height="12"'
        ' transform="rotate(180 '
        f'{cx} {bot - 14})" fill="#fff"/>'
    )
  if kind == "universal_wrench":
    return (
        f'<path d="M {cx - 8} {top + 12} L {cx + 8} {top + 12} L {cx + 12}'
        f" {cx * 0 + 145} L {cx + 18} 155 L {cx + 8} 170 L {cx + 8} {bot - 10}"
        f' L {cx - 8} {bot - 10} Z" fill="#a1a1aa" stroke="#3f3f46"'
        ' stroke-width="2"/>'
        f'<polygon points="{cx},132 {cx + 6},136 {cx + 6},143 {cx},147'
        f' {cx - 6},143 {cx - 6},136" fill="#fff" stroke="#3f3f46"'
        ' stroke-width="1.5"/>'
    )
  if kind == "screwdriver":
    return (
        f'<line x1="{cx}" y1="{top + 6}" x2="{cx}" y2="148" stroke="#52525b"'
        ' stroke-width="4" stroke-linecap="round"/>'
        f'<rect x="{cx - 11}" y="146" width="22" height="78" rx="9"'
        ' fill="#3f3f46" stroke="#18181b" stroke-width="2"/>'
    )
  if kind == "soldering_iron":
    return (
        f'<line x1="{cx}" y1="{top + 4}" x2="{cx}" y2="{top + 40}"'
        ' stroke="#71717a" stroke-width="2.5" stroke-linecap="round"/><rect'
        f' x="{cx - 4}" y="{top + 40}" width="8" height="30" rx="2"'
        ' fill="#a1a1aa" stroke="#52525b" stroke-width="1.5"/><rect'
        f' x="{cx - 9}" y="{top + 70}" width="18" height="{bot - top - 70}"'
        ' rx="7" fill="#3f3f46" stroke="#18181b" stroke-width="2"/>'
    )
  if kind == "pliers":
    return (
        f'<path d="M {cx - 2} {top + 6} L {cx - 3} {top + 60}'
        f' M {cx + 2} {top + 6} L {cx + 3} {top + 60}" fill="none"'
        ' stroke="#52525b" stroke-width="4" stroke-linecap="round"/>'
        f'<circle cx="{cx}" cy="{top + 66}" r="5" fill="#a1a1aa"'
        ' stroke="#52525b" stroke-width="1.5"/>'
        f'<path d="M {cx - 3} {top + 70} Q {cx - 14} {top + 110} {cx - 12}'
        f" {bot} M {cx + 3} {top + 70} Q {cx + 14} {top + 110} {cx + 12}"
        f' {bot}" fill="none" stroke="#3f3f46" stroke-width="7"'
        ' stroke-linecap="round"/>'
    )
  if kind == "mat":
    return (
        f'<polygon points="{cx - 26},178 {cx + 6},160 {cx + 30},172'
        f' {cx - 2},192" fill="#e4e4e7" stroke="#71717a" stroke-width="2"'
        ' stroke-linejoin="round"/>'
        f'<polyline points="{cx - 26},178 {cx - 26},182 {cx - 2},196'
        f' {cx + 30},176 {cx + 30},172" fill="none" stroke="#71717a"'
        ' stroke-width="2" stroke-linejoin="round"/>'
    )
  if kind == "spudger":
    return (
        f'<path d="M {cx - 4} {top + 14} L {cx + 4} {top + 8} L {cx + 5}'
        f' {bot - 12} L {cx} {bot} L {cx - 5} {bot - 12} Z" fill="#27272a"/>'
    )
  if kind == "tweezers":
    return (
        f'<path d="M {cx} {top + 8} L {cx - 9} {bot - 4} M {cx} {top + 8}'
        f' L {cx + 9} {bot - 4}" fill="none" stroke="#3f3f46"'
        ' stroke-width="3.5" stroke-linecap="round"/>'
        f'<circle cx="{cx}" cy="{top + 10}" r="3.5" fill="#27272a"/>'
    )
  if kind == "pcb":
    return (
        f'<rect x="{cx - 40}" y="114" width="80" height="72" rx="5"'
        ' fill="#15803d" stroke="#14532d" stroke-width="2.2"/>'
        f'<rect x="{cx - 16}" y="136" width="32" height="28" rx="2"'
        ' fill="#27272a"/>'
        f'<circle cx="{cx - 32}" cy="122" r="3" fill="#eab308"/>'
        f'<circle cx="{cx + 32}" cy="122" r="3" fill="#eab308"/>'
        f'<circle cx="{cx - 32}" cy="178" r="3" fill="#eab308"/>'
        f'<circle cx="{cx + 32}" cy="178" r="3" fill="#eab308"/>'
    )
  if kind == "cable":
    return (
        f'<path d="M {cx - 52} 166 C {cx - 20} 118, {cx + 20} 182,'
        f' {cx + 50} 134" fill="none" stroke="#27272a" stroke-width="4.5"'
        ' stroke-linecap="round"/>'
        f'<rect x="{cx - 60}" y="160" width="12" height="12" rx="2"'
        ' fill="#f4f4f5" stroke="#52525b" stroke-width="1.5"/>'
        f'<rect x="{cx + 48}" y="128" width="12" height="12" rx="2"'
        ' fill="#f4f4f5" stroke="#52525b" stroke-width="1.5"/>'
    )
  if kind == "brass_brush":
    return (
        f'<rect x="{cx - 18}" y="{top + 18}" width="12" height="34" rx="2"'
        f' fill="#a1a1aa"/><rect x="{cx - 6}" y="{top + 14}" width="10"'
        f' height="{bot - top - 14}" rx="4" fill="#e7e5e4" stroke="#a8a29e"'
        ' stroke-width="2"/>'
    )
  if kind == "cardboard_box":
    return (
        f'<polygon points="{cx - 62},140 {cx + 10},108 {cx + 68},136'
        f' {cx - 4},168" fill="#d6b88d" stroke="#8c6d46" stroke-width="2"/>'
        f'<polygon points="{cx - 62},140 {cx - 4},168 {cx - 4},196'
        f' {cx - 62},168" fill="#bfa074" stroke="#8c6d46" stroke-width="2"/>'
        f'<polygon points="{cx - 4},168 {cx + 68},136 {cx + 68},164'
        f' {cx - 4},196" fill="#c9ab80" stroke="#8c6d46" stroke-width="2"/>'
    )
  if kind == "zip_tie":
    return (
        f'<path d="M {cx - 65} 135 Q {cx} 152 {cx + 62} 165" fill="none"'
        ' stroke="#27272a" stroke-width="3.5" stroke-linecap="round"/>'
        f'<rect x="{cx + 58}" y="160" width="9" height="10" rx="1.5"'
        ' fill="#18181b"/>'
    )
  if kind == "fan":
    return (
        f'<rect x="{cx - 42}" y="110" width="84" height="84" rx="6"'
        ' fill="#27272a" stroke="#18181b" stroke-width="2.5"/>'
        f'<circle cx="{cx}" cy="152" r="28" fill="#3f3f46" stroke="#18181b"'
        ' stroke-width="2"/>'
        f'<circle cx="{cx}" cy="152" r="13" fill="#52525b"/>'
        f'<path d="M {cx - 8} 110 C {cx - 12} 82, {cx + 28} 78, {cx + 46} 94"'
        ' fill="none" stroke="#dc2626" stroke-width="2.2"/>'
        f'<path d="M {cx - 5} 110 C {cx - 9} 85, {cx + 28} 81, {cx + 46} 97"'
        ' fill="none" stroke="#eab308" stroke-width="1.8"/>'
    )
  if kind == "nozzle":
    return (
        f'<line x1="{cx - 54}" y1="108" x2="{cx + 8}" y2="156"'
        ' stroke="#a1a1aa" stroke-width="6" stroke-linecap="round"/>'
        f'<line x1="{cx + 8}" y1="156" x2="{cx + 20}" y2="165"'
        ' stroke="#ea580c" stroke-width="7"/>'
        f'<line x1="{cx + 20}" y1="165" x2="{cx + 42}" y2="182"'
        ' stroke="#eab308" stroke-width="10" stroke-linecap="butt"/>'
        f'<polygon points="{cx + 42},177 {cx + 52},189 {cx + 39},187"'
        ' fill="#ca8a04"/>'
    )
  return (
      f'<rect x="{cx - 22}" y="128" width="44" height="56" rx="6"'
      ' fill="#f4f4f5" stroke="#a1a1aa" stroke-width="2"'
      ' stroke-dasharray="4 3"/>'
  )


# Approximate natural widths (viewBox px) used to scale silhouettes into slots.
_SILHOUETTE_WIDTHS = {
    "cardboard_box": 136,
    "zip_tie": 136,
    "fan": 92,
    "nozzle": 110,
    "pcb": 84,
    "cable": 124,
    "mat": 64,
    "wrench": 32,
    "universal_wrench": 40,
}
# Character width in em for the lineup label font (bold system sans).
_LABEL_EM_WIDTH = 0.6


def _wrap_label(label: str, max_chars: int) -> list[str]:
  """Greedy word wrap into at most two lines."""
  words = label.split()
  lines: list[str] = []
  current = ""
  for word in words:
    candidate = f"{current} {word}".strip()
    if len(candidate) <= max_chars or not current:
      current = candidate
    else:
      lines.append(current)
      current = word
  if current:
    lines.append(current)
  if len(lines) > 2:
    lines = [lines[0], " ".join(lines[1:])]
  return lines


def _render_tool_lineup(items: list[dict[str, Any]]) -> str:
  """Renders a neutral, full-width lineup with labels sized to fit slots."""
  n = max(1, len(items))
  margin = 14.0
  slot_w = (400.0 - 2 * margin) / n
  parts = ['<rect width="400" height="300" fill="#fff"/>']
  for i, item in enumerate(items):
    cx = margin + slot_w * (i + 0.5)
    kind = str(item.get("kind", ""))
    scale = float(item.get("scale", 0.9))
    natural = _SILHOUETTE_WIDTHS.get(kind, 0)
    shape = _render_tool_silhouette(kind, cx, scale)
    fit = min(1.0, (slot_w - 8) / natural) if natural else 1.0
    if fit < 1.0:
      shape = (
          f'<g transform="translate({cx:.1f} 225) scale({fit:.3f})'
          f' translate({-cx:.1f} -225)">{shape}</g>'
      )
    parts.append(shape)
    label = str(item.get("label", "")).strip()
    if not label:
      continue
    font = 12.0
    lines = _wrap_label(
        label, max(4, int((slot_w - 6) / (font * _LABEL_EM_WIDTH)))
    )
    longest = max(len(line) for line in lines)
    while font > 8.5 and longest * font * _LABEL_EM_WIDTH > slot_w - 6:
      font -= 0.5
      lines = _wrap_label(
          label, max(4, int((slot_w - 6) / (font * _LABEL_EM_WIDTH)))
      )
      longest = max(len(line) for line in lines)
    tspans = "".join(
        f'<tspan x="{cx:.1f}" dy="{0 if j == 0 else font * 1.2:.1f}">'
        f"{html.escape(line)}</tspan>"
        for j, line in enumerate(lines)
    )
    parts.append(
        f'<text class="ag-lineup-label" data-slot-w="{slot_w:.1f}"'
        f' x="{cx:.1f}" y="250" text-anchor="middle"'
        ' font-family="system-ui, -apple-system, sans-serif"'
        f' font-size="{font:.1f}" font-weight="600" fill="#27272a">'
        f"{tspans}</text>"
    )
  return "".join(parts)


def _fit_screen_text(
    text: str, width_px: float, font: float, floor: float
) -> tuple[str, float]:
  """Shrinks, then truncates, text so it fits a monospace column.

  Args:
    text: Row text to fit.
    width_px: Available column width in viewBox pixels.
    font: Starting font size.
    floor: Smallest allowed font size.

  Returns:
    A tuple of (fitted text, font size).
  """
  char_w = 0.6
  while font > floor and len(text) * font * char_w > width_px:
    font -= 0.5
  max_chars = int(width_px / (font * char_w))
  if len(text) > max_chars:
    text = text[: max(1, max_chars - 1)].rstrip() + "…"
  return text, font


NEUTRAL_FILTER_ID = "ag-neutral"


def _neutral_filter_def(uid: str) -> str:
  """Desaturates base visuals so only markers carry saturated color."""
  return (
      f'<defs><filter id="{uid}"'
      ' color-interpolation-filters="sRGB"><feColorMatrix type="saturate"'
      ' values="0.06"/><feComponentTransfer><feFuncR type="linear" slope="0.9"'
      ' intercept="0.08"/><feFuncG type="linear" slope="0.9"'
      ' intercept="0.08"/><feFuncB type="linear" slope="0.9"'
      ' intercept="0.08"/></feComponentTransfer></filter></defs>'
  )


def _build_base_visual_svg(
    img: dict[str, Any], base_dir: pathlib.Path, embed: bool
) -> tuple[str, bool]:
  """Returns (inner_svg_markup_400x300, is_raster_src)."""
  if img.get("src"):
    resolved = html.escape(_resolve_image_src(img["src"], base_dir, embed))
    return (
        (
            '<rect width="400" height="300" fill="#fff"/>'
            f'<image href="{resolved}" x="0" y="0" width="400" height="300"'
            ' preserveAspectRatio="xMidYMid meet"/>'
        ),
        True,
    )
  if img.get("tool_lineup"):
    return _render_tool_lineup(img["tool_lineup"]), False

  if img.get("ui_screen"):
    scr = img["ui_screen"]
    dev = html.escape(str(scr.get("device_label", "DEVICE")))
    crumb = html.escape(str(scr.get("breadcrumb", "MENU")))
    rows = scr.get("rows", [])
    active_idx = scr.get("active_index", -1)
    footer = html.escape(str(scr.get("footer", "")))
    out = [
        '<rect width="400" height="300" fill="#18181b"/>',
        (
            '<rect x="18" y="18" width="364" height="264" rx="10"'
            ' fill="#27272a" stroke="#3f3f46" stroke-width="2"/>'
        ),
        (
            '<text x="38" y="255" transform="rotate(-90 38 255)"'
            ' font-family="system-ui, sans-serif" font-size="14"'
            ' font-weight="800" letter-spacing="1.5"'
            f' fill="#f97316">{dev}</text>'
        ),
        (
            '<rect x="64" y="38" width="286" height="218" rx="4" fill="#09090b"'
            ' stroke="#3f3f46" stroke-width="1.5"/>'
        ),
        (
            '<text x="80" y="60" font-family="ui-monospace, monospace"'
            f' font-size="10.5" font-weight="700" fill="#a1a1aa">{crumb}</text>'
        ),
        '<line x1="76" y1="68" x2="338" y2="68" stroke="#27272a"/>',
    ]
    for r_i, row_text in enumerate(rows[:6]):
      ry = 80 + r_i * 25
      is_active = r_i == active_idx
      if is_active:
        out.append(
            f'<rect x="76" y="{ry - 13}" width="262" height="21" rx="2"'
            ' fill="#f4f4f5"/>'
        )
      fill = "#09090b" if is_active else "#e4e4e7"
      row_fit, row_font = _fit_screen_text(str(row_text), 246.0, 11.5, 8.5)
      out.append(
          f'<text x="86" y="{ry + 2}" font-family="ui-monospace, monospace"'
          f' font-size="{row_font:.1f}" font-weight="600" fill="{fill}">'
          f"{html.escape(row_fit)}</text>"
      )
    if footer:
      foot_fit, foot_font = _fit_screen_text(
          html.unescape(footer), 250.0, 10.0, 8.0
      )
      out.append(
          '<text x="80" y="244" font-family="ui-monospace, monospace"'
          f' font-size="{foot_font:.1f}" fill="#f97316">'
          f"{html.escape(foot_fit)}</text>"
      )
    out.append(
        '<circle cx="366" cy="252" r="10" fill="#18181b" stroke="#f97316"'
        ' stroke-width="1.5"/>'
    )
    return "".join(out), False

  raw_svg = str(img.get("svg", ""))
  if embed:
    raw_svg = re.sub(
        r'(<image\b[^>]*?\bhref=")([^"]+)(")',
        lambda m: (
            f"{m.group(1)}"
            f"{html.escape(_resolve_image_src(m.group(2), base_dir, True))}"
            f"{m.group(3)}"
        ),
        raw_svg,
    )
  return f'<rect width="400" height="300" fill="#f8fafc"/>{raw_svg}', False


def _render_marker_svg(m: dict[str, Any], base_svg: str, uid: str) -> str:
  """Renders one vector marker in the 400x300 viewBox."""
  color_key = str(m.get("color", "orange"))
  pal = COLOR_PALETTE.get(color_key, COLOR_PALETTE["orange"])
  stroke = pal["hex"]
  halo = pal["halo"]
  shape = m.get("shape", "circle")
  attr = f'class="ag-marker" data-color="{html.escape(color_key)}"'

  if shape == "circle":
    cx = float(m.get("x", 50)) * 4.0
    cy = float(m.get("y", 50)) * 3.0
    r = float(m.get("r", 5.5)) * 4.0
    return (
        f"<g {attr}>"
        f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="none"'
        f' stroke="{halo}" stroke-width="5.5" opacity="0.92"/>'
        f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="none"'
        f' stroke="{stroke}" stroke-width="3"/>'
        "</g>"
    )
  if shape == "rect":
    rx = float(m.get("x", 20)) * 4.0
    ry = float(m.get("y", 20)) * 3.0
    rw = float(m.get("w", 20)) * 4.0
    rh = float(m.get("h", 20)) * 3.0
    return (
        f"<g {attr}>"
        f'<rect x="{rx:.1f}" y="{ry:.1f}" width="{rw:.1f}" height="{rh:.1f}"'
        f' rx="3" fill="none" stroke="{halo}" stroke-width="5" opacity="0.9"/>'
        f'<rect x="{rx:.1f}" y="{ry:.1f}" width="{rw:.1f}" height="{rh:.1f}"'
        f' rx="3" fill="none" stroke="{stroke}" stroke-width="2.6"/>'
        "</g>"
    )
  if shape == "arrow":
    x1 = float(m.get("x1", 25)) * 4.0
    y1 = float(m.get("y1", 70)) * 3.0
    x2 = float(m.get("x2", 50)) * 4.0
    y2 = float(m.get("y2", 50)) * 3.0
    ang = math.atan2(y2 - y1, x2 - x1)
    head_len = 13.0
    ax1 = x2 - head_len * math.cos(ang - 0.48)
    ay1 = y2 - head_len * math.sin(ang - 0.48)
    ax2 = x2 - head_len * math.cos(ang + 0.48)
    ay2 = y2 - head_len * math.sin(ang + 0.48)
    path_d = (
        f"M {x1:.1f} {y1:.1f} L {x2:.1f} {y2:.1f}"
        f" M {ax1:.1f} {ay1:.1f} L {x2:.1f} {y2:.1f} L {ax2:.1f} {ay2:.1f}"
    )
    return (
        f"<g {attr}>"
        f'<path d="{path_d}" fill="none" stroke="{halo}" stroke-width="5.6"'
        ' stroke-linecap="round" stroke-linejoin="round" opacity="0.92"/>'
        f'<path d="{path_d}" fill="none" stroke="{stroke}" stroke-width="3"'
        ' stroke-linecap="round" stroke-linejoin="round"/>'
        "</g>"
    )
  if shape == "arc":
    cx = float(m.get("x", 50)) * 4.0
    cy = float(m.get("y", 50)) * 3.0
    r = float(m.get("r", 12)) * 4.0
    s_deg = float(m.get("start_deg", -40))
    e_deg = float(m.get("end_deg", 140))
    direction = str(m.get("direction", "cw"))
    s_rad = math.radians(s_deg)
    e_rad = math.radians(e_deg)
    sx, sy = cx + r * math.cos(s_rad), cy + r * math.sin(s_rad)
    ex, ey = cx + r * math.cos(e_rad), cy + r * math.sin(e_rad)
    sweep_deg = (e_deg - s_deg) % 360
    large_arc = 1 if sweep_deg > 180 else 0
    tip_x, tip_y = (ex, ey) if direction == "cw" else (sx, sy)
    tan_ang = (
        (e_rad + math.pi / 2.0)
        if direction == "cw"
        else (s_rad - math.pi / 2.0)
    )
    hl = 12.0
    hx1 = tip_x - hl * math.cos(tan_ang - 0.5)
    hy1 = tip_y - hl * math.sin(tan_ang - 0.5)
    hx2 = tip_x - hl * math.cos(tan_ang + 0.5)
    hy2 = tip_y - hl * math.sin(tan_ang + 0.5)
    arc_d = (
        f"M {sx:.1f} {sy:.1f} A {r:.1f} {r:.1f} 0 {large_arc} 1"
        f" {ex:.1f} {ey:.1f}"
        f" M {hx1:.1f} {hy1:.1f} L {tip_x:.1f} {tip_y:.1f}"
        f" L {hx2:.1f} {hy2:.1f}"
    )
    return (
        f"<g {attr}>"
        f'<path d="{arc_d}" fill="none" stroke="{halo}" stroke-width="5.2"'
        ' stroke-linecap="round" stroke-linejoin="round" opacity="0.9"/>'
        f'<path d="{arc_d}" fill="none" stroke="{stroke}" stroke-width="2.8"'
        ' stroke-linecap="round" stroke-linejoin="round"/>'
        "</g>"
    )
  if shape == "loupe":
    cx = float(m.get("x", 22)) * 4.0
    cy = float(m.get("y", 26)) * 3.0
    tx = float(m.get("target_x", 50)) * 4.0
    ty = float(m.get("target_y", 50)) * 3.0
    lr = float(m.get("r", 16)) * 4.0
    zoom = float(m.get("zoom", 2.3))
    dx, dy = tx - cx, ty - cy
    dist = max(1.0, math.hypot(dx, dy))
    lx = cx + (dx / dist) * lr
    ly = cy + (dy / dist) * lr
    tx_in = cx - tx * zoom
    ty_in = cy - ty * zoom
    return (
        f"<g {attr}>"
        f'<defs><clipPath id="{uid}">'
        f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{lr:.1f}"/>'
        "</clipPath></defs>"
        f'<line x1="{lx:.1f}" y1="{ly:.1f}" x2="{tx:.1f}" y2="{ty:.1f}"'
        f' stroke="#fff" stroke-width="4.5" opacity="0.9"/>'
        f'<line x1="{lx:.1f}" y1="{ly:.1f}" x2="{tx:.1f}" y2="{ty:.1f}"'
        f' stroke="{stroke}" stroke-width="2.4"/>'
        f'<g clip-path="url(#{uid})">'
        f'<rect x="{cx - lr:.1f}" y="{cy - lr:.1f}" width="{2 * lr:.1f}"'
        f' height="{2 * lr:.1f}" fill="#fff"/>'
        f'<g transform="translate({tx_in:.1f},{ty_in:.1f}) scale({zoom:.2f})">'
        f"{base_svg}</g></g>"
        f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{lr:.1f}" fill="none"'
        ' stroke="#fff" stroke-width="5"/>'
        f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{lr:.1f}" fill="none"'
        f' stroke="{stroke}" stroke-width="3"/>'
        "</g>"
    )
  return ""


def _render_visual_svg(
    img: dict[str, Any],
    step_idx: int,
    img_idx: int,
    base_dir: pathlib.Path,
    embed: bool,
    neutralize: bool = True,
) -> tuple[str, set[str]]:
  """Builds a complete 4:3 SVG visual with markers.

  When `neutralize` is set (default), the base visual is desaturated so the
  colored markers are the only saturated elements in the frame. Set
  `"neutralize": false` on an image when hue itself is the datum (for example,
  wire colors).

  Args:
    img: Image spec from the guide.
    step_idx: Step number, used for unique SVG ids.
    img_idx: Image index within the step.
    base_dir: Directory used to resolve relative image paths.
    embed: Whether to inline local raster images as data URIs.
    neutralize: Whether to desaturate the base visual.

  Returns:
    A tuple of (svg_html, spatial marker colors used).
  """
  base_svg, _ = _build_base_visual_svg(img, base_dir, embed)
  defs = ""
  if neutralize and img.get("neutralize", True):
    fid = f"{NEUTRAL_FILTER_ID}-s{step_idx}-i{img_idx}"
    defs = _neutral_filter_def(fid)
    base_svg = f'<g filter="url(#{fid})">{base_svg}</g>'
  markers_html: list[str] = []
  colors: set[str] = set()
  for m_i, m in enumerate(img.get("markers", [])):
    col = str(m.get("color", "orange"))
    if col in SPATIAL_COLORS:
      colors.add(col)
    uid = f"loupe-s{step_idx}-i{img_idx}-m{m_i}"
    markers_html.append(_render_marker_svg(m, base_svg, uid))
  caption = html.escape(
      str(img.get("caption", f"Step {step_idx} visual {img_idx + 1}"))
  )
  svg_str = (
      '<svg class="ag-visual-svg" viewBox="0 0 400 300" role="img"'
      f' aria-label="{caption}" xmlns="http://www.w3.org/2000/svg">'
      f"{defs}{base_svg}{''.join(markers_html)}</svg>"
  )
  return svg_str, colors


def _bullet_icon_svg(btype: str, color_key: str) -> str:
  """Returns bullet icon HTML (hexagon or ring glyph by layout, or a semantic icon)."""
  if btype == "warning":
    return (
        '<span class="ag-icon ag-icon-warn" aria-hidden="true">'
        '<svg viewBox="0 0 24 24" width="22" height="22" fill="none">'
        '<path d="M12 3.2L2.4 20h19.2L12 3.2z" stroke="#c62828"'
        ' stroke-width="2" stroke-linejoin="round"/>'
        '<line x1="12" y1="9" x2="12" y2="14.2" stroke="#c62828"'
        ' stroke-width="2.2" stroke-linecap="round"/>'
        '<circle cx="12" cy="17.2" r="1.2" fill="#c62828"/>'
        "</svg></span>"
    )
  if btype == "info":
    return (
        '<span class="ag-icon ag-icon-info" aria-hidden="true">'
        '<svg viewBox="0 0 24 24" width="21" height="21" fill="none">'
        '<circle cx="12" cy="12" r="9.5" stroke="#18181b" stroke-width="1.8"/>'
        '<line x1="12" y1="10.8" x2="12" y2="16.8" stroke="#18181b"'
        ' stroke-width="2.1" stroke-linecap="round"/>'
        '<circle cx="12" cy="7.5" r="1.25" fill="#18181b"/>'
        "</svg></span>"
    )
  if btype == "pin":
    return (
        '<span class="ag-icon ag-icon-pin" aria-hidden="true">'
        '<svg viewBox="0 0 24 24" width="21" height="21" fill="none">'
        '<path d="M8 4h8l-1.2 5.2 2.7 2.8v1.5H6.5V12l2.7-2.8L8 4z"'
        ' stroke="#18181b" stroke-width="1.8" stroke-linejoin="round"/>'
        '<line x1="12" y1="13.5" x2="12" y2="20" stroke="#18181b"'
        ' stroke-width="1.9" stroke-linecap="round"/>'
        "</svg></span>"
    )
  hex_col = COLOR_PALETTE.get(color_key, COLOR_PALETTE["black"])["hex"]
  return (
      '<span class="ag-icon ag-icon-bullet" aria-hidden="true">'
      '<svg class="ag-glyph-hex" viewBox="0 0 20 20" width="15" height="15">'
      '<polygon points="10,1.5 17.5,5.8 17.5,14.2 10,18.5 2.5,14.2 2.5,5.8"'
      f' fill="{hex_col}"/></svg>'
      '<svg class="ag-glyph-ring" viewBox="0 0 20 20" width="15" height="15">'
      f'<circle cx="10" cy="10" r="7.5" fill="none" stroke="{hex_col}"'
      ' stroke-width="2.2"/>'
      f'<circle cx="10" cy="10" r="3.8" fill="{hex_col}"/></svg></span>'
  )


def _localize_guide(guide: dict[str, Any]) -> dict[str, Any]:
  """Returns a deep copy with `display_names` applied to builder-facing text."""
  names = guide.get("display_names") or {}
  if not names:
    return guide
  out = json.loads(json.dumps(guide))
  for key in ("title", "subtitle"):
    if out.get(key):
      out[key] = _apply_display_names(str(out[key]), names)
  for coll, fields in (("tools", ("name", "spec")), ("parts", ("name", "qty"))):
    for item in out.get(coll, []):
      for f in fields:
        if item.get(f):
          item[f] = _apply_display_names(str(item[f]), names)
  for v in out.get("variants", []):
    for f in ("label", "note"):
      if v.get(f):
        v[f] = _apply_display_names(str(v[f]), names)
  for step in out.get("steps", []):
    for f in ("title", "milestone"):
      if step.get(f):
        step[f] = _apply_display_names(str(step[f]), names)
    for b in step.get("bullets", []):
      b["text"] = _apply_display_names(str(b.get("text", "")), names)
    for img in step.get("images", []):
      if img.get("caption"):
        img["caption"] = _apply_display_names(str(img["caption"]), names)
      if img.get("svg"):
        img["svg"] = _apply_display_names(str(img["svg"]), names)
  return out


def _inventory_table(title: str, rows: list[tuple[str, str]]) -> str:
  """Two-column inventory with a shared column grid so specs align."""
  if not rows:
    return ""
  body = "".join(
      f'<tr><th scope="row">{html.escape(name)}</th>'
      f"<td>{html.escape(meta)}</td></tr>"
      for name, meta in rows
  )
  return (
      f'<section class="ag-inv-box"><h3>{html.escape(title)}</h3>'
      '<table class="ag-inv-table"><colgroup><col class="ag-inv-col-name"/>'
      f'<col class="ag-inv-col-meta"/></colgroup><tbody>{body}</tbody></table>'
      "</section>"
  )


def render_html(
    guide: dict[str, Any],
    base_dir: pathlib.Path,
    embed_images: bool = False,
    dialect_override: str | None = None,
    paper: str = "A4",
    pdf_href: str | None = None,
) -> str:
  """Compiles a validated guide dictionary into a self-contained HTML file."""
  paper = "letter" if str(paper).lower() == "letter" else "A4"
  guide = _localize_guide(guide)
  neutralize = bool(guide.get("neutralize_base_visuals", True))
  title = html.escape(str(guide.get("title", "Assembly Guide")))
  subtitle = _format_inline_md(str(guide.get("subtitle", "")))
  category = html.escape(str(guide.get("category", "Assembly & Maintenance")))
  guide_id = html.escape(str(guide.get("guide_id", "")))
  canonical_url = html.escape(str(guide.get("canonical_url", "")))
  archetype = str(guide.get("archetype", "roundtrip"))
  default_dialect = dialect_override or str(
      guide.get("default_dialect", "manual")
  )
  difficulty = str(guide.get("difficulty", "Moderate"))
  time_req = html.escape(str(guide.get("time_required", "30 minutes")))
  steps = guide.get("steps", [])

  diff_idx = (
      VALID_DIFFICULTIES.index(difficulty) + 1
      if difficulty in VALID_DIFFICULTIES
      else 3
  )
  bars_html = "".join(
      f'<span class="ag-diff-seg{" active" if i < diff_idx else ""}"></span>'
      for i in range(5)
  )

  inventory_html = (
      '<div class="ag-inventory">'
      + _inventory_table(
          "Necessary tools",
          [
              (str(t.get("name", "")), str(t.get("spec", "")))
              for t in guide.get("tools", [])
          ],
      )
      + _inventory_table(
          "Parts and consumables",
          [
              (str(p.get("name", "")), str(p.get("qty", "")))
              for p in guide.get("parts", [])
          ],
      )
      + "</div>"
  )

  toc_items = "".join(
      f'<li><a href="#step-{s.get("number", i)}">'
      f'<span>Step {s.get("number", i)} — '
      f'{html.escape(str(s.get("title", "")))}</span>'
      "</a></li>"
      for i, s in enumerate(steps, start=1)
  )

  variants_html = ""
  variants = guide.get("variants") or []
  if variants:
    lines = [
        "<strong>"
        f'{html.escape(str(v.get("label", "")))}.</strong> '
        f'{_format_inline_md(str(v.get("note", "")))}'
        for v in variants
    ]
    inner = (
        f"<p>{lines[0]}</p>"
        if len(lines) == 1
        else "<ul>" + "".join(f"<li>{x}</li>" for x in lines) + "</ul>"
    )
    variants_html = (
        '<div class="ag-variants" role="note" aria-label="Hardware variants">'
        f'{_bullet_icon_svg("info", "black")}<div>{inner}</div></div>'
    )

  cheatsheet_html = ""
  fasteners = guide.get("fastener_cheatsheet", [])
  if fasteners:
    f_cards = []
    for f in fasteners:
      flbl = html.escape(str(f.get("label", "M3x10")))
      fdia = float(f.get("diameter_mm", 3.0))
      flen = float(f.get("length_mm", 10.0))
      fqty = html.escape(str(f.get("qty", "")))
      head_h = max(2.2, fdia * 0.9)
      head_w = max(4.8, fdia * 1.8)
      f_cards.append(
          '<div class="ag-fastener-item">'
          f'<div class="ag-fastener-title">{flbl}'
          f'{f" <span>({fqty})</span>" if fqty else ""}</div>'
          '<div class="ag-fastener-draw">'
          f'<span class="ag-screw-head" style="width:{head_h:.1f}mm;'
          f'height:{head_w:.1f}mm"></span>'
          f'<span class="ag-screw-shaft" style="width:{flen:.1f}mm;'
          f'height:{fdia:.1f}mm"></span>'
          "</div>"
          f'<div class="ag-fastener-dim">{flen:g} mm shaft</div>'
          "</div>"
      )
    cheatsheet_html = (
        '<section class="ag-cheatsheet" aria-label="1:1 Fastener Scale">'
        '<div class="ag-cheatsheet-head">'
        "<strong>1:1 Fastener Reference</strong>"
        "<span>Print at 100% scale (no fit-to-page) and lay screws directly"
        " over silhouettes.</span>"
        '<div class="ag-scale-wrap">'
        '<div class="ag-scale-ruler"></div>'
        '<div class="ag-scale-labels"><span>0 mm</span><span>50 mm</span></div>'
        "</div>"
        "</div>"
        f'<div class="ag-cheatsheet-grid">{"".join(f_cards)}</div>'
        "</section>"
    )

  steps_html_list: list[str] = []
  for idx, step in enumerate(steps, start=1):
    snum = step.get("number", idx)
    stitle = html.escape(str(step.get("title", "")))
    images = step.get("images", [])
    img_count = len(images)

    rendered_imgs: list[tuple[str, str, set[str]]] = []
    for i_idx, img in enumerate(images):
      svg_markup, cols = _render_visual_svg(
          img, snum, i_idx, base_dir, embed_images, neutralize
      )
      cap = html.escape(
          str(img.get("caption", f"Step {snum} frame {i_idx + 1}"))
      )
      rendered_imgs.append((svg_markup, cap, cols))

    frames_html = "".join(
        f'<figure class="ag-frame{" is-active" if i == 0 else ""}"'
        f' data-frame-idx="{i}"'
        f' data-colors="{" ".join(sorted(cols))}"'
        f' tabindex="0" role="button" aria-label="Zoom {cap}">'
        f"{svg_markup}"
        f'<figcaption class="ag-sr-only">{cap}</figcaption>'
        "</figure>"
        for i, (svg_markup, cap, cols) in enumerate(rendered_imgs)
    )

    thumbs_html = ""
    if img_count > 1:
      thumbs_inner = "".join(
          '<button type="button"'
          f' class="ag-thumb{" is-active" if i == 0 else ""}"'
          f' data-target-idx="{i}" aria-label="Show frame {i + 1}:'
          f' {cap}">{svg_markup}</button>'
          for i, (svg_markup, cap, _) in enumerate(rendered_imgs)
      )
      thumbs_html = f'<div class="ag-thumbs">{thumbs_inner}</div>'

    bullets_html_items: list[str] = []
    for b in step.get("bullets", []):
      btype = str(b.get("type", "action"))
      bcolor = (
          str(b.get("color", "black"))
          if btype in ("action", "subaction")
          else "black"
      )
      indent = int(b.get("indent", 1 if btype == "subaction" else 0))
      btext_html = _format_inline_md(str(b.get("text", "")))
      icon_html = _bullet_icon_svg(btype, bcolor)
      color_attr = (
          f' data-color="{html.escape(bcolor)}"'
          if bcolor in SPATIAL_COLORS
          else ""
      )
      cls = f"ag-bullet ag-btype-{html.escape(btype)}" + (
          " ag-indent" if indent else ""
      )
      bullets_html_items.append(
          f'<li class="{cls}"{color_attr}>{icon_html}'
          f'<div class="ag-bullet-text">{btext_html}</div></li>'
      )

    milestone_raw = str(step.get("milestone", "")).strip()
    milestone_html = (
        f'<div class="ag-milestone">{_format_inline_md(milestone_raw)}</div>'
        if milestone_raw
        else ""
    )

    steps_html_list.append(
        f'<article class="ag-step" id="step-{snum}" data-step="{snum}"'
        f' data-img-count="{img_count}">'
        '<header class="ag-step-header">'
        '<div class="ag-step-heading">'
        f'<span class="ag-step-num">STEP {snum}</span>'
        f'<h2 class="ag-step-title">{stitle}</h2>'
        "</div>"
        f'<label class="ag-step-done" title="Mark Step {snum} complete">'
        f'<input type="checkbox" data-step-check="{snum}"/>'
        "<span>Done</span></label>"
        "</header>"
        '<div class="ag-step-body">'
        f'<div class="ag-media">{frames_html}{thumbs_html}</div>'
        '<div class="ag-instructions">'
        f'<ul class="ag-bullets">{"".join(bullets_html_items)}</ul>'
        f"{milestone_html}"
        "</div></div></article>"
    )

  reassembly_html = ""
  if archetype == "teardown":
    extra = _format_inline_md(str(guide.get("reassembly_note", "")))
    reassembly_html = (
        '<div class="ag-reassembly-banner">'
        "<strong>Reassembly:</strong> To reassemble your device, follow these"
        f" instructions in reverse order. {extra}</div>"
    )

  notes_pages = int(guide.get("include_print_notes_pages", 1))
  notes_html = "".join(
      '<section class="ag-print-notes"><h3>Notes:</h3>'
      + "".join('<div class="ag-note-rule"></div>' for _ in range(18))
      + "</section>"
      for _ in range(max(0, min(notes_pages, 4)))
  )

  storage_key = re.sub(r"[^a-zA-Z0-9_-]+", "_", guide_id or title)[:48]
  pdf_link_html = ""
  pdf_target = pdf_href or str(guide.get("pdf_url", "") or "")
  if pdf_target:
    pdf_link_html = (
        f'<a class="ag-btn ag-btn-primary" href="{html.escape(pdf_target)}"'
        " download>Download PDF</a>"
    )

  url_line = ""
  if canonical_url:
    url_line = (
        '<p class="ag-canonical-link">Interactive version: '
        f'<a href="{canonical_url}">{canonical_url}</a></p>'
    )

  return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>{title}</title>
<style>
:root {{
  --font-sans: "Inter", "Roboto", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  --font-condensed: "Barlow Condensed", "Roboto Condensed", "Arial Narrow", "Liberation Sans Narrow", sans-serif;
  --bg: #fff;
  --surface: #f8fafc;
  --border: #e4e4e7;
  --border-strong: #d4d4d8;
  --text: #18181b;
  --text-muted: #52525b;
  --accent: #fa6831;
  --accent-alt: #0071ce;
  --heading-accent: var(--accent);
  --warn-red: #c62828;
  --radius-outer: 12px;
  --radius-inner: 6px;
}}
*, *::before, *::after {{ box-sizing: border-box; }}
body {{
  margin: 0;
  min-height: 100dvh;
  background: var(--bg);
  color: var(--text);
  font-family: var(--font-sans);
  line-height: 1.5;
  -webkit-font-smoothing: antialiased;
}}
.ag-sr-only {{
  position: absolute;
  width: 1px;
  height: 1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
}}
.ag-topbar {{
  position: sticky;
  top: 0;
  z-index: 30;
  background: rgba(255, 255, 255, 0.94);
  backdrop-filter: blur(8px);
  border-bottom: 1px solid var(--border);
  padding: 10px 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}}
.ag-topbar-meta {{
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 0.85rem;
  color: var(--text-muted);
  font-weight: 500;
}}
.ag-cat-tag {{
  color: var(--accent);
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  font-size: 0.76rem;
}}
body[data-dialect="workbench"] .ag-cat-tag {{ color: var(--accent-alt); }}
.ag-controls {{ display: flex; align-items: center; gap: 10px; }}
.ag-seg-track {{
  display: inline-flex;
  background: #f4f4f5;
  padding: 3px;
  border-radius: 9px;
  border: 1px solid var(--border);
}}
.ag-seg-btn {{
  border: 0;
  background: transparent;
  padding: 5px 12px;
  border-radius: var(--radius-inner);
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--text-muted);
  cursor: pointer;
  transition: transform 140ms cubic-bezier(0.16, 1, 0.3, 1),
              background-color 140ms ease,
              color 140ms ease;
}}
.ag-seg-btn:active {{ transition-duration: 0ms; transform: translateY(1px); }}
.ag-seg-btn.is-active {{
  background: #fff;
  color: var(--text);
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.08);
}}
.ag-btn {{
  border: 1px solid var(--border-strong);
  background: #fff;
  color: var(--text);
  padding: 6px 12px;
  border-radius: 8px;
  font-size: 0.8rem;
  font-weight: 600;
  cursor: pointer;
  transition: transform 140ms cubic-bezier(0.16, 1, 0.3, 1),
              background-color 140ms ease;
}}
.ag-btn:hover {{ background: #f4f4f5; }}
a.ag-btn {{ text-decoration: none; display: inline-flex; align-items: center; }}
.ag-btn-primary {{
  background: var(--heading-accent);
  border-color: var(--heading-accent);
  color: #fff;
}}
.ag-btn-primary:hover {{ background: var(--heading-accent); filter: brightness(0.94); }}
.ag-btn:active {{ transition-duration: 0ms; transform: translateY(1px); }}
.ag-progress-pill {{
  font-size: 0.78rem;
  font-weight: 600;
  color: var(--text-muted);
  font-variant-numeric: tabular-nums;
}}
.ag-container {{
  max-width: 1040px;
  margin: 0 auto;
  padding: 28px 24px 72px;
}}
.ag-hero {{ margin-bottom: 26px; }}
body[data-dialect="workbench"] {{ --heading-accent: var(--accent-alt); }}
.ag-hero h1 {{
  margin: 4px 0 8px;
  color: var(--heading-accent);
  font-size: clamp(1.75rem, 3vw, 2.35rem);
  line-height: 1.15;
  letter-spacing: -0.02em;
}}
body[data-dialect="manual"] .ag-hero h1 {{
  font-family: var(--font-condensed);
  font-stretch: condensed;
  font-size: clamp(2rem, 3.6vw, 2.65rem);
  letter-spacing: -0.01em;
}}
.ag-subtitle {{
  margin: 0 0 14px;
  color: var(--text-muted);
  max-width: 65ch;
  font-size: 0.98rem;
}}
.ag-canonical-link {{
  margin: 0 0 14px;
  font-size: 0.8rem;
  color: var(--text-muted);
  overflow-wrap: anywhere;
}}
.ag-canonical-link a {{ color: inherit; }}
.ag-variants {{
  display: flex;
  gap: 10px;
  align-items: flex-start;
  margin: 0 0 16px;
  padding: 12px 14px;
  border: 1px solid var(--border);
  border-radius: var(--radius-outer);
  background: #fff;
  font-size: 0.88rem;
}}
.ag-variants .ag-icon {{ margin-top: 1px; }}
.ag-variants p {{ margin: 0; }}
.ag-variants ul {{ margin: 0; padding-left: 18px; display: grid; gap: 4px; }}
.ag-logistics {{
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
  margin: 16px 0;
}}
.ag-stat-card {{
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-outer);
  padding: 12px 14px;
}}
.ag-stat-label {{
  font-size: 0.74rem;
  color: var(--heading-accent);
  font-weight: 600;
  margin-bottom: 4px;
}}
.ag-stat-val {{
  font-size: 0.95rem;
  font-weight: 700;
  display: flex;
  align-items: center;
  gap: 8px;
}}
.ag-diff-bars {{ display: inline-flex; gap: 3px; }}
.ag-diff-seg {{
  width: 12px;
  height: 7px;
  border-radius: 2px;
  background: #e4e4e7;
}}
.ag-diff-seg.active {{ background: var(--heading-accent); }}
.ag-inventory {{
  display: grid;
  grid-template-columns: 1fr;
  gap: 14px;
  margin: 16px 0 24px;
}}
.ag-inv-box {{
  border: 1px solid var(--border);
  border-radius: var(--radius-outer);
  padding: 14px 16px 8px;
  background: #fff;
  break-inside: avoid;
  page-break-inside: avoid;
}}
.ag-inv-box h3 {{
  margin: 0 0 8px;
  font-size: 0.86rem;
  font-weight: 700;
  color: var(--heading-accent);
}}
.ag-inv-table {{
  width: 100%;
  border-collapse: collapse;
  table-layout: fixed;
  font-size: 0.86rem;
}}
.ag-inv-col-name {{ width: 42%; }}
.ag-inv-col-meta {{ width: 58%; }}
.ag-inv-table th,
.ag-inv-table td {{
  text-align: left;
  vertical-align: top;
  padding: 6px 12px 6px 0;
  border-top: 1px solid #f4f4f5;
}}
.ag-inv-table tr:first-child th,
.ag-inv-table tr:first-child td {{ border-top: 0; }}
.ag-inv-table th {{ font-weight: 600; color: var(--text); }}
.ag-inv-table td {{ color: var(--text-muted); }}
.ag-toc {{
  display: none;
  margin: 18px 0 28px;
  padding: 14px 18px;
  border: 1px solid var(--border);
  border-radius: var(--radius-outer);
  background: var(--surface);
}}
.ag-toc summary {{ font-weight: 700; font-size: 0.9rem; cursor: pointer; color: var(--heading-accent); }}
.ag-toc ol {{
  margin: 10px 0 0;
  padding-left: 20px;
  columns: 2;
  column-gap: 28px;
  font-size: 0.85rem;
}}
.ag-toc a {{ color: var(--text); text-decoration: none; }}
.ag-toc a:hover {{ text-decoration: underline; color: var(--accent); }}
body[data-dialect="manual"] .ag-toc {{ display: block; }}

.ag-cheatsheet {{
  border: 1px solid var(--border-strong);
  border-radius: var(--radius-outer);
  padding: 14px 16px;
  margin-bottom: 28px;
  background: #fff;
}}
.ag-cheatsheet-head {{
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  margin-bottom: 12px;
  font-size: 0.82rem;
  color: var(--text-muted);
}}
.ag-cheatsheet-head strong {{ color: var(--heading-accent); font-size: 0.9rem; }}
.ag-scale-wrap {{ width: 50mm; }}
.ag-scale-ruler {{
  width: 50mm;
  height: 6px;
  border-bottom: 2px solid #18181b;
  border-left: 2px solid #18181b;
  border-right: 2px solid #18181b;
}}
.ag-scale-labels {{
  display: flex;
  justify-content: space-between;
  font-size: 9.5px;
  line-height: 1.1;
  margin-top: 3px;
  color: #18181b;
  font-weight: 700;
}}
.ag-cheatsheet-grid {{
  display: flex;
  flex-wrap: wrap;
  gap: 18px;
}}
.ag-fastener-item {{
  border: 1px solid var(--border);
  border-radius: var(--radius-inner);
  padding: 8px 12px;
  background: var(--surface);
}}
.ag-fastener-title {{ font-size: 0.8rem; font-weight: 700; margin-bottom: 6px; }}
.ag-fastener-title span {{ color: var(--text-muted); font-weight: 500; }}
.ag-fastener-draw {{ display: flex; align-items: center; min-height: 22px; }}
.ag-screw-head {{
  display: inline-block;
  background: #27272a;
  border-radius: 1.5px 0 0 1.5px;
}}
.ag-screw-shaft {{
  display: inline-block;
  background: repeating-linear-gradient(
    90deg, #52525b 0, #52525b 1px, #a1a1aa 1px, #a1a1aa 2px
  );
}}
.ag-fastener-dim {{ font-size: 0.72rem; color: var(--text-muted); margin-top: 4px; }}

/* Step layout: manual layout */
.ag-step {{
  padding: 18px 0 28px;
  border-top: 2px solid var(--accent);
}}
body[data-dialect="workbench"] .ag-step {{
  border-top: 1px solid var(--border);
  padding: 24px 0 30px;
}}
.ag-step-header {{
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 14px;
}}
.ag-step-heading {{ display: flex; align-items: baseline; gap: 10px; min-width: 0; }}
.ag-step-num {{ flex-shrink: 0; }}
.ag-step-title {{ min-width: 0; }}
.ag-step-num {{
  font-family: var(--font-condensed);
  font-stretch: condensed;
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--accent);
  letter-spacing: 0.02em;
}}
body[data-dialect="workbench"] .ag-step-num {{
  font-family: var(--font-sans);
  font-stretch: normal;
  font-size: 1.15rem;
  color: var(--accent-alt);
}}
.ag-step-title {{
  margin: 0;
  font-family: var(--font-condensed);
  font-stretch: condensed;
  font-size: 1.5rem;
  font-weight: 600;
  color: #52525b;
}}
body[data-dialect="workbench"] .ag-step-title {{
  font-family: var(--font-sans);
  font-stretch: normal;
  font-size: 1.2rem;
  font-weight: 700;
  color: var(--text);
}}
.ag-step-done {{
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 0.78rem;
  font-weight: 600;
  color: var(--text-muted);
  cursor: pointer;
  user-select: none;
}}
.ag-step.is-completed {{ opacity: 0.68; }}

/* Manual layout: adaptive 1 / 2 / 3 visual grids */
body[data-dialect="manual"] .ag-step[data-img-count="1"] .ag-step-body {{
  display: grid;
  grid-template-columns: minmax(260px, 47%) 1fr;
  gap: 24px;
  align-items: start;
}}
body[data-dialect="manual"] .ag-step[data-img-count="2"] .ag-media {{
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
  margin-bottom: 16px;
}}
body[data-dialect="manual"] .ag-step[data-img-count="3"] .ag-media {{
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
  margin-bottom: 16px;
}}
body[data-dialect="manual"] .ag-thumbs {{ display: none; }}

/* Workbench layout: 4:3 stage + thumbnails */
body[data-dialect="workbench"] .ag-step-body {{
  display: grid;
  grid-template-columns: minmax(300px, 55%) 1fr;
  gap: 26px;
  align-items: start;
}}
body[data-dialect="workbench"] .ag-frame {{ display: none; }}
body[data-dialect="workbench"] .ag-frame.is-active {{ display: block; }}
.ag-thumbs {{
  display: flex;
  gap: 8px;
  margin-top: 8px;
}}
.ag-thumb {{
  width: 92px;
  padding: 0;
  border: 2px solid var(--border);
  border-radius: var(--radius-inner);
  background: #fff;
  overflow: hidden;
  cursor: pointer;
  transition: transform 140ms cubic-bezier(0.16, 1, 0.3, 1),
              border-color 140ms ease;
}}
.ag-thumb:active {{ transition-duration: 0ms; transform: scale(0.98); }}
.ag-thumb.is-active {{ border-color: var(--accent-alt); }}
.ag-thumb svg {{ display: block; width: 100%; height: auto; }}

.ag-frame {{
  margin: 0;
  border: 1px solid var(--border-strong);
  background: #fff;
  overflow: hidden;
  cursor: zoom-in;
  box-shadow: inset 0 0 0 1px rgba(0, 0, 0, 0.04);
}}
body[data-dialect="workbench"] .ag-frame {{ border-radius: 8px; }}
.ag-visual-svg {{ display: block; width: 100%; height: auto; }}

/* Bullets & Icons */
.ag-bullets {{
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  gap: 11px;
}}
.ag-bullet {{
  display: flex;
  align-items: flex-start;
  gap: 12px;
  font-size: 0.96rem;
  line-height: 1.48;
  padding: 3px 6px;
  border-radius: 6px;
  transition: background-color 140ms ease;
}}
.ag-bullet[data-color] {{ cursor: pointer; }}
.ag-bullet[data-color]:hover,
.ag-bullet.is-highlighted {{ background: #f4f4f5; }}
.ag-bullet.ag-indent {{ margin-left: 28px; }}
.ag-icon {{
  flex-shrink: 0;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  margin-top: 3px;
}}
body[data-dialect="manual"] .ag-glyph-ring {{ display: none; }}
body[data-dialect="workbench"] .ag-glyph-hex {{ display: none; }}
.ag-btype-warning .ag-bullet-text {{ color: var(--warn-red); font-weight: 500; }}
.ag-btype-pin .ag-bullet-text {{ font-weight: 500; }}
.ag-bullet-text code {{
  font-family: ui-monospace, SFMono-Regular, monospace;
  font-size: 0.86em;
  background: #f4f4f5;
  padding: 1px 5px;
  border-radius: 4px;
}}
.ag-marker {{
  transform-box: fill-box;
  transform-origin: center;
  transition: transform 150ms cubic-bezier(0.16, 1, 0.3, 1),
              opacity 150ms ease;
}}
.ag-step.has-hover .ag-marker:not(.is-highlighted) {{ opacity: 0.28; }}
.ag-marker.is-highlighted {{ transform: scale(1.12); }}

.ag-milestone {{
  margin-top: 14px;
  padding: 10px 14px;
  border-radius: var(--radius-inner);
  background: #fff;
  border: 1px solid var(--border-strong);
  color: var(--text);
  font-size: 0.88rem;
  font-weight: 600;
  break-before: avoid;
  break-inside: avoid;
}}
.ag-reassembly-banner {{
  margin-top: 24px;
  padding: 14px 18px;
  border-radius: var(--radius-outer);
  background: #fff;
  border: 1px solid var(--border-strong);
  color: var(--text);
  font-size: 0.92rem;
}}
.ag-val {{ font-weight: 600; }}
.ag-bullet {{ break-inside: avoid; }}

/* Lightbox */
.ag-lightbox {{
  position: fixed;
  inset: 0;
  z-index: 60;
  background: rgba(9, 9, 11, 0.84);
  display: none;
  align-items: center;
  justify-content: center;
  padding: 24px;
}}
.ag-lightbox.is-open {{ display: flex; }}
.ag-lightbox-inner {{
  background: #fff;
  border-radius: var(--radius-outer);
  max-width: min(1000px, 94vw);
  width: 100%;
  padding: 14px;
  position: relative;
}}
.ag-lightbox-inner svg {{ width: 100%; height: auto; max-height: 78dvh; }}
.ag-lightbox-bar {{
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
  font-size: 0.88rem;
  font-weight: 600;
}}

.ag-print-notes {{ display: none; }}

@media screen and (max-width: 760px) {{
  body[data-dialect="manual"] .ag-step[data-img-count="1"] .ag-step-body,
  body[data-dialect="workbench"] .ag-step-body {{
    grid-template-columns: 1fr;
  }}
  body[data-dialect="manual"] .ag-step[data-img-count="3"] .ag-media {{
    grid-template-columns: 1fr;
  }}
  .ag-toc ol {{ columns: 1; }}
}}

@media print {{
  @page {{ size: {paper} portrait; margin: 14mm; }}
  .ag-topbar, .ag-step-done, .ag-thumbs, .ag-lightbox {{ display: none !important; }}
  body {{ font-size: 10.5pt; }}
  .ag-container {{ max-width: 100%; padding: 0; }}
  .ag-step {{ break-inside: avoid; page-break-inside: avoid; opacity: 1 !important; }}
  body[data-dialect="workbench"] .ag-frame {{ display: block !important; margin-bottom: 6px; }}
  /* Print keeps single visuals full width so callouts stay legible. */
  .ag-step[data-img-count="1"] .ag-step-body {{ display: block !important; }}
  .ag-step[data-img-count="1"] .ag-media {{ margin-bottom: 12px; }}
  .ag-step[data-img-count="1"] .ag-frame {{ max-width: 140mm; margin: 0 auto; }}
  .ag-toc {{ display: block !important; background: #fff; }}
  .ag-print-notes {{
    display: block;
    page-break-before: always;
    padding-top: 8mm;
  }}
  .ag-print-notes h3 {{ margin: 0 0 10mm; font-size: 13pt; }}
  .ag-note-rule {{ border-bottom: 1px solid #a1a1aa; height: 11mm; }}
}}
</style>
</head>
<body data-dialect="{html.escape(default_dialect)}">
<div class="ag-topbar">
  <div class="ag-topbar-meta">
    <span class="ag-cat-tag">{category}</span>
    {f'<span>· {guide_id}</span>' if guide_id else ''}
    <span class="ag-progress-pill" id="ag-progress">0 / {len(steps)} steps</span>
  </div>
  <div class="ag-controls">
    <div class="ag-seg-track" role="group" aria-label="Guide visual dialect">
      <button type="button" class="ag-seg-btn{' is-active' if default_dialect == 'manual' else ''}" data-set-dialect="manual">Manual layout</button>
      <button type="button" class="ag-seg-btn{' is-active' if default_dialect == 'workbench' else ''}" data-set-dialect="workbench">Workbench layout</button>
    </div>
    {pdf_link_html}
    <button type="button" class="ag-btn" id="ag-print-btn">Print</button>
  </div>
</div>

<main class="ag-container">
  <header class="ag-hero">
    <h1>{title}</h1>
    {f'<p class="ag-subtitle">{subtitle}</p>' if subtitle else ''}
    {url_line}
    {variants_html}
    <div class="ag-logistics">
      <div class="ag-stat-card">
        <div class="ag-stat-label">Difficulty</div>
        <div class="ag-stat-val"><span>{html.escape(difficulty)}</span><span class="ag-diff-bars" aria-hidden="true">{bars_html}</span></div>
      </div>
      <div class="ag-stat-card">
        <div class="ag-stat-label">Time Required</div>
        <div class="ag-stat-val">{time_req}</div>
      </div>
      <div class="ag-stat-card">
        <div class="ag-stat-label">Steps</div>
        <div class="ag-stat-val">{len(steps)} steps</div>
      </div>
    </div>
    <details class="ag-toc" open>
      <summary>Table of Contents</summary>
      <ol>{toc_items}</ol>
    </details>
    {inventory_html}
  </header>

  {cheatsheet_html}
  <section aria-label="Step-by-step instructions">
    {''.join(steps_html_list)}
  </section>
  {reassembly_html}
  {notes_html}
</main>

<div class="ag-lightbox" id="ag-lightbox" role="dialog" aria-modal="true" aria-label="Zoomed step visual">
  <div class="ag-lightbox-inner">
    <div class="ag-lightbox-bar">
      <span id="ag-lightbox-cap"></span>
      <button type="button" class="ag-btn" id="ag-lightbox-close">Close (Esc)</button>
    </div>
    <div id="ag-lightbox-stage"></div>
  </div>
</div>

<script>
(() => {{
  const STORAGE_KEY = "ag_done_{storage_key}";
  const body = document.body;

  // Dialect switcher
  document.querySelectorAll("[data-set-dialect]").forEach((btn) => {{
    btn.addEventListener("click", () => {{
      const d = btn.getAttribute("data-set-dialect");
      body.setAttribute("data-dialect", d);
      document.querySelectorAll("[data-set-dialect]").forEach((b) => {{
        b.classList.toggle("is-active", b === btn);
      }});
    }});
  }});

  document.getElementById("ag-print-btn").addEventListener("click", () => window.print());

  // Thumbnail frame switching + color-synced bullet hover
  document.querySelectorAll(".ag-step").forEach((stepEl) => {{
    const frames = Array.from(stepEl.querySelectorAll(".ag-frame"));
    const thumbs = Array.from(stepEl.querySelectorAll(".ag-thumb"));
    const setFrame = (idx) => {{
      frames.forEach((f, i) => f.classList.toggle("is-active", i === idx));
      thumbs.forEach((t, i) => t.classList.toggle("is-active", i === idx));
    }};
    thumbs.forEach((thumb) => {{
      const idx = Number(thumb.getAttribute("data-target-idx"));
      thumb.addEventListener("mouseenter", () => setFrame(idx));
      thumb.addEventListener("click", () => setFrame(idx));
    }});

    stepEl.querySelectorAll(".ag-bullet[data-color]").forEach((bullet) => {{
      const col = bullet.getAttribute("data-color");
      const highlight = (active) => {{
        stepEl.classList.toggle("has-hover", active);
        bullet.classList.toggle("is-highlighted", active);
        stepEl.querySelectorAll(`.ag-marker[data-color="${{col}}"]`).forEach((m) => {{
          m.classList.toggle("is-highlighted", active);
        }});
        if (active && body.getAttribute("data-dialect") === "workbench") {{
          const matchIdx = frames.findIndex((f) =>
            (f.getAttribute("data-colors") || "").split(" ").includes(col)
          );
          if (matchIdx >= 0) setFrame(matchIdx);
        }}
      }};
      bullet.addEventListener("mouseenter", () => highlight(true));
      bullet.addEventListener("mouseleave", () => highlight(false));
      bullet.addEventListener("click", () => {{
        const was = bullet.classList.contains("is-highlighted");
        stepEl.querySelectorAll(".ag-bullet.is-highlighted").forEach((b) => b.classList.remove("is-highlighted"));
        stepEl.querySelectorAll(".ag-marker.is-highlighted").forEach((m) => m.classList.remove("is-highlighted"));
        highlight(!was);
      }});
    }});
  }});

  // Lightbox zoom
  const lb = document.getElementById("ag-lightbox");
  const lbStage = document.getElementById("ag-lightbox-stage");
  const lbCap = document.getElementById("ag-lightbox-cap");
  const closeLb = () => lb.classList.remove("is-open");
  document.querySelectorAll(".ag-frame").forEach((frame) => {{
    const open = () => {{
      const svg = frame.querySelector("svg");
      const cap = frame.querySelector("figcaption");
      if (!svg) return;
      lbStage.innerHTML = svg.outerHTML;
      lbCap.textContent = cap ? cap.textContent : "";
      lb.classList.add("is-open");
    }};
    frame.addEventListener("click", open);
    frame.addEventListener("keydown", (e) => {{
      if (e.key === "Enter" || e.key === " ") {{ e.preventDefault(); open(); }}
    }});
  }});
  document.getElementById("ag-lightbox-close").addEventListener("click", closeLb);
  lb.addEventListener("click", (e) => {{ if (e.target === lb) closeLb(); }});
  document.addEventListener("keydown", (e) => {{ if (e.key === "Escape") closeLb(); }});

  // Persistent step completion checkboxes
  let saved = {{}};
  try {{ saved = JSON.parse(localStorage.getItem(STORAGE_KEY) || "{{}}"); }} catch (err) {{ console.error("State load error:", err); }}
  const checks = Array.from(document.querySelectorAll("[data-step-check]"));
  const progEl = document.getElementById("ag-progress");
  const syncProgress = () => {{
    let done = 0;
    checks.forEach((chk) => {{
      const id = chk.getAttribute("data-step-check");
      const stepArt = chk.closest(".ag-step");
      if (chk.checked) done += 1;
      if (stepArt) stepArt.classList.toggle("is-completed", chk.checked);
      saved[id] = chk.checked;
    }});
    progEl.textContent = `${{done}} / ${{checks.length}} steps`;
    try {{ localStorage.setItem(STORAGE_KEY, JSON.stringify(saved)); }} catch (err) {{ console.error("State save error:", err); }}
  }};
  checks.forEach((chk) => {{
    const id = chk.getAttribute("data-step-check");
    chk.checked = Boolean(saved[id]);
    chk.addEventListener("change", syncProgress);
  }});
  syncProgress();
}})();
</script>
</body>
</html>
"""


_CHROME_CANDIDATES = (
    "google-chrome",
    "google-chrome-stable",
    "chromium",
    "chromium-browser",
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
)

_AUDIT_JS = r"""
window.addEventListener('load', () => {
  const out = [];
  const push = (code, where, msg) => out.push({code, where, msg});
  const stepOf = (el) => { const s = el.closest('.ag-step'); return s ? s.id : 'header'; };
  document.querySelectorAll('svg.ag-visual-svg').forEach((svg) => {
    if (svg.closest('.ag-thumb')) return;
    const where = stepOf(svg);
    const inv = svg.getCTM() ? svg.getCTM().inverse() : null;
    svg.querySelectorAll('text').forEach((t) => {
      if (t.closest('[clip-path]') || !inv) return;
      const b = t.getBBox();
      const m = inv.multiply(t.getCTM());
      const pts = [[b.x, b.y], [b.x + b.width, b.y], [b.x, b.y + b.height], [b.x + b.width, b.y + b.height]]
        .map(([x, y]) => new DOMPoint(x, y).matrixTransform(m));
      const xs = pts.map((p) => p.x), ys = pts.map((p) => p.y);
      if (Math.min(...xs) < 3 || Math.max(...xs) > 397 || Math.min(...ys) < 3 || Math.max(...ys) > 297) {
        push('A-TEXT-OVERFLOW', where, `"${t.textContent.trim().slice(0, 40)}" touches or crosses the frame edge`);
      }
    });
    svg.querySelectorAll('text.ag-lineup-label').forEach((t) => {
      const slot = parseFloat(t.dataset.slotW || '0');
      if (slot && t.getBBox().width > slot - 2) {
        push('A-LABEL-FIT', where, `lineup label "${t.textContent.trim()}" is wider than its slot`);
      }
    });
    const cols = new Set([...svg.querySelectorAll('.ag-marker')].map((m) => m.dataset.color).filter((c) => c && c !== 'black'));
    if (cols.size > 3) push('A-MARKER-COLORS', where, `${cols.size} marker colors on one visual`);
  });
  document.querySelectorAll('body *').forEach((el) => {
    const cs = getComputedStyle(el);
    const bl = parseFloat(cs.borderLeftWidth), bt = parseFloat(cs.borderTopWidth);
    if (cs.borderLeftStyle !== 'none' && bl >= 2 && bl > bt && parseFloat(cs.borderTopLeftRadius) > 0) {
      push('A-ACCENT-STRIPE', stepOf(el), `.${el.className} has a colored left stripe on a rounded box`);
    }
  });
  document.querySelectorAll('.ag-inv-table').forEach((tb) => {
    const xs = new Set([...tb.querySelectorAll('td')].map((td) => Math.round(td.getBoundingClientRect().left)));
    if (xs.size > 1) push('A-COLUMN-ALIGN', 'header', 'inventory spec column is not aligned');
  });
  const pre = document.createElement('pre');
  pre.id = 'ag-audit-result';
  pre.textContent = JSON.stringify(out);
  document.body.appendChild(pre);
});
"""


def _find_chrome() -> str | None:
  env = os.environ.get("CHROME_BIN")
  if env and (shutil.which(env) or pathlib.Path(env).is_file()):
    return env
  for cand in _CHROME_CANDIDATES:
    found = shutil.which(cand) or (
        cand if pathlib.Path(cand).is_file() else None
    )
    if found:
      return found
  return None


def _run_chrome(
    args: list[str], timeout: int = 180
) -> subprocess.CompletedProcess[str]:
  """Runs headless Chrome with a throwaway profile and returns the result."""
  chrome = _find_chrome()
  if not chrome:
    raise RuntimeError(
        "Chrome/Chromium not found. Set CHROME_BIN or install google-chrome."
    )
  with tempfile.TemporaryDirectory(prefix="ag-chrome-") as profile:
    cmd = [
        chrome,
        "--headless=new",
        "--disable-gpu",
        "--no-sandbox",
        "--disable-extensions",
        "--no-proxy-server",
        "--hide-scrollbars",
        f"--user-data-dir={profile}",
        *args,
    ]
    return subprocess.run(
        cmd, capture_output=True, text=True, timeout=timeout, check=False
    )


def render_pdf(html_path: pathlib.Path, pdf_path: pathlib.Path) -> None:
  """Prints the compiled HTML to PDF with print media via headless Chrome."""
  pdf_path.parent.mkdir(parents=True, exist_ok=True)
  if pdf_path.exists():
    pdf_path.unlink()
  result = _run_chrome([
      f"--print-to-pdf={pdf_path.resolve()}",
      "--no-pdf-header-footer",
      "--virtual-time-budget=5000",
      html_path.resolve().as_uri(),
  ])
  if not pdf_path.is_file() or pdf_path.stat().st_size == 0:
    raise RuntimeError(f"PDF render failed:\n{result.stderr[-2000:]}")


def audit_html(html_text: str) -> list[LintFinding]:
  """Renders the HTML in headless Chrome and checks rendered geometry."""
  findings: list[LintFinding] = []
  probe = html_text.replace("</body>", f"<script>{_AUDIT_JS}</script></body>")
  with tempfile.TemporaryDirectory(prefix="ag-audit-") as tmp:
    page = pathlib.Path(tmp) / "audit.html"
    page.write_text(probe, encoding="utf-8")
    result = _run_chrome([
        "--window-size=1280,2000",
        "--virtual-time-budget=6000",
        "--dump-dom",
        page.as_uri(),
    ])
  match = re.search(
      r'<pre id="ag-audit-result">(.*?)</pre>', result.stdout, re.S
  )
  if not match:
    findings.append(
        LintFinding("A-AUDIT", "ERROR", "Rendered audit produced no result.")
    )
    return findings
  for item in json.loads(html.unescape(match.group(1))):
    findings.append(
        LintFinding(item["code"], "WARN", f"{item['where']}: {item['msg']}")
    )
  return findings


def audit_pdf(
    pdf_path: pathlib.Path, guide: dict[str, Any]
) -> list[LintFinding]:
  """Checks print pagination: orphaned milestones and stranded step headers."""
  findings: list[LintFinding] = []
  pdftotext = shutil.which("pdftotext")
  if not pdftotext:
    return findings
  text = subprocess.run(
      [pdftotext, "-layout", str(pdf_path), "-"],
      capture_output=True,
      text=True,
      check=False,
  ).stdout
  milestones = [
      str(s.get("milestone", "")).strip()[:30]
      for s in _localize_guide(guide).get("steps", [])
      if s.get("milestone")
  ]
  for page_no, page in enumerate(text.split("\f"), start=1):
    lines = [ln.strip() for ln in page.splitlines() if ln.strip()]
    if not lines:
      continue
    if any(m and lines[0].startswith(m) for m in milestones):
      findings.append(
          LintFinding(
              "A-ORPHAN-MILESTONE",
              "WARN",
              f"PDF page {page_no}: milestone banner starts the page, separated"
              " from its step.",
          )
      )
    if re.match(r"^STEP \d+\b", lines[-1]):
      findings.append(
          LintFinding(
              "A-STRANDED-HEADER",
              "WARN",
              f"PDF page {page_no}: step header sits at the bottom of the"
              " page.",
          )
      )
  return findings


def render_markdown(guide: dict[str, Any]) -> str:
  """Compiles a validated guide dictionary into GitHub Flavored Markdown."""
  guide = _localize_guide(guide)
  lines: list[str] = [f"# {guide.get('title', 'Assembly Guide')}", ""]
  if guide.get("subtitle"):
    lines.extend([str(guide["subtitle"]), ""])

  if guide.get("variants"):
    for v in guide["variants"]:
      lines.append(
          f"> [!NOTE] **{v.get('label', 'Variant')}:** {v.get('note', '')}"
      )
    lines.append("")

  lines.extend([
      "| Field | Value |",
      "| :--- | :--- |",
      f"| **Difficulty** | {guide.get('difficulty', 'Moderate')} |",
      f"| **Time Required** | {guide.get('time_required', '30 minutes')} |",
      f"| **Procedure Type** | `{guide.get('archetype', 'roundtrip')}` |",
      f"| **Steps** | {len(guide.get('steps', []))} |",
      "",
  ])

  if guide.get("tools"):
    lines.extend(["## Necessary Tools", ""])
    for t in guide["tools"]:
      spec = f" ({t['spec']})" if t.get("spec") else ""
      lines.append(f"*   **{t.get('name', '')}**{spec}")
    lines.append("")

  if guide.get("parts"):
    lines.extend(["## Parts & Consumables", ""])
    for p in guide["parts"]:
      qty = f" — `{p['qty']}`" if p.get("qty") else ""
      lines.append(f"*   **{p.get('name', '')}**{qty}")
    lines.append("")

  for idx, step in enumerate(guide.get("steps", []), start=1):
    snum = step.get("number", idx)
    stitle = step.get("title", "")
    lines.extend([f"## Step {snum}: {stitle}", ""])
    for img in step.get("images", []):
      cap = img.get("caption", f"Step {snum} visual")
      if img.get("src"):
        lines.append(f"![{cap}]({img['src']})")
      else:
        lines.append(f"*Visual: {cap}*")
    if step.get("images"):
      lines.append("")

    for b in step.get("bullets", []):
      btype = b.get("type", "action")
      text = str(b.get("text", "")).replace("->", "→")
      indent_prefix = (
          "    " if b.get("indent", 1 if btype == "subaction" else 0) else ""
      )
      if btype == "warning":
        if lines and lines[-1]:
          lines.append("")
        lines.extend([f"> [!WARNING] {text}", ""])
      elif btype == "info":
        lines.append(f"{indent_prefix}*   ⓘ {text}")
      elif btype == "pin":
        lines.append(f"{indent_prefix}*   📌 {text}")
      else:
        col = str(b.get("color", "black"))
        tag = (
            f"**[{COLOR_PALETTE[col]['label']}]** "
            if col in SPATIAL_COLORS
            else ""
        )
        lines.append(f"{indent_prefix}*   {tag}{text}")
    lines.append("")
    if step.get("milestone"):
      lines.extend([f"> [!TIP] {step['milestone']}", ""])

  if guide.get("archetype") == "teardown":
    extra = (
        f" {guide['reassembly_note']}" if guide.get("reassembly_note") else ""
    )
    lines.extend([
        "---",
        "",
        (
            "**Reassembly:** To reassemble your device, follow these"
            f" instructions in reverse order.{extra}"
        ),
        "",
    ])
  return "\n".join(lines).rstrip() + "\n"


SAMPLE_GUIDE: dict[str, Any] = {
    "title": "How to replace the Cooling Fan (Sensor Enclosure)",
    "subtitle": (
        "Complete disassembly, zip-tie strain relief replacement, and "
        "power-on fan verification."
    ),
    "category": "Hardware maintenance",
    "guide_id": "g-demo-01",
    "archetype": "roundtrip",
    "default_dialect": "manual",
    "difficulty": "Moderate",
    "time_required": "20–30 minutes",
    "variants": [{
        "label": "Dual-blower enclosure revision (Rev C)",
        "note": (
            "Follow the Rev C dual-duct supplement instead of "
            "this single-fan guide."
        ),
    }],
    "tools": [
        {"name": "TX 8 Torx key", "spec": "Torx T8 L-key"},
        {"name": "2.5 mm Allen key", "spec": "Hex 2.5 mm"},
        {"name": "Flush cutters", "spec": "For single-use cable zip tie"},
        {"name": "Cardboard work mat", "spec": "Protects enclosure face"},
    ],
    "parts": [
        {"name": "5V radial blower fan", "qty": "1x"},
        {"name": "Nylon zip tie", "qty": "1x (2.5 x 100 mm)"},
    ],
    "fastener_cheatsheet": [
        {"label": "M3x10b", "diameter_mm": 3.0, "length_mm": 10.0, "qty": "3x"},
        {"label": "M3x14", "diameter_mm": 3.0, "length_mm": 14.0, "qty": "2x"},
        {"label": "M3x40", "diameter_mm": 3.0, "length_mm": 40.0, "qty": "2x"},
    ],
    "include_print_notes_pages": 1,
    "steps": [
        {
            "number": 1,
            "title": "Necessary tools",
            "images": [
                {
                    "caption": "TX 8 Torx and 2.5 mm Allen keys",
                    "tool_lineup": [
                        {"kind": "torx_key", "label": "TX 6", "scale": 0.76},
                        {"kind": "torx_key", "label": "TX 8", "scale": 0.85},
                        {"kind": "torx_key", "label": "TX 10", "scale": 0.93},
                        {"kind": "hex_key", "label": "2.5 mm", "scale": 0.9},
                        {"kind": "hex_key", "label": "3.0 mm", "scale": 1.0},
                    ],
                    "markers": [{
                        "shape": "rect",
                        "color": "black",
                        "x": 31.5,
                        "y": 22,
                        "w": 12,
                        "h": 68,
                    }],
                },
                {
                    "caption": "Protective cardboard box",
                    "tool_lineup": [{"kind": "cardboard_box", "label": ""}],
                    "markers": [],
                },
            ],
            "bullets": [
                {
                    "type": "action",
                    "color": "black",
                    "text": "**Prepare the following tools before starting:**",
                },
                {
                    "type": "action",
                    "color": "black",
                    "text": (
                        "**TX 8** Torx key (boxed; easy to confuse "
                        "with TX 6 and TX 10)"
                    ),
                },
                {
                    "type": "action",
                    "color": "black",
                    "text": "**2.5 mm** Allen key",
                },
                {
                    "type": "action",
                    "color": "black",
                    "text": (
                        "Flat cardboard box to shield the front "
                        "bezel from scratches."
                    ),
                },
            ],
        },
        {
            "number": 2,
            "title": "Shutting down and disconnecting power",
            "images": [
                {
                    "caption": "Select Cooldown on the control menu",
                    "ui_screen": {
                        "device_label": "CONTROLLER",
                        "breadcrumb": "PREHEAT",
                        "rows": [
                            "Return",
                            "PLA 215/60",
                            "PETG 230/85",
                            "ABS 255/100",
                            "Cooldown",
                        ],
                        "active_index": 4,
                        "footer": "Core: 28°C   Ambient",
                    },
                    "markers": [{
                        "shape": "rect",
                        "color": "red",
                        "x": 18,
                        "y": 55,
                        "w": 68,
                        "h": 9,
                    }],
                },
                {
                    "caption": "Switch rear rocker to O and unplug mains cord",
                    "svg": (
                        '<rect x="70" y="60" width="260" height="180" '
                        'rx="12" fill="#27272a" stroke="#18181b" '
                        'stroke-width="2.5"/><rect x="115" y="110" '
                        'width="58" height="76" rx="5" fill="#18181b" '
                        'stroke="#52525b" stroke-width="2"/><rect '
                        'x="125" y="122" width="38" height="24" '
                        'rx="2" fill="#dc2626"/><text x="144" y="139" '
                        'text-anchor="middle" font-size="13" '
                        'font-weight="700" fill="#fff">O</text><rect '
                        'x="210" y="116" width="76" height="64" '
                        'rx="6" fill="#18181b" stroke="#52525b" '
                        'stroke-width="2"/><rect x="228" y="134" '
                        'width="40" height="28" rx="4" '
                        'fill="#3f3f46"/>'
                    ),
                    "markers": [
                        {
                            "shape": "circle",
                            "color": "blue",
                            "x": 36,
                            "y": 45,
                            "r": 7,
                        },
                        {
                            "shape": "arrow",
                            "color": "green",
                            "x1": 62,
                            "y1": 50,
                            "x2": 82,
                            "y2": 50,
                        },
                    ],
                },
                {
                    "caption": "Place cardboard shield under carriage",
                    "tool_lineup": [{
                        "kind": "cardboard_box",
                        "label": "Work surface shield",
                    }],
                    "markers": [{
                        "shape": "arrow",
                        "color": "orange",
                        "x1": 74,
                        "y1": 30,
                        "x2": 56,
                        "y2": 45,
                    }],
                },
            ],
            "bullets": [
                {
                    "type": "warning",
                    "text": (
                        "**Thermal hazard:** Confirm all internal "
                        "heaters read below **35°C** before "
                        "touching the shroud."
                    ),
                },
                {
                    "type": "action",
                    "color": "red",
                    "text": (
                        "Navigate to *Preheat -> Cooldown* and wait "
                        "until components reach ambient "
                        "temperature."
                    ),
                },
                {
                    "type": "action",
                    "color": "blue",
                    "text": "Flip the rear power switch **OFF** (symbol `O`).",
                },
                {
                    "type": "action",
                    "color": "green",
                    "text": (
                        "Unplug the AC power cord from the rear receptacle."
                    ),
                },
                {
                    "type": "action",
                    "color": "orange",
                    "text": (
                        "Place the cardboard shield flat across the lower deck."
                    ),
                },
            ],
        },
        {
            "number": 3,
            "title": "Disconnecting and removing the fan",
            "images": [{
                "caption": "Unlatch fan header and release mounting screws",
                "svg": (
                    '<rect x="65" y="45" width="270" height="210" '
                    'rx="10" fill="#27272a" stroke="#18181b" '
                    'stroke-width="2.5"/><rect x="95" y="75" '
                    'width="110" height="150" rx="6" '
                    'fill="#15803d" stroke="#14532d" '
                    'stroke-width="2"/><rect x="132" y="168" '
                    'width="34" height="24" rx="2" fill="#f4f4f5" '
                    'stroke="#a1a1aa"/><rect x="222" y="80" '
                    'width="90" height="90" rx="6" fill="#3f3f46" '
                    'stroke="#18181b" stroke-width="2"/><circle '
                    'cx="267" cy="125" r="28" '
                    'fill="#18181b"/><circle cx="234" cy="92" '
                    'r="5" fill="#d4d4d8"/><circle cx="300" '
                    'cy="158" r="5" fill="#d4d4d8"/><circle '
                    'cx="234" cy="205" r="5" '
                    'fill="#d4d4d8"/><circle cx="267" cy="205" '
                    'r="5" fill="#d4d4d8"/><circle cx="300" '
                    'cy="205" r="5" fill="#d4d4d8"/>'
                ),
                "markers": [
                    {
                        "shape": "rect",
                        "color": "red",
                        "x": 31.5,
                        "y": 54,
                        "w": 11.5,
                        "h": 11,
                    },
                    {
                        "shape": "circle",
                        "color": "blue",
                        "x": 58.5,
                        "y": 30.7,
                        "r": 3.8,
                    },
                    {
                        "shape": "circle",
                        "color": "blue",
                        "x": 75.0,
                        "y": 52.7,
                        "r": 3.8,
                    },
                    {
                        "shape": "circle",
                        "color": "green",
                        "x": 58.5,
                        "y": 68.3,
                        "r": 3.8,
                    },
                    {
                        "shape": "circle",
                        "color": "green",
                        "x": 66.8,
                        "y": 68.3,
                        "r": 3.8,
                    },
                    {
                        "shape": "circle",
                        "color": "green",
                        "x": 75.0,
                        "y": 68.3,
                        "r": 3.8,
                    },
                    {
                        "shape": "loupe",
                        "color": "red",
                        "target_x": 37,
                        "target_y": 60,
                        "x": 18,
                        "y": 24,
                        "r": 14,
                        "zoom": 2.3,
                    },
                ],
            }],
            "bullets": [
                {
                    "type": "warning",
                    "text": (
                        "The board header uses a friction latch. "
                        "**Depress the side tab before pulling the "
                        "plug** so the socket stays soldered to the "
                        "PCB."
                    ),
                },
                {
                    "type": "action",
                    "color": "red",
                    "text": (
                        "Press the white connector tab and unplug "
                        "the 3-pin fan cable."
                    ),
                },
                {
                    "type": "action",
                    "color": "blue",
                    "fastener_count": 2,
                    "text": (
                        "Release the **two M3x40** screws securing "
                        "the fan housing."
                    ),
                },
                {
                    "type": "action",
                    "color": "green",
                    "fastener_count": 3,
                    "text": (
                        "Release the **three M3x10b** screws along "
                        "the lower retainer plate and lift the fan "
                        "free."
                    ),
                },
            ],
        },
        {
            "number": 4,
            "title": "New fan: parts preparation",
            "images": [
                {
                    "caption": "Replacement 5V blower fan",
                    "tool_lineup": [{"kind": "fan", "label": "5V Blower (1x)"}],
                    "markers": [],
                },
                {
                    "caption": "Replacement nylon zip tie",
                    "tool_lineup": [
                        {"kind": "zip_tie", "label": "Zip tie (1x)"}
                    ],
                    "markers": [],
                },
            ],
            "bullets": [
                {
                    "type": "action",
                    "color": "black",
                    "text": (
                        "**Stage the replacement parts on a clean "
                        "corner of the mat:**"
                    ),
                },
                {
                    "type": "action",
                    "color": "black",
                    "text": "New 5V radial blower fan (`1x`)",
                },
                {
                    "type": "action",
                    "color": "black",
                    "text": "Nylon zip tie (`1x`, `2.5 x 100 mm`)",
                },
            ],
        },
        {
            "number": 5,
            "title": "Installing the fan and routing cables",
            "images": [{
                "caption": "Mount retainer and torque screws",
                "svg": (
                    '<rect x="65" y="45" width="270" height="210" '
                    'rx="10" fill="#27272a" stroke="#18181b" '
                    'stroke-width="2.5"/><rect x="222" y="80" '
                    'width="90" height="90" rx="6" fill="#3f3f46" '
                    'stroke="#18181b" stroke-width="2"/><circle '
                    'cx="267" cy="125" r="28" '
                    'fill="#18181b"/><circle cx="234" cy="92" '
                    'r="5" fill="#d4d4d8"/><circle cx="300" '
                    'cy="158" r="5" fill="#d4d4d8"/><circle '
                    'cx="234" cy="205" r="5" '
                    'fill="#d4d4d8"/><circle cx="267" cy="205" '
                    'r="5" fill="#d4d4d8"/><circle cx="300" '
                    'cy="205" r="5" fill="#d4d4d8"/><path d="M '
                    '222 100 C 175 100, 165 140, 148 168" '
                    'fill="none" stroke="#eab308" '
                    'stroke-width="3"/><rect x="172" y="122" '
                    'width="10" height="14" rx="2" '
                    'fill="#18181b"/>'
                ),
                "markers": [
                    {
                        "shape": "circle",
                        "color": "red",
                        "x": 58.5,
                        "y": 68.3,
                        "r": 3.8,
                    },
                    {
                        "shape": "circle",
                        "color": "red",
                        "x": 66.8,
                        "y": 68.3,
                        "r": 3.8,
                    },
                    {
                        "shape": "circle",
                        "color": "red",
                        "x": 75.0,
                        "y": 68.3,
                        "r": 3.8,
                    },
                    {
                        "shape": "circle",
                        "color": "blue",
                        "x": 58.5,
                        "y": 30.7,
                        "r": 3.8,
                    },
                    {
                        "shape": "circle",
                        "color": "blue",
                        "x": 75.0,
                        "y": 52.7,
                        "r": 3.8,
                    },
                    {
                        "shape": "arc",
                        "color": "blue",
                        "x": 75.0,
                        "y": 52.7,
                        "r": 8.0,
                        "start_deg": -60,
                        "end_deg": 120,
                        "direction": "cw",
                    },
                    {
                        "shape": "arrow",
                        "color": "green",
                        "x1": 44,
                        "y1": 34,
                        "x2": 44,
                        "y2": 43,
                    },
                ],
            }],
            "bullets": [
                {
                    "type": "action",
                    "color": "red",
                    "fastener_count": 3,
                    "text": (
                        "Align the lower retainer plate and thread "
                        "in the **three M3x10b** screws."
                    ),
                },
                {
                    "type": "action",
                    "color": "blue",
                    "fastener_count": 2,
                    "text": (
                        "Seat the fan housing with the **two "
                        "M3x40** screws and tighten them clockwise "
                        "until snug against the polymer boss."
                    ),
                },
                {
                    "type": "info",
                    "indent": 1,
                    "text": (
                        "Target torque is **0.8 Nm (7.1 lb-in)**; "
                        "stop as soon as the screw head seats flush "
                        "so the printed threads do not strip."
                    ),
                },
                {
                    "type": "warning",
                    "text": (
                        "**Do not overtighten the zip tie!** "
                        "Crushing the insulation can sever the "
                        "tachometer wire."
                    ),
                },
                {
                    "type": "action",
                    "color": "green",
                    "text": (
                        "Plug in the 3-pin connector, dress the "
                        "signal wires along the channel (excluding "
                        "heater leads), and snug the new zip "
                        "tie."
                    ),
                },
            ],
        },
        {
            "number": 6,
            "title": "Verifying fan airflow and tachometer",
            "images": [{
                "caption": "Run Diagnostic Fan Self-Test",
                "ui_screen": {
                    "device_label": "CONTROLLER",
                    "breadcrumb": "CALIBRATIONS & TESTS",
                    "rows": [
                        "Return",
                        "1. Fan test [PASS 4200 RPM]",
                        "2. Thermal check",
                        "3. Axis home",
                    ],
                    "active_index": 1,
                    "footer": "Fan tach: 4200 RPM",
                },
                "markers": [{
                    "shape": "rect",
                    "color": "red",
                    "x": 18,
                    "y": 30,
                    "w": 68,
                    "h": 9,
                }],
            }],
            "bullets": [
                {
                    "type": "pin",
                    "text": (
                        "Remove the cardboard shield from the lower "
                        "deck before restoring AC power."
                    ),
                },
                {
                    "type": "action",
                    "color": "red",
                    "text": (
                        "Reconnect power and run *Calibrations & "
                        "Tests -> 1. Fan test*, confirming steady "
                        "airflow and a tachometer reading above "
                        "`3800 RPM`."
                    ),
                },
            ],
            "milestone": (
                "That's it, good job! The replacement cooling fan "
                "is installed and verified."
            ),
        },
    ],
}


def recolor_guide(guide: dict[str, Any]) -> dict[str, Any]:
  """Remaps each step's spatial colors to contrast-first order.

  Colors are reassigned by first appearance in the bullet list, and matching
  markers are updated so bullet-to-marker pairing is preserved.

  Args:
    guide: Guide dictionary to recolor.

  Returns:
    A recolored deep copy of the guide.
  """
  out = json.loads(json.dumps(guide))
  for step in out.get("steps", []):
    order: list[str] = []
    for b in step.get("bullets", []):
      col = b.get("color")
      if (
          b.get("type", "action") in ("action", "subaction")
          and col in SPATIAL_COLORS
      ):
        if col not in order:
          order.append(col)
    for img in step.get("images", []):
      for m in img.get("markers", []):
        col = m.get("color")
        if col in SPATIAL_COLORS and col not in order:
          order.append(col)
    mapping = dict(zip(order, COLOR_SEQUENCE))
    for b in step.get("bullets", []):
      if b.get("color") in mapping:
        b["color"] = mapping[b["color"]]
    for img in step.get("images", []):
      for m in img.get("markers", []):
        if m.get("color") in mapping:
          m["color"] = mapping[m["color"]]
  return out


def main(argv: list[str] | None = None) -> int:
  parser = argparse.ArgumentParser(
      description="Lint and compile step-by-step assembly guides."
  )
  sub = parser.add_subparsers(dest="cmd", required=True)

  p_lint = sub.add_parser(
      "lint", help="Validate guide.json against quality gates"
  )
  p_lint.add_argument("input", type=pathlib.Path, help="Path to guide.json")
  p_lint.add_argument(
      "--strict", action="store_true", help="Treat warnings as errors"
  )
  p_lint.add_argument("--allow-text-only", action="store_true")

  p_build = sub.add_parser(
      "build",
      help="Compile guide.json to interactive HTML, print PDF, and Markdown",
  )
  p_build.add_argument("input", type=pathlib.Path, help="Path to guide.json")
  p_build.add_argument(
      "--html", type=pathlib.Path, help="Output interactive HTML path"
  )
  p_build.add_argument(
      "--pdf",
      type=pathlib.Path,
      help="Output print PDF path (rendered from the HTML via headless Chrome)",
  )
  p_build.add_argument(
      "--markdown", type=pathlib.Path, help="Output GFM Markdown path"
  )
  p_build.add_argument(
      "--pdf-dialect",
      choices=sorted(VALID_DIALECTS),
      default=None,
      help="Layout dialect used for the PDF (default: guide default_dialect)",
  )
  p_build.add_argument(
      "--paper", choices=("a4", "letter"), default="a4", help="PDF paper size"
  )
  p_build.add_argument(
      "--embed-images",
      action=argparse.BooleanOptionalAction,
      default=True,
      help="Base64-embed local images so the HTML is portable (default on)",
  )
  p_build.add_argument(
      "--audit",
      action="store_true",
      help="Run rendered-geometry and pagination audits after building",
  )
  p_build.add_argument(
      "--strict", action="store_true", help="Fail build on warnings"
  )
  p_build.add_argument("--allow-text-only", action="store_true")

  p_audit = sub.add_parser(
      "audit",
      help=(
          "Render the guide and check text overflow, label fit, marker colors,"
          " callout stripes, column alignment, and PDF pagination"
      ),
  )
  p_audit.add_argument("input", type=pathlib.Path, help="Path to guide.json")
  p_audit.add_argument(
      "--pdf", type=pathlib.Path, help="Existing PDF to check pagination"
  )
  p_audit.add_argument(
      "--strict", action="store_true", help="Treat warnings as errors"
  )
  p_audit.add_argument("--allow-text-only", action="store_true")

  p_recolor = sub.add_parser(
      "recolor",
      help="Rewrite guide.json so each step uses contrast-first colors",
  )
  p_recolor.add_argument("input", type=pathlib.Path, help="Path to guide.json")
  p_recolor.add_argument(
      "--output", type=pathlib.Path, help="Write here instead of in place"
  )

  p_sample = sub.add_parser(
      "init-sample", help="Write a complete sample guide.json"
  )
  p_sample.add_argument(
      "output", type=pathlib.Path, help="Destination guide.json path"
  )

  args = parser.parse_args(argv)

  if args.cmd == "init-sample":
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(SAMPLE_GUIDE, indent=2) + "\n", encoding="utf-8"
    )
    print(f"Wrote sample guide spec to {args.output}")
    return 0

  if args.cmd == "recolor":
    src = json.loads(args.input.read_text(encoding="utf-8"))
    dest = args.output or args.input
    dest.write_text(
        json.dumps(recolor_guide(src), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"Recolored guide written to {dest}")
    return 0

  data = json.loads(args.input.read_text(encoding="utf-8"))
  findings = lint_guide(data, allow_text_only=args.allow_text_only)
  for f in findings:
    print(f.format(), file=sys.stderr if f.severity == "ERROR" else sys.stdout)

  errors = [f for f in findings if f.severity == "ERROR"]
  warns = [f for f in findings if f.severity == "WARN"]
  if errors or (args.strict and warns):
    print(
        f"Lint failed: {len(errors)} error(s), {len(warns)} warning(s).",
        file=sys.stderr,
    )
    return 1

  if args.cmd == "lint":
    print(
        f"Lint passed ({len(data.get('steps', []))} steps, {len(warns)}"
        " warning(s))."
    )
    return 0

  base_dir = args.input.resolve().parent

  def _report(audit_findings: list[LintFinding]) -> int:
    for f in audit_findings:
      print(f.format())
    a_err = [f for f in audit_findings if f.severity == "ERROR"]
    a_warn = [f for f in audit_findings if f.severity == "WARN"]
    if a_err or (args.strict and a_warn):
      print(
          f"Audit failed: {len(a_err)} error(s), {len(a_warn)} warning(s).",
          file=sys.stderr,
      )
      return 1
    print(f"Audit passed ({len(a_warn)} warning(s)).")
    return 0

  if args.cmd == "audit":
    html_text = render_html(data, base_dir=base_dir, embed_images=True)
    audit_findings = audit_html(html_text)
    if args.pdf:
      audit_findings += audit_pdf(args.pdf, data)
    return _report(audit_findings)

  if not (args.html or args.pdf or args.markdown):
    print(
        "Specify at least one of --html, --pdf, or --markdown.", file=sys.stderr
    )
    return 2

  pdf_href = None
  if args.pdf:
    html_dir = (args.html or args.pdf).resolve().parent
    pdf_href = os.path.relpath(args.pdf.resolve(), html_dir)
  html_out = render_html(
      data,
      base_dir=base_dir,
      embed_images=args.embed_images,
      pdf_href=pdf_href,
  )
  if args.html:
    args.html.parent.mkdir(parents=True, exist_ok=True)
    args.html.write_text(html_out, encoding="utf-8")
    print(f"Built interactive HTML guide: {args.html}")

  if args.pdf:
    print_html = render_html(
        data,
        base_dir=base_dir,
        embed_images=True,
        dialect_override=args.pdf_dialect,
        paper=args.paper,
    )
    with tempfile.TemporaryDirectory(prefix="ag-print-") as tmp:
      tmp_html = pathlib.Path(tmp) / "print.html"
      tmp_html.write_text(print_html, encoding="utf-8")
      render_pdf(tmp_html, args.pdf)
    print(f"Built print PDF guide: {args.pdf}")

  if args.markdown:
    args.markdown.parent.mkdir(parents=True, exist_ok=True)
    md_out = render_markdown(data)
    args.markdown.write_text(md_out, encoding="utf-8")
    print(f"Built Markdown guide: {args.markdown}")

  if args.audit:
    audit_findings = audit_html(html_out)
    if args.pdf:
      audit_findings += audit_pdf(args.pdf, data)
    return _report(audit_findings)

  return 0


if __name__ == "__main__":
  sys.exit(main())
