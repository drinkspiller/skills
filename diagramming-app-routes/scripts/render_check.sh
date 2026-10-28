#!/usr/bin/env bash
# Renders a route-flow HTML page to a full-page PNG with headless Chrome so the
# layout can be inspected visually (text overflow, overlapping labels).
#
# Usage: render_check.sh <page.html> <out.png> [width] [height]
# Defaults: width=1280, height=2900 (tall enough for flowchart + table + pipeline).
set -euo pipefail

if [[ $# -lt 2 ]]; then
  echo "usage: $0 <page.html> <out.png> [width] [height]" >&2
  exit 2
fi

page="$(readlink -f "$1")"
out="$2"
width="${3:-1280}"
height="${4:-2900}"

chrome=""
for c in google-chrome google-chrome-stable chromium chromium-browser \
  "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"; do
  if command -v "$c" >/dev/null 2>&1 || [[ -x "$c" ]]; then
    chrome="$c"
    break
  fi
done
if [[ -z "$chrome" ]]; then
  echo "error: no Chrome/Chromium binary found" >&2
  exit 1
fi

# Headless Chrome can't read some network/FUSE mounts reliably; render a local copy.
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT
cp "$page" "$tmp/page.html"

timeout 60 "$chrome" --headless=new --disable-gpu --hide-scrollbars \
  --window-size="${width},${height}" --screenshot="$out" \
  "file://$tmp/page.html" >/dev/null 2>&1

echo "wrote $out (${width}x${height})"
