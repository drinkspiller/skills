---
name: design-system-patterns
description: >
  Builds scalable design systems with design tokens, theming infrastructure,
  and component architecture patterns. Use when creating design tokens,
  implementing theme switching, building component libraries, establishing
  design system foundations, or setting up multi-brand theming.
---

# Design System Patterns

Master design system architecture to create consistent, maintainable, and
scalable UI foundations across web and mobile applications.

## When to Use This Skill

- Creating design tokens for colors, typography, spacing, and shadows
- Implementing light/dark theme switching with CSS custom properties
- Building multi-brand theming systems
- Architecting component libraries with consistent APIs
- Establishing design-to-code workflows with Figma tokens
- Creating semantic token hierarchies (primitive, semantic, component)
- Setting up design system documentation and guidelines

## Core Capabilities

### 1. Design Tokens

- Primitive tokens (raw values: colors, sizes, fonts)
- Semantic tokens (contextual meaning: text-primary, surface-elevated)
- Component tokens (specific usage: button-bg, card-border)
- Token naming conventions and organization
- Multi-platform token generation (CSS, iOS, Android)

### 2. Theming Infrastructure

- CSS custom properties architecture
- Theme context providers in React
- Dynamic theme switching
- System preference detection (prefers-color-scheme)
- Persistent theme storage
- Reduced motion and high contrast modes

### 3. Component Architecture

- Compound component patterns
- Polymorphic components (as prop)
- Variant and size systems
- Slot-based composition
- Headless UI patterns
- Style props and responsive variants

## References

For detailed patterns and worked examples, see the `references/` directory:

- `details.md` — Token hierarchy patterns and theme switching examples
- `design-tokens.md` — Deep dive into color, typography, spacing, and shadow
  token structures
- `component-architecture.md` — Compound components, polymorphic components,
  and variant systems
- `theming-architecture.md` — CSS custom properties architecture, React theme
  providers, and multi-brand theming
