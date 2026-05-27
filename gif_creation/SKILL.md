---
name: gif-creation
description: >
  Create optimized GIFs from videos, image sequences, or WebGL shader captures
  using 2-pass palette generation. Use when users ask to create GIF, video to GIF,
  optimize GIF, animated GIF, GIF from images, shader to GIF, or reduce GIF file size.
  Supports quality presets, custom timing, transparency, and headless WebGL capture.
---

<!-- Based on https://mcpmarket.com/tools/skills/gif-creation-optimization,
     extended with Playwright + WebGL shader capture pipeline from dithering-gif. -->

# GIF Creation

Create high-quality, optimized GIFs from videos, image sequences, or WebGL shader
renders using FFmpeg's 2-pass palette generation, ImageMagick, or Playwright-based
headless capture pipelines.

---

## Quick Start

### From video

```bash
ffmpeg -i video.mp4 \
  -vf "fps=15,scale=480:-1:flags=lanczos,split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse" \
  -loop 0 output.gif
```

### From image sequence

```bash
magick -delay 7 -loop 0 -dispose Background frames/frame_*.png output.gif
```

### From WebGL shader (interactive)

```bash
cd <project-dir>
pnpm dev
# → http://localhost:3000  — tweak params, click ⬇ Save GIF
```

---

## Source Detection

Automatically detect the source type and choose the appropriate pipeline:

| Input | Detection | Method |
|---|---|---|
| Video file (`video.mp4`) | Video source | FFmpeg 2-pass with palette |
| Image folder (`./frames/`) | Image sequence | FFmpeg or ImageMagick |
| Glob pattern (`frame_*.png`) | Image sequence | FFmpeg or ImageMagick |
| WebGL shader (`shader.html`) | Shader source | Playwright capture → ImageMagick |

---

## Pipeline 1: Video → GIF (FFmpeg 2-Pass)

The gold standard for video-to-GIF conversion. Two passes produce better colour
fidelity and smaller files than single-pass approaches.

### Pass 1 — Generate palette

```bash
ffmpeg -ss <start> -t <duration> -i video.mp4 \
  -vf "fps=<FPS>,scale=<WIDTH>:-1:flags=lanczos,palettegen=stats_mode=diff" \
  -y /tmp/palette.png
```

### Pass 2 — Encode GIF

```bash
ffmpeg -ss <start> -t <duration> -i video.mp4 -i /tmp/palette.png \
  -lavfi "fps=<FPS>,scale=<WIDTH>:-1:flags=lanczos[x];[x][1:v]paletteuse=dither=bayer:bayer_scale=5" \
  -loop 0 \
  output.gif
```

### Optimization Presets

| Preset | `stats_mode` | Dither | Colours | Best For |
|---|---|---|---|---|
| `quality` | `full` | `floyd_steinberg` | 256 | Photographs, gradients |
| `balanced` | `diff` | `bayer:5` | 256 | General use (default) |
| `size` | `single` | `none` | 128 | Smallest files, simple graphics |

---

## Pipeline 2: Image Sequence → GIF

### With ImageMagick (recommended for transparency)

```bash
magick -delay <DELAY> -loop 0 -dispose Background "frames/frame_*.png" output.gif
```

> **Delay calculation:** `delay = 100 / FPS` (centiseconds). E.g. 15 FPS → delay 7.

ImageMagick's `-dispose Background` is essential for transparent GIFs — it clears
each frame before drawing the next, preventing ghosting artefacts.

### With FFmpeg

```bash
ffmpeg -framerate <FPS> -pattern_type glob -i "frames/*.png" \
  -vf "scale=<WIDTH>:-1:flags=lanczos,split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse" \
  -loop 0 \
  output.gif
```

---

## Pipeline 3: WebGL Shader → GIF (Playwright + ImageMagick)

For generating GIFs from programmatic WebGL/shader sources — no screen recording
needed. This pipeline was developed in the `dithering-gif` project.

### Architecture

```
shader.html  →  Playwright (headless)  →  PNG frames  →  ImageMagick  →  GIF
                     │                         │
                     └─ page.evaluate()        └─ temp dir (cleaned up)
                        drives u_time
                        deterministically
```

### Key Concepts

1. **Deterministic capture**: Drive the shader's `u_time` uniform manually
   (one value per frame) rather than recording real-time playback. This gives
   pixel-perfect, timing-independent frames and guarantees seamless loops.

2. **`gl.readPixels` for reliable export**: WebGL clears its drawing buffer
   after each frame swap. Use `gl.readPixels` + an offscreen 2D canvas to
   bypass this and get reliable PNG data.

3. **Row-flip**: WebGL is bottom-left origin; PNG/2D canvas is top-left. Flip
   rows during the readback copy.

4. **Dynamic sizing**: The shader's `canvas.width`/`canvas.height` and the
   `gl.viewport` must be updated together when changing output resolution.
   The `readPixels` buffer must be reallocated to match.

### Shader Page Contract

The shader HTML page must expose these globals for headless capture:

```js
window.__ready      = true;                      // signals page is loaded
window.__setParams  = (params) => { /* ... */ };  // apply uniform overrides
window.__render     = (uTime) => { /* ... */ };   // render one frame at time t
window.__getDataUrl = () => canvas.toDataURL();   // return PNG as data URL
```

### Capture Script Pattern (Node.js)

```js
import { chromium } from 'playwright';

const LOOP_PERIOD = 8 * Math.PI;  // exact loop period for the animation
const FRAME_COUNT = 90;
const step        = LOOP_PERIOD / FRAME_COUNT;

const browser = await chromium.launch({ args: ['--enable-webgl', '--use-gl=egl'] });
const page    = await (await browser.newContext({
  viewport: { width: 480, height: 480 },
})).newPage();

await page.goto('http://localhost:3000/shader.html');
await page.waitForFunction(() => window.__ready === true);

// Push params before capture
await page.evaluate((p) => window.__setParams(p), params);

for (let i = 0; i < FRAME_COUNT; i++) {
  await page.evaluate((t) => window.__render(t), i * step);
  const b64 = await page.evaluate(() => window.__getDataUrl().split(',')[1]);
  writeFileSync(`frame_${String(i).padStart(4, '0')}.png`, Buffer.from(b64, 'base64'));
}

await browser.close();
```

### Encode with ImageMagick

```bash
magick -delay <DELAY> -loop 0 -dispose Background "frames/frame_*.png" output.gif
```

### Seamless Loop Calculation

To find the exact loop period for sinusoidal animations:

1. Identify all time-dependent terms: e.g. `cos(a × t)` and `sin(b × t)`.
2. Each term's period in `t` is `2π / coefficient`.
3. The animation's period is the LCM of all individual periods.
4. Drive `u_time` from `0` to that LCM over exactly `FRAME_COUNT` frames.

**Example:** `cos(0.75t)` has period `8π/3`; `sin(0.625t)` has period `16π/5`.
LCM = `8π`. So 90 frames over `8π` gives a mathematically exact loop.

---

## Transparency

### In GIFs (general)

GIF supports only 1-bit transparency (fully transparent or fully opaque per pixel).
Use `alpha_threshold=128` in FFmpeg or ImageMagick's palette handling.

### With ImageMagick (recommended)

```bash
magick -delay 7 -loop 0 -dispose Background frames/frame_*.png output.gif
```

`-dispose Background` is critical — without it, transparent pixels accumulate
ghost frames from previous iterations.

### With FFmpeg

```bash
ffmpeg -framerate 15 -pattern_type glob -i "frames/*.png" \
  -vf "split[s0][s1];[s0]palettegen=reserve_transparent=1[p];[s1][p]paletteuse=alpha_threshold=128" \
  -gifflags +transdiff \
  -loop 0 output.gif
```

---

## Configuration Defaults

| Option | Default | Range / Options | Description |
|---|---|---|---|
| Width | 480 | 240, 320, 480, 640, 720, 800, 1024 | Output width in pixels |
| FPS | 15 | 10, 12, 15, 20, 24, 30 | Frames per second |
| Duration | full | full, or seconds | Video duration to convert |
| Start | 0 | seconds or `HH:MM:SS` | Start time offset |
| Loop | infinite | infinite, once, `<N>` | Loop count (`-loop 0` = infinite) |
| Optimize | balanced | quality, balanced, size | Preset (see table above) |

---

## Size Estimation

Approximate file sizes at the `balanced` preset:

| Width | 5 s @ 15 fps | 10 s @ 15 fps | 5 s @ 24 fps | 10 s @ 24 fps |
|---|---|---|---|---|
| 800 px | 8–15 MB | 15–30 MB | 12–24 MB | 24–48 MB |
| 640 px | 5–10 MB | 10–20 MB | 8–16 MB | 16–32 MB |
| 480 px | 3–6 MB | 6–12 MB | 5–10 MB | 10–20 MB |
| 320 px | 1–3 MB | 2–6 MB | 2–5 MB | 4–10 MB |
| 240 px | 0.5–2 MB | 1–4 MB | 1–3 MB | 2–6 MB |

**Factors affecting size:** width, FPS, duration, scene complexity, and
optimisation preset (`quality` > `balanced` > `size`).

---

## Platform Limits

| Platform | Max Size | Recommended Settings |
|---|---|---|
| Twitter / X | 5 MB | 480 px, 15 fps, 5–10 s |
| Discord | 8 MB | 640 px, 15 fps, 5–10 s |
| Slack | 5 MB | 480 px, 12 fps, 5–10 s |
| GitHub | 10 MB | 640 px, 15 fps, 10–15 s |
| Email | 1–2 MB | 320 px, 12 fps, 3–5 s |

---

## Post-Processing (Optional)

### gifsicle — further compression

```bash
gifsicle -O3 --lossy=80 output.gif -o output_optimized.gif
```

| Flag | Effect |
|---|---|
| `--lossy=30` | Minimal quality loss |
| `--lossy=80` | Good balance (recommended) |
| `--lossy=200` | Maximum compression |

---

## Best Practices

### Reducing file size

- Lower FPS (12–15 is sufficient for most content).
- Smaller width (480 px or less).
- Use the `size` optimisation preset.
- Trim to the shortest necessary duration.
- Apply `gifsicle -O3 --lossy=80` as a post-processing step.

### Better quality

- Higher FPS (24–30 for smooth motion).
- Larger width (640–800 px).
- Use the `quality` optimisation preset.
- Use `floyd_steinberg` dithering for photographic content.

### Smooth motion

- 24+ FPS for fast action or camera movement.
- 12–15 FPS for simple content, UI demos, or talking heads.

### Transparent GIFs

- Always use `-dispose Background` with ImageMagick.
- Prefer ImageMagick over FFmpeg for transparent output — more reliable disposal.
- Test the output in multiple viewers; some render GIF transparency inconsistently.

### Shader / WebGL GIFs

- Use deterministic `u_time` stepping — never record real-time playback.
- Calculate the exact loop period mathematically from the animation's frequency components.
- Use `gl.readPixels` + offscreen canvas — never rely on `canvas.toDataURL` directly
  (WebGL clears the drawing buffer between frames).
- Expose a `__setParams` API so the capture script can override uniforms without
  editing the shader source.

---

## Requirements

| Tool | Required | Purpose |
|---|---|---|
| FFmpeg | Yes (video sources) | Video decoding + 2-pass palette GIF encoding |
| ImageMagick 7+ | Yes (image sequences) | Frame assembly + transparent GIF encoding |
| Playwright | Yes (shader sources) | Headless Chromium for WebGL frame capture |
| gifsicle | Optional | Additional lossy compression |

### Install (macOS)

```bash
brew install ffmpeg imagemagick gifsicle
```

### Verify

```bash
ffmpeg -version | head -n 1
magick -version | head -n 1
gifsicle --version | head -n 1
```
