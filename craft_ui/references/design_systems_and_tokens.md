# Design Systems, Typography & Token Architecture

This reference guides foundation selection, typographic principles, and token
hierarchies based on the incoming design read.

--------------------------------------------------------------------------------

## Foundation Selection Matrix

Do not hand-roll custom CSS for problems already solved by vetted design
systems. When the brief calls for an established design language, use the
official package.

| Brief Archetype       | Recommended Foundation       | Strategic Rationale   |
| :-------------------- | :--------------------------- | :-------------------- |
| Microsoft /           | `@fluentui/react-components` | Native Fluent design  |
: Enterprise            :                              : tokens, verified      :
: Productivity          :                              : accessibility tree    :
| Google Workspace /    | `@material/web`              | Material 3 token      |
: Material Ecosystem    :                              : bindings, themeable   :
:                       :                              : via CSS variables     :
| Industrial /          | `@carbon/react` +            | IBM Carbon system,    |
: Enterprise Analytics  : `@carbon/styles`             : mature data density   :
:                       :                              : patterns              :
| Accessible Modern     | `@radix-ui/themes` or        | Unstyled headless     |
: React Primitives      : `@radix-ui/react-*`          : primitives with full  :
:                       :                              : keyboard navigation   :
| Custom SaaS with      | `shadcn/ui` (`@radix-ui` +   | Full component        |
: Owned Code            : Tailwind)                    : ownership; requires   :
:                       :                              : aggressive            :
:                       :                              : de-slopping of        :
:                       :                              : defaults              :
| Fast Developer        | UnoCSS + Attributify preset  | Instant compilation,  |
: Tooling / Vite Stack  :                              : zero CSS bloat, clean :
:                       :                              : class-based tokens    :
| Modern Bespoke Web    | Tailwind CSS v4 + native CSS | Maximum flexibility   |
: Application           : Grid                         : for asymmetric        :
:                       :                              : layouts and           :
:                       :                              : micro-interactions    :
| Hermetic / Enterprise | `@material/web` + Google     | Material 3 token      |
: Monorepo Stack        : Sans / Roboto                : system; external CDN  :
:                       :                              : display fonts are     :
:                       :                              : inaccessible          :

--------------------------------------------------------------------------------

## Choosing a Look (A Method, Not a Palette)

The failure mode of every anti-slop effort is replacing one default look with
another. The 2024 tell was the purple gradient on a dark hero. The 2026 tell is
a warm cream background with a serif display font and a sage green accent — the
current "AI tried to be tasteful" house style. Prescribing any specific palette
or font pairing is how you become next year's slop.

This section gives you a **method to decide**, not a thing to copy.

### Always Start from a Reference

The highest-leverage input is a real reference. Ask the user for one site,
brand, or screenshot whose feel they want. Anchor color, type, and density to
it. If the user cannot name one, that is the conversation to have before writing
CSS — without a reference, the model picks the median of the training data, and
everyone's median is identical.

A reference is how a human injects taste into a model that otherwise averages.

### If No Reference Exists: Name a Direction

If there is genuinely no reference and the agent must choose, pick a **named
direction** and commit to it, rather than "modern and clean." Named directions
force specificity and steer away from the center:

*   **Dense and Utilitarian** — think trading terminal, cockpit HUD,
    infrastructure console
*   **Editorial and Text-Forward** — think magazine layout, longform
    publication, cultural journal
*   **Warm and Consumer** — think friendly app, playful onboarding, accessible
    retail
*   **Stark and Technical** — think developer tooling, CLI dashboard, monospaced
    telemetry
*   **Expressive and Brand-Loud** — think product launch, cultural showcase,
    breakthrough portfolio

These are vocabulary labels for communicating intent, not prescriptions. Do not
attach specific hex codes, font names, or Tailwind classes to them — that is the
trap this method exists to prevent.

### Color

Decide a primary from the project, not the framework. A real brand color is
best. If choosing from scratch, sample from something concrete — a product
photo, a logo, a physical object, a place — so the palette has a source. Build a
neutral ramp the agent actually picked rather than stock slate or stock cream.

The test: "Is this color here because of something specific about this project,
or because it is what the model defaults to?" If the answer is the latter, pick
again.

### Typography

Avoid defaulting to `Inter` + `Roboto` or `Fraunces` + `Instrument Serif`. The
goal is a type choice that has a reason connected to the project. If the brief
is technical, a monospaced or grotesque display font carries that signal. If the
brief is editorial, a high-contrast serif is appropriate — but only if
"editorial" was a deliberate direction choice, not the model's next-most-likely
guess after purple was banned.

### Environment-Specific Font Constraints

For **hermetic or air-gapped enterprise monorepos** (Angular + Lit + Material
Web Components), external CDN typefaces (Satoshi, Cabinet Grotesk, GT Walsheim,
Space Grotesk) are inaccessible. Default to system or corporate typefaces (e.g.,
Google Sans / Roboto) with Material 3 type scales.

For **public web** projects, verify that chosen typefaces are available via
Google Fonts, Adobe Fonts, or self-hosted WOFF2. Never reference a font the
build system cannot load.

--------------------------------------------------------------------------------

## Typographic Sizing and Tracking Rules

*   **Display Headlines ($36\text{px}+$):** Always tighten tracking
    (`tracking-tight` or `tracking-[-0.03em]`).
*   **Micro-Labels ($10\text{px}-12\text{px}$):** Increase letter spacing
    (`tracking-widest` or `tracking-[0.15em]`) to preserve legibility.
*   **Tabular Data:** Force tabular numbers via CSS `font-variant-numeric:
    tabular-nums` to prevent column jittering when data updates.
