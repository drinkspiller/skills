# Sandbox Explainer HTML Boilerplate

Use this exact HTML/CSS/JS shell to guarantee perfect Craft UI physics, Material 3 tokens, `>= 7:1` WCAG AAA contrast, concentric border radii, and keyboard-navigable step state management. 

Modify the `steps` array and the `.workspace` HTML/JS to fit the specific topic.

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Interactive Explainer</title>
<!-- Inter, JetBrains Mono, Material Symbols -->
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200" />
<style>
  :root {
    /* Material 3 Dark Theme Tokens (Tuned for >= 7:1 WCAG AAA Contrast) */
    --md-sys-color-background: #0b0f14;
    --md-sys-color-surface: #121820;
    --md-sys-color-surface-container: #1a222d;
    --md-sys-color-surface-container-high: #232d3b;
    --md-sys-color-on-surface: #f8fafc;
    --md-sys-color-on-surface-variant: #cbd5e1; /* High contrast muted text */
    --md-sys-color-outline: #475569;
    --md-sys-color-outline-variant: #1e293b;
    
    --md-sys-color-primary: #7dd3fc;
    --md-sys-color-on-primary: #082f49;
    
    /* Semantic Accent Colors (Contrast-first) */
    --color-blue: #60a5fa;
    --color-green: #4ade80;
    --color-red: #f87171;
    --color-yellow: #facc15;

    /* Concentric Border Radius Law: R_inner = max(0, R_outer - padding) */
    --card-radius: 16px;
    --card-padding: 8px;
    --inner-radius: calc(max(0px, var(--card-radius) - var(--card-padding)));
    
    --font-display: 'Inter', 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
    --font-body: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
    --font-mono: 'JetBrains Mono', 'Roboto Mono', 'DejaVu Sans Mono', ui-monospace, monospace;
  }

  * { box-sizing: border-box; margin: 0; padding: 0; }
  
  body {
    background-color: var(--md-sys-color-background);
    color: var(--md-sys-color-on-surface);
    font-family: var(--font-body);
    min-height: 100dvh;
    display: grid;
    grid-template-columns: 460px 1fr;
    gap: 24px;
    padding: 24px;
    overflow: hidden;
  }

  h1, h2, h3, h4 { font-family: var(--font-display); font-weight: 600; }
  code { font-family: var(--font-mono); background: rgba(255,255,255,0.1); padding: 2px 6px; border-radius: 4px; font-size: 0.9em; color: #fff; }
  
  /* --- Sidebar & Stepper --- */
  .sidebar {
    display: flex; flex-direction: column; height: calc(100dvh - 48px);
    background: var(--md-sys-color-surface); border-radius: var(--card-radius); border: 1px solid var(--md-sys-color-outline-variant);
    overflow: hidden; position: relative;
  }
  .title-area { padding: 24px 24px 16px 24px; border-bottom: 1px solid var(--md-sys-color-outline-variant); background: var(--md-sys-color-surface-container); }
  
  /* Eyebrow kicker (Craft UI: max 1 per section, optical dot alignment) */
  .kicker { font-family: var(--font-mono); font-size: 12px; color: var(--md-sys-color-primary); margin-bottom: 8px; letter-spacing: 0.05em; display: flex; align-items: center; gap: 6px; text-transform: uppercase; }
  .kicker::before { content: ''; display: inline-block; width: 6px; height: 6px; background: currentColor; border-radius: 1px; transform: translateY(-0.5px); }
  .title-area h1 { font-size: 24px; color: #fff; letter-spacing: -0.02em; line-height: 1.2; }
  
  .step-body { flex: 1; overflow-y: auto; padding: 24px; display: flex; flex-direction: column; gap: 16px; }
  .step-body::-webkit-scrollbar { width: 6px; }
  .step-body::-webkit-scrollbar-thumb { background: var(--md-sys-color-outline); border-radius: 3px; }

  .body-text { font-size: 15px; color: var(--md-sys-color-on-surface-variant); line-height: 1.6; }
  .body-text strong { color: #fff; font-weight: 500; }

  /* Cards & Boxes (No border-left stripes, zero nested box fatigue) */
  .card { background: var(--md-sys-color-surface-container); border-radius: var(--inner-radius); padding: 16px; display: flex; flex-direction: column; gap: 12px; }
  .section-label { font-family: var(--font-mono); font-size: 11px; text-transform: uppercase; letter-spacing: 0.1em; color: var(--md-sys-color-on-surface-variant); }

  .ascii-card { background: #05070a; border: 1px solid var(--md-sys-color-outline-variant); border-radius: var(--inner-radius); padding: 16px; overflow-x: auto; }
  .ascii-card pre { font-family: var(--font-mono); font-size: 12px; color: var(--md-sys-color-on-surface); line-height: 1.5; }

  .hint-box { background: rgba(125, 211, 252, 0.08); border: 1px solid rgba(125, 211, 252, 0.2); padding: 12px 16px; border-radius: var(--inner-radius); font-size: 13px; color: #e0f2fe; line-height: 1.5; display: flex; gap: 10px; align-items: flex-start; }
  .hint-box .material-symbols-outlined { font-size: 18px; color: var(--md-sys-color-primary); margin-top: 1px; }

  .task-box { background: var(--md-sys-color-surface-container-high); border: 1px solid var(--md-sys-color-outline); padding: 16px; border-radius: var(--inner-radius); display: flex; flex-direction: column; gap: 8px; }
  .task-box h4 { font-size: 14px; color: #fff; display: flex; align-items: center; gap: 8px; }
  .task-box h4 .material-symbols-outlined { font-size: 18px; color: var(--task-color, var(--md-sys-color-primary)); }
  .task-box p { font-size: 14px; color: var(--md-sys-color-on-surface-variant); line-height: 1.5; }

  .ignore-box { background: transparent; border: 1px dashed var(--md-sys-color-outline); padding: 12px 16px; border-radius: var(--inner-radius); font-size: 13px; color: var(--md-sys-color-on-surface-variant); line-height: 1.5; margin-top: auto; }
  .ignore-box strong { color: var(--md-sys-color-on-surface); }

  /* Transport & Pagination */
  .transport { padding: 16px 24px; background: var(--md-sys-color-surface-container); border-top: 1px solid var(--md-sys-color-outline-variant); display: flex; justify-content: space-between; align-items: center; z-index: 10; }
  .step-dots { display: flex; gap: 6px; }
  /* Craft UI: Scoped transitions only, NO transition: all */
  .dot { width: 8px; height: 8px; border-radius: 4px; background: var(--md-sys-color-outline); transition: background-color 300ms ease, width 300ms cubic-bezier(0.16, 1, 0.3, 1); }
  .dot.active { background: var(--md-sys-color-primary); width: 24px; }
  .dot.past { background: var(--md-sys-color-on-surface-variant); }

  /* Craft UI Buttons (Tactile push physics, optical alignment, no multi-line lozenges) */
  .m3-btn {
    font-family: var(--font-display); font-size: 14px; font-weight: 500; height: 40px; padding: 0 16px; border-radius: 9999px; border: none; cursor: pointer; display: inline-flex; align-items: center; justify-content: center; gap: 8px; white-space: nowrap; user-select: none;
    transition: transform 150ms cubic-bezier(0.16, 1, 0.3, 1), background-color 150ms ease, box-shadow 150ms ease, opacity 150ms ease;
    background: var(--md-sys-color-surface-container-high); color: var(--md-sys-color-on-surface); box-shadow: 0 1px 2px rgba(0,0,0,0.2), inset 0 1px 0 rgba(255,255,255,0.05);
  }
  .m3-btn:hover:not(:disabled) { background: #2d3a4b; }
  .m3-btn:active:not(:disabled) { transition-duration: 0ms; transform: translateY(1px) scale(0.985); box-shadow: none; }
  .m3-btn:disabled { opacity: 0.4; cursor: not-allowed; box-shadow: none; }
  .m3-btn .material-symbols-outlined { font-size: 18px; }
  .m3-btn-primary { background: var(--md-sys-color-primary); color: var(--md-sys-color-on-primary); box-shadow: 0 2px 4px rgba(0,0,0,0.3), inset 0 1px 0 rgba(255,255,255,0.2); }
  .m3-btn-primary:hover:not(:disabled) { background: #bae6fd; }

  /* Segmented Tracks (Rectangular radius to prevent wrapping lozenges) */
  .segmented-track { display: flex; background: var(--md-sys-color-background); padding: 4px; border-radius: 10px; border: 1px solid var(--md-sys-color-outline-variant); gap: 4px; transition: opacity 300ms ease; }
  .segmented-track.disabled { opacity: 0.4; pointer-events: none; }
  .seg-btn { flex: 1; height: 32px; border: none; background: transparent; color: var(--md-sys-color-on-surface-variant); font-family: var(--font-display); font-size: 13px; font-weight: 500; border-radius: 6px; cursor: pointer; display: flex; align-items: center; justify-content: center; gap: 6px; white-space: nowrap; transition: transform 150ms cubic-bezier(0.16, 1, 0.3, 1), background-color 150ms ease, color 150ms ease, box-shadow 150ms ease; }
  .seg-btn:active { transition-duration: 0ms; transform: translateY(1px) scale(0.985); }
  .seg-btn.active { background: var(--md-sys-color-surface-container-high); color: #fff; box-shadow: 0 1px 3px rgba(0,0,0,0.3), inset 0 1px 0 rgba(255,255,255,0.05); }
  .seg-btn .material-symbols-outlined { font-size: 16px; }

  /* Interactive Vocabulary Rows (Zero-stroke tonal elevation, radio dot for color) */
  .vocab-list { display: flex; flex-direction: column; gap: 6px; }
  .vocab-row { display: flex; align-items: flex-start; gap: 12px; padding: 12px; border-radius: var(--inner-radius); background: var(--md-sys-color-surface-container); border: 1px solid transparent; cursor: pointer; text-align: left; transition: background-color 150ms ease, transform 150ms ease, border-color 150ms ease; color: var(--md-sys-color-on-surface); width: 100%; font-family: inherit; }
  .vocab-row:hover { background: var(--md-sys-color-surface-container-high); }
  .vocab-row:active { transition-duration: 0ms; transform: translateY(1px) scale(0.99); }
  .vocab-row.active { background: var(--md-sys-color-surface-container-high); border-color: var(--md-sys-color-outline); }
  .v-radio { width: 18px; height: 18px; border-radius: 9px; border: 2px solid var(--md-sys-color-on-surface-variant); margin-top: 2px; flex-shrink: 0; display: flex; align-items: center; justify-content: center; transition: border-color 150ms ease; }
  .vocab-row.active .v-radio { border-color: var(--v-color, var(--md-sys-color-primary)); }
  .vocab-row.active .v-radio::after { content: ''; width: 8px; height: 8px; border-radius: 4px; background: var(--v-color, var(--md-sys-color-primary)); }
  .v-info h4 { font-size: 14px; display: flex; align-items: center; gap: 6px; color: #fff; font-family: var(--font-display); }
  .v-info p { font-size: 13px; color: var(--md-sys-color-on-surface-variant); margin-top: 4px; line-height: 1.4; }
  .v-badge { font-family: var(--font-mono); font-size: 11px; padding: 2px 6px; border-radius: 4px; background: rgba(255,255,255,0.1); color: #fff; }

  /* Sliders */
  .slider-row { display: flex; flex-direction: column; gap: 8px; }
  .slider-header { display: flex; justify-content: space-between; font-size: 13px; font-family: var(--font-display); font-weight: 500; color: var(--md-sys-color-on-surface); }
  .slider-val { font-family: var(--font-mono); color: var(--md-sys-color-primary); }
  input[type=range] { -webkit-appearance: none; width: 100%; background: var(--md-sys-color-background); height: 6px; border-radius: 3px; border: 1px solid var(--md-sys-color-outline-variant); outline: none; }
  input[type=range]::-webkit-slider-thumb { -webkit-appearance: none; width: 16px; height: 16px; border-radius: 8px; background: var(--md-sys-color-primary); cursor: pointer; transition: transform 150ms; }
  input[type=range]::-webkit-slider-thumb:active { transform: scale(1.2); }

  /* --- Main Workspace --- */
  .workspace { display: flex; flex-direction: column; gap: 24px; height: calc(100dvh - 48px); }
  .panel { flex: 1; background: var(--md-sys-color-surface); border-radius: var(--card-radius); border: 1px solid var(--md-sys-color-outline-variant); display: flex; flex-direction: column; overflow: hidden; position: relative; transition: opacity 400ms ease, filter 400ms ease; isolation: isolate; }
  .panel.dimmed { opacity: 0.3; filter: grayscale(1); pointer-events: none; }
  .panel-header { padding: 12px 16px; background: var(--md-sys-color-surface-container); border-bottom: 1px solid var(--md-sys-color-outline-variant); display: flex; justify-content: space-between; align-items: center; z-index: 10; }
  .panel-header h2 { font-size: 15px; display: flex; align-items: center; gap: 8px; color: #fff; }
  .panel-header .material-symbols-outlined { font-size: 18px; color: var(--md-sys-color-primary); }
  
  .viewport { flex: 1; position: relative; background: #05070a; overflow: hidden; display: flex; align-items: center; justify-content: center; }

  .hint-toast { position: absolute; bottom: 16px; left: 50%; transform: translateX(-50%); background: rgba(0,0,0,0.8); backdrop-filter: blur(8px); border: 1px solid var(--md-sys-color-outline); padding: 8px 16px; border-radius: 9999px; font-size: 13px; display: flex; align-items: center; gap: 8px; pointer-events: none; z-index: 20; box-shadow: 0 4px 12px rgba(0,0,0,0.3); color: #fff; white-space: nowrap; transition: opacity 300ms ease; }
  .hint-toast .material-symbols-outlined { font-size: 16px; color: var(--md-sys-color-primary); }

  /* Muted bottom-right version tag (Never a header badge) */
  .version-tag { position: absolute; bottom: 4px; right: 8px; font-size: 10px; color: var(--md-sys-color-outline); font-family: var(--font-mono); pointer-events: none; z-index: 100; }
</style>
</head>
<body>

<div class="sidebar">
  <div class="title-area">
    <div class="kicker" id="stepKicker">01 / 05 · ZOOM OUT</div>
    <h1 id="stepTitle">Title</h1>
  </div>
  <div class="step-body" id="stepBody">
    <!-- Injected by JS -->
  </div>
  <div class="transport">
    <!-- Craft UI: Optical alignment shifts arrows 1.5px along their directional axis -->
    <button class="m3-btn" id="btnPrev" onclick="nav(-1)"><span class="material-symbols-outlined" style="transform:translateX(-1.5px)">arrow_back</span> Back</button>
    <div class="step-dots" id="stepDots"></div>
    <button class="m3-btn m3-btn-primary" id="btnNext" onclick="nav(1)">Next <span class="material-symbols-outlined" style="transform:translateX(1.5px)">arrow_forward</span></button>
  </div>
  <div class="version-tag">v1.0.0</div>
</div>

<div class="workspace">
  <div class="panel" id="mainPanel">
    <div class="panel-header">
      <h2><span class="material-symbols-outlined">science</span> Interactive Workspace</h2>
      <!-- Optional header controls (toggles, segmented tracks) go here -->
    </div>
    <div class="viewport" id="viewport">
      <!-- Canvases, SVGs, D3 graphs, or CSS 3D scenes go here -->
      <div class="hint-toast" id="toast"><span class="material-symbols-outlined">info</span> <span id="toastText">Workspace ready.</span></div>
    </div>
  </div>
</div>

<script>
// --- Workspace State & Logic ---
// Define canvases, D3 scales, or interactive state variables here.

function setVocab(type, btn) {
  document.querySelectorAll('.vocab-row').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  // Trigger visual highlights in the workspace based on `type`
}

// --- Stepper Logic (5-Part Default Spine) ---
const steps = [
  {
    kicker: "01 / 05 · ZOOM OUT", 
    title: "The 10,000-Foot View",
    body: `
      <p class="body-text">Tee up what is being explained directly without meta-scaffolding. Anchor it in a relatable <strong>physical metaphor</strong>.</p>
      <div class="ascii-card"><pre>
[Input] ──► (Physical Verb) ──► [Output]
      </pre></div>
      <div class="hint-box"><span class="material-symbols-outlined">visibility</span> Look at the right panel. It shows the final working state in action.</div>
      <div class="ignore-box"><strong>Safe to ignore right now:</strong> Advanced edge cases, complex math, and specific file names.</div>
    `,
    setup: () => {
      document.getElementById('toastText').textContent = "Observing the final working state.";
      // Lock interactive tools, set workspace to auto-play or show final state
    }
  },
  {
    kicker: "02 / 05 · VOCABULARY", 
    title: "The Tangible Pieces",
    body: `
      <p class="body-text">Click each piece below to see how the abstract code maps to the physical workspace:</p>
      <div class="vocab-list">
        <button class="vocab-row active" style="--v-color: var(--color-blue)" onclick="setVocab('a', this)"><div class="v-radio"></div><div class="v-info"><h4>file_a.js <span class="v-badge">The Sorter</span></h4><p>Acts like a mailroom sorting belt, routing traffic.</p></div></button>
        <button class="vocab-row" style="--v-color: var(--color-green)" onclick="setVocab('b', this)"><div class="v-radio"></div><div class="v-info"><h4>file_b.js <span class="v-badge">The Stamp</span></h4><p>Punches a timestamp onto every passing packet.</p></div></button>
      </div>
    `,
    setup: () => {
      document.getElementById('toastText').textContent = "Click a row to highlight the component.";
      setTimeout(() => document.querySelector('.vocab-row').click(), 50);
    }
  },
  {
    kicker: "03 / 05 · THE PROBLEM", 
    title: "Why the Valve Breaks",
    body: `
      <p class="body-text">Look at the workspace. Without the new logic, the system hits a visceral broken state:</p>
      <div class="card">
        <p class="body-text"><strong style="color:var(--color-red)">Traffic Pileup:</strong> Packets slam into the closed door and drop to the floor.</p>
      </div>
    `,
    setup: () => {
      document.getElementById('toastText').textContent = "Notice the dropped packets piling up.";
      // Force workspace into broken state
    }
  },
  {
    kicker: "04 / 05 · HANDS-ON FIX", 
    title: "Tuning the Valve",
    body: `
      <p class="body-text">Adjusting the threshold commands the valve to snap open before the queue overflows.</p>
      <div class="task-box" style="--task-color: var(--color-green)">
        <h4><span class="material-symbols-outlined">build</span> Try it in the Workspace:</h4>
        <p>Drag the slider to 50. Watch the traffic flow smoothly without dropping.</p>
      </div>
      <div class="card">
        <div class="slider-row">
          <div class="slider-header"><span>Valve Threshold</span><span class="slider-val" id="valThresh">10</span></div>
          <input type="range" min="0" max="100" value="10" oninput="document.getElementById('valThresh').textContent=this.value; /* update workspace */">
        </div>
      </div>
    `,
    setup: () => {
      document.getElementById('toastText').textContent = "Drag the slider to fix the pileup.";
      // Unlock specific tool
    }
  },
  {
    kicker: "05 / 05 · SANDBOX", 
    title: "Free Play & Review",
    body: `
      <p class="body-text">The mental model is complete! Use the controls below to freely toggle views, inject edge cases, or click <strong>Auto-Fix</strong>.</p>
      <div style="display:flex; gap:8px;">
        <button class="m3-btn" style="flex:1" onclick="/* reset */"><span class="material-symbols-outlined">refresh</span> Break It</button>
        <button class="m3-btn m3-btn-primary" style="flex:1" onclick="/* autofix */"><span class="material-symbols-outlined">auto_fix</span> Auto-Fix</button>
      </div>
    `,
    setup: () => {
      document.getElementById('toastText').textContent = "Free play mode active. All controls unlocked.";
      // Unlock all tools
    }
  }
];

let curStep = 0;
function renderStep() {
  const s = steps[curStep];
  document.getElementById('stepKicker').textContent = s.kicker;
  document.getElementById('stepTitle').textContent = s.title;
  document.getElementById('stepBody').innerHTML = s.body;
  
  document.getElementById('btnPrev').disabled = curStep === 0;
  document.getElementById('btnNext').disabled = curStep === steps.length - 1;
  
  let dots = '';
  for(let i=0; i<steps.length; i++) dots += `<div class="dot ${i===curStep?'active':i<curStep?'past':''}"></div>`;
  document.getElementById('stepDots').innerHTML = dots;
  
  s.setup();
}

function nav(dir) {
  curStep = Math.max(0, Math.min(steps.length - 1, curStep + dir));
  renderStep();
}

// Keyboard Navigation (No Auto-Play)
window.addEventListener('keydown', e => {
  if(e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;
  if(e.key === 'ArrowRight') nav(1);
  if(e.key === 'ArrowLeft') nav(-1);
});

// Init
renderStep();
</script>
</body>
</html>
```

## CSS 3D Label Occlusion Gotcha

When building exploded 3D views using `transform-style: preserve-3d` and `rotateX(15deg) rotateY(-35deg)`, the visual stack inverts (foreground shifts top-left, background shifts bottom-right). 
- Place `.layer-label` elements on the `right` side of the canvas to avoid bounding-box occlusion.
- Manually stagger their `top` values and use a CSS variable `--line-w` for the `::after` leader lines so the labels map perfectly to the visual stack without overlapping.
